"""Evaluate a trained locomotion policy in simulation.

  python evaluate.py --checkpoint logs/locomotion/model_final.pt

Measures the metrics from the doc's "Evaluation and deployment" table,
plots the training curves and renders a video of the policy.
"""
import argparse
import json
import os

os.environ.setdefault("MUJOCO_GL", "egl")

import numpy as np
import torch

from env import CTRL_DT, HumanoidLocoEnv
from ppo import ActorCritic


def load_policy(path):
    probe = HumanoidLocoEnv()
    ac = ActorCritic(probe.obs_dim, probe.priv_dim, probe.act_dim)
    ckpt = torch.load(path, weights_only=False)
    ac.load_state_dict(ckpt["model"])
    ac.eval()

    @torch.no_grad()
    def policy(obs):
        return torch.clamp(ac.act_deterministic(torch.as_tensor(np.asarray(obs), dtype=torch.float32)), -1, 1).numpy()

    return policy, ckpt


def run_batch(policy, n, seconds, randomize, setup, on_step=None, seed=1000):
    """Run n envs in lockstep. setup(i, env) sets commands; on_step(t, envs) can push."""
    envs = [HumanoidLocoEnv(seed=seed + i, randomize=randomize) for i in range(n)]
    for e in envs:
        e.push_vel = 0.0
    obs = np.stack([e.reset()[0] for e in envs])
    for i, e in enumerate(envs):
        setup(i, e)
    alive = np.ones(n, dtype=bool)
    rec = {"v": [], "yaw": [], "cmd": [], "act": [], "power": [], "alive": []}
    for t in range(int(seconds / CTRL_DT)):
        if on_step:
            on_step(t, envs)
        act = policy(obs)
        for i, e in enumerate(envs):
            if not alive[i]:
                continue
            o, _, _, fell, _, info = e.step(act[i])
            obs[i] = o
            if fell:
                alive[i] = False
        rec["v"].append([e._base_quantities()[2] for e in envs])
        rec["yaw"].append([e.data.qvel[5] for e in envs])
        rec["cmd"].append([e.cmd.copy() for e in envs])
        rec["act"].append(act.copy())
        rec["power"].append([np.sum(np.abs(e.data.actuator_force[:e.nu] * e.data.qvel[e.vadr])) for e in envs])
        rec["alive"].append(alive.copy())
    return {k: np.array(v) for k, v in rec.items()}, envs


