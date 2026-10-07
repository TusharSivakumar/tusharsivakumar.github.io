"""Train the humanoid locomotion policy with PPO.

  python train.py --iterations 3000 --num-envs 256 --workers 4

Writes logs/<run>/progress.csv, periodic checkpoints and a TorchScript
policy (policy.pt) for deployment.
"""
import argparse
import csv
import json
import os
import time
import warnings

import numpy as np
import torch

from env import HumanoidLocoEnv
from ppo import PPO, ActorCritic, DeployPolicy
from vec_env import STAT_KEYS, VecEnv

# Command curriculum (doc "Training setup"): start small, widen when tracking is good.
CMD_START = np.array([[-0.3, 0.6], [-0.2, 0.2], [-0.3, 0.3]])
CMD_MAX = np.array([[-0.5, 1.5], [-0.5, 0.5], [-1.0, 1.0]])
CMD_STEP = np.array([[-0.1, 0.15], [-0.05, 0.05], [-0.1, 0.1]])
TRACKING_THRESHOLD = 0.8   # fraction of max linear-velocity tracking reward
PUSH_START_LEVEL = 2       # pushes switch on at this curriculum level
PUSH_MAX = 1.0             # m/s
DR_START, DR_PER_LEVEL = 0.25, 0.25   # domain-randomization strength: 0.25 -> 1.0 by level 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=3000)
    ap.add_argument("--num-envs", type=int, default=256)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--steps-per-env", type=int, default=24)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--run", default="locomotion")
    ap.add_argument("--save-every", type=int, default=100)
    ap.add_argument("--max-minutes", type=float, default=0, help="stop early after this wall time (0 = off)")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.set_num_threads(4)
    out = os.path.join("logs", args.run)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "config.json"), "w") as f:
        json.dump(vars(args), f, indent=2)

    probe = HumanoidLocoEnv()
    obs_dim, priv_dim, act_dim = probe.obs_dim, probe.priv_dim, probe.act_dim
    venv = VecEnv(args.num_envs, args.workers, seed=args.seed)
    ac = ActorCritic(obs_dim, priv_dim, act_dim, init_std=0.5)
    ppo = PPO(ac, entropy_coef=0.003)

    cmd_ranges, level, push_vel = CMD_START.copy(), 0, 0.0
    venv.set_attr(cmd_ranges=cmd_ranges, push_vel=push_vel, dr_scale=DR_START)
    obs, priv = venv.reset()
    obs, priv = torch.from_numpy(obs), torch.from_numpy(priv)

    N, T = args.num_envs, args.steps_per_env
    ep_ret, ep_len = np.zeros(N), np.zeros(N)
    done_returns, done_lengths = [], []
    log_f = open(os.path.join(out, "progress.csv"), "w", newline="")
    writer = None
    start = time.time()
    total_steps = 0

    for it in range(1, args.iterations + 1):
        # Entropy coefficient 0.003 -> 0.001 over training (doc: "lower late")
        ppo.entropy_coef = 0.003 + (0.001 - 0.003) * min(1.0, it / (0.7 * args.iterations))
        buf = {k: [] for k in ["obs", "priv", "act", "logp", "mu", "std", "rew", "done", "val"]}
        stat_sum = np.zeros(len(STAT_KEYS))
        t0 = time.time()
        for _ in range(T):
            with torch.no_grad():
                ac.obs_norm.update(obs)
                ac.priv_norm.update(priv)
                d = ac.dist(obs)
                act = d.sample()
                logp = d.log_prob(act).sum(-1)
                val = ac.value(priv)
            o, p, r, done, timeout, final_priv, stats = venv.step(act.numpy())
            r = torch.from_numpy(r)
            if timeout.any():  # bootstrap time-outs: the episode was cut, not ended
                with torch.no_grad():
                    r[timeout] += ppo.gamma * ac.value(torch.from_numpy(final_priv[timeout]))
            for k, v in zip(buf, [obs, priv, act, logp, d.mean, d.stddev, r, torch.from_numpy(done).float(), val]):
                buf[k].append(v)
            ep_ret += r.numpy(); ep_len += 1
            for i in np.nonzero(done)[0]:
                done_returns.append(ep_ret[i]); done_lengths.append(ep_len[i])
                ep_ret[i] = ep_len[i] = 0
            stat_sum += stats.mean(0)
            obs, priv = torch.from_numpy(o), torch.from_numpy(p)
        collect_s = time.time() - t0
        total_steps += N * T

        with torch.no_grad():
            last_v = ac.value(priv)
        B = {k: torch.stack(v) for k, v in buf.items()}
        ret, adv = ppo.compute_returns(B["rew"], B["done"], B["val"], last_v)
        flat = lambda x: x.reshape(N * T, *x.shape[2:])
        batch = [flat(B[k]) for k in ["obs", "priv", "act", "logp", "mu", "std"]] + [flat(ret), flat(adv), flat(B["val"])]
        t1 = time.time()
        upd = ppo.update(batch)
        learn_s = time.time() - t1

        # Curriculum
        stats_mean = stat_sum / T
        tracking = stats_mean[0]
        if tracking > TRACKING_THRESHOLD and level < 12:
            level += 1
            cmd_ranges = np.clip(cmd_ranges + CMD_STEP, CMD_MAX[:, :1], CMD_MAX[:, 1:])
            if level >= PUSH_START_LEVEL:
                push_vel = min(PUSH_MAX, 0.5 + 0.1 * (level - PUSH_START_LEVEL))
            venv.set_attr(cmd_ranges=cmd_ranges, push_vel=push_vel,
                          dr_scale=min(1.0, DR_START + DR_PER_LEVEL * level))

        recent_r = np.mean(done_returns[-100:]) if done_returns else 0.0
        recent_l = np.mean(done_lengths[-100:]) if done_lengths else 0.0
        row = {
            "iteration": it, "env_steps": total_steps, "minutes": (time.time() - start) / 60,
            "episode_return": recent_r, "episode_length_s": recent_l * 0.02,
            "lin_vel_tracking": tracking, "yaw_rate_tracking": stats_mean[1],
            "vel_error_mps": stats_mean[2], "falls_per_1k_steps": stats_mean[3] * 1000,
            "curriculum_level": level, "dr_scale": min(1.0, DR_START + DR_PER_LEVEL * level), "vx_max": cmd_ranges[0, 1], "push_mps": push_vel,
            "action_std": ac.log_std.exp().mean().item(), "lr": ppo.lr,
            "steps_per_s": N * T / (collect_s + learn_s), **upd,
        }
        if writer is None:
            writer = csv.DictWriter(log_f, fieldnames=list(row))
            writer.writeheader()
        writer.writerow(row)
        log_f.flush()
        if it % 10 == 0 or it == 1:
            print(f"it {it:5d} | steps {total_steps/1e6:6.2f}M | ret {recent_r:7.2f} | len {recent_l*0.02:5.1f}s "
                  f"| track {tracking:.2f} | verr {stats_mean[2]:.2f} | lvl {level} | push {push_vel:.1f} "
                  f"| std {row['action_std']:.2f} | {row['steps_per_s']:.0f} sps", flush=True)
        if it % args.save_every == 0:
            save(ac, out, f"model_{it}.pt", level, cmd_ranges, push_vel)
        if args.max_minutes and (time.time() - start) / 60 > args.max_minutes:
            print("time budget reached", flush=True)
            break

    save(ac, out, "model_final.pt", level, cmd_ranges, push_vel)
    warnings.filterwarnings("ignore", category=FutureWarning)
    scripted = torch.jit.trace(DeployPolicy(ac).eval(), torch.zeros(1, obs_dim))
    scripted.save(os.path.join(out, "policy.pt"))
    venv.close()
    print("done", out)


def save(ac, out, name, level, cmd_ranges, push_vel):
    torch.save({"model": ac.state_dict(), "level": level, "cmd_ranges": cmd_ranges.tolist(),
                "push_vel": push_vel}, os.path.join(out, name))


if __name__ == "__main__":
    main()