def tracking_error(policy):
    """Mean |v_cmd - v| over steady-state walking for a grid of commands (nominal robot)."""
    cmds = [(0.0, 0, 0), (0.5, 0, 0), (1.0, 0, 0), (1.5, 0, 0), (-0.5, 0, 0),
            (0, 0.3, 0), (0, -0.3, 0), (0.5, 0, 0.5), (0.5, 0, -0.5), (0, 0, 0.8)]
    reps = 4
    rec, _ = run_batch(policy, len(cmds) * reps, 10.0, False,
                       lambda i, e: e.set_command(cmds[i // reps]))
    s = int(2.0 / CTRL_DT)  # skip the first 2 s (acceleration)
    rows = []
    for c_i, c in enumerate(cmds):
        idx = slice(c_i * reps, (c_i + 1) * reps)
        ok = rec["alive"][-1, idx]
        v = rec["v"][s:, idx]
        lin_err = np.linalg.norm(v[..., :2] - np.array(c[:2]), axis=-1).mean()
        yaw_err = np.abs(rec["yaw"][s:, idx] - c[2]).mean()
        rows.append({"vx": c[0], "vy": c[1], "yaw": c[2], "lin_err": float(lin_err), "yaw_err": float(yaw_err),
                     "mean_vx": float(v[..., 0].mean()), "survived": float(ok.mean())})
    alive_mask = rec["alive"][s:]
    v_err = np.linalg.norm(rec["v"][s:, :, :2] - rec["cmd"][s:, :, :2], axis=-1)
    return float(v_err[alive_mask].mean()), rows


def survival(policy, n=64, randomize=True, push=0.0):
    """Fraction of 20 s episodes without a fall, random commands, randomized dynamics."""
    def on_step(t, envs):
        if push > 0 and t > 0 and t % int(6.0 / CTRL_DT) == 0:
            for e in envs:
                e.data.qvel[0:2] += e.rng.uniform(-push, push, 2); e._bq = None
    rec, _ = run_batch(policy, n, 20.0, randomize, lambda i, e: None, on_step=on_step, seed=5000)
    return float(rec["alive"][-1].mean())


def push_recovery(policy, magnitudes=(0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0), n=24):
    """Survival after a single sideways push while walking at 0.5 m/s."""
    out = []
    for mag in magnitudes:
        def setup(i, e):
            e.set_command((0.5, 0.0, 0.0))

        def on_step(t, envs, mag=mag):
            if t == int(3.0 / CTRL_DT):
                for i, e in enumerate(envs):
                    R = e._rot()
                    lateral = R[:2, 1] / np.linalg.norm(R[:2, 1])
                    e.data.qvel[0:2] += (1 if i % 2 else -1) * mag * lateral; e._bq = None
        rec, _ = run_batch(policy, n, 6.0, False, setup, on_step=on_step, seed=9000)
        out.append({"push_mps": mag, "survived": float(rec["alive"][-1].mean())})
    return out


def efficiency(policy):
    """Cost of transport and action smoothness walking at 1.0 m/s (nominal robot)."""
    rec, envs = run_batch(policy, 8, 10.0, False, lambda i, e: e.set_command((1.0, 0, 0)))
    s = int(2.0 / CTRL_DT)
    mass = envs[0].model.body_mass.sum()
    alive = rec["alive"][s:]
    if not alive.any():
        return float("nan"), float("nan"), 0.0
    speed = np.abs(rec["v"][s:, :, 0])[alive].mean()
    cot = rec["power"][s:][alive].mean() / (mass * 9.81 * max(speed, 1e-3))
    both = alive[1:] & alive[:-1]
    smooth = np.linalg.norm(np.diff(rec["act"][s:], axis=0), axis=-1)[both].mean()
    return float(cot), float(smooth), float(speed)


def render_video(policy, path, seconds=16.0, width=640, height=384):
    """Scripted run: walk, speed up, sidestep, turn, get pushed, stand."""
    import imageio
    import mujoco

    env = HumanoidLocoEnv(seed=7, randomize=False, visual=True)
    env.push_vel = 0.0
    obs, _ = env.reset()
    schedule = [(0, (0.5, 0, 0), "walk 0.5 m/s"), (3, (1.2, 0, 0), "walk 1.2 m/s"),
                (6, (0, 0.4, 0), "sidestep left"), (8.5, (0.6, 0, 0.6), "walk + turn"),
                (12, (0.5, 0, 0), "push 1.0 m/s"), (14, (0, 0, 0), "stand")]
    renderer = mujoco.Renderer(env.model, height, width)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
    cam.trackbodyid = env.torso
    cam.distance, cam.elevation, cam.azimuth = 2.6, -12.0, 135.0
    frames, label, k = [], "", 0
    for t in range(int(seconds / CTRL_DT)):
        now = t * CTRL_DT
        while k < len(schedule) and now >= schedule[k][0]:
            env.set_command(schedule[k][1]); label = schedule[k][2]; k += 1
            if label.startswith("push"):
                R = env._rot()
                env.data.qvel[0:2] += 1.0 * R[:2, 1] / np.linalg.norm(R[:2, 1]); env._bq = None
        obs, _, _, fell, _, _ = env.step(policy(obs[None])[0])
        if t % 2 == 0:  # 25 fps
            renderer.update_scene(env.data, cam)
            frames.append(_caption(renderer.render(), f"{label}   t={now:4.1f}s"))
        if fell:
            label = "FELL"
    imageio.mimsave(path, frames, fps=25, quality=7)
    return path


def _caption(img, text):
    from PIL import Image, ImageDraw
    im = Image.fromarray(img)
    ImageDraw.Draw(im).rectangle([0, 0, 260, 22], fill=(0, 0, 0))
    ImageDraw.Draw(im).text((6, 5), text, fill=(255, 255, 255))
    return np.asarray(im)


def plot_curves(csv_path, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    df = pd.read_csv(csv_path)
    x = df["env_steps"] / 1e6
    fig, ax = plt.subplots(2, 2, figsize=(10, 6.5))
    sm = lambda s: s.rolling(20, min_periods=1).mean()
    ax[0, 0].plot(x, sm(df["episode_return"])); ax[0, 0].set_title("Episode return")
    ax[0, 1].plot(x, sm(df["episode_length_s"])); ax[0, 1].set_title("Episode length (s, max 20)")
    ax[1, 0].plot(x, sm(df["vel_error_mps"])); ax[1, 0].set_title("Velocity tracking error (m/s)")
    ax[1, 1].plot(x, df["vx_max"], label="max commanded vx (m/s)")
    ax[1, 1].plot(x, df["push_mps"], label="push strength (m/s)"); ax[1, 1].legend(); ax[1, 1].set_title("Curriculum")
    for a in ax.flat:
        a.set_xlabel("environment steps (millions)"); a.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(out_png, dpi=120)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="logs/locomotion/model_final.pt")
    ap.add_argument("--out", default="results")
    ap.add_argument("--no-video", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    policy, ckpt = load_policy(args.checkpoint)

    err, per_cmd = tracking_error(policy)
    print(f"velocity tracking error: {err:.3f} m/s")
    surv_flat = survival(policy, randomize=False)
    surv_rand = survival(policy, randomize=True, push=0.5)
    print(f"survival nominal {surv_flat:.1%}, randomized + pushes {surv_rand:.1%}")
    pushes = push_recovery(policy)
    max_push = max([p["push_mps"] for p in pushes if p["survived"] >= 0.9], default=0.0)
    print("push recovery", pushes)
    cot, smooth, speed = efficiency(policy)
    print(f"cost of transport {cot:.2f} at {speed:.2f} m/s, action smoothness {smooth:.3f}")

    metrics = {
        "velocity_tracking_error_mps": err,
        "survival_nominal": surv_flat,
        "survival_randomized_with_pushes": surv_rand,
        "max_push_survived_90pct_mps": max_push,
        "cost_of_transport": cot,
        "speed_for_cot_mps": speed,
        "action_smoothness": smooth,
        "per_command": per_cmd,
        "push_sweep": pushes,
        "curriculum_level": ckpt.get("level"),
        "final_cmd_ranges": ckpt.get("cmd_ranges"),
    }
    with open(os.path.join(args.out, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    csv_path = os.path.join(os.path.dirname(args.checkpoint), "progress.csv")
    if os.path.exists(csv_path):
        plot_curves(csv_path, os.path.join(args.out, "training_curves.png"))
    if not args.no_video:
        print("video:", render_video(policy, os.path.join(args.out, "rollout.mp4")))


if __name__ == "__main__":
    main()
