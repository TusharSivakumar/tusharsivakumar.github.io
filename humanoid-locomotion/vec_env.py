"""Runs many HumanoidLocoEnv copies across worker processes.

Each worker owns a slice of the environments and steps them in a loop;
environments reset themselves when they fall or time out.
"""
import multiprocessing as mp

import numpy as np


def _worker(remote, seeds, randomize):
    from env import HumanoidLocoEnv

    envs = [HumanoidLocoEnv(seed=s, randomize=randomize) for s in seeds]
    while True:
        cmd, payload = remote.recv()
        if cmd == "reset":
            out = [e.reset() for e in envs]
            remote.send((np.stack([o for o, _ in out]), np.stack([p for _, p in out])))
        elif cmd == "step":
            obs, priv, rew, done, timeout, final_priv, stats = [], [], [], [], [], [], []
            for e, a in zip(envs, payload):
                o, p, r, fell, to, info = e.step(a)
                final_priv.append(p)
                stats.append(_stats(info))
                if fell or to:
                    o, p = e.reset()
                obs.append(o); priv.append(p); rew.append(r); done.append(fell or to); timeout.append(to and not fell)
            remote.send((np.stack(obs), np.stack(priv), np.array(rew, np.float32), np.array(done),
                         np.array(timeout), np.stack(final_priv), np.stack(stats)))
        elif cmd == "set":
            for e in envs:
                for k, v in payload.items():
                    setattr(e, k, v)
            remote.send(None)
        elif cmd == "close":
            remote.close()
            return


STAT_KEYS = ["lin_vel_tracking", "yaw_rate_tracking", "vel_error", "fell"]


def _stats(info):
    t = info["terms"]
    err = np.linalg.norm(info["cmd"][:2] - info["v"][:2])
    return np.array([t["lin_vel_tracking"], t["yaw_rate_tracking"], err, float(info["fell"])], np.float32)


class VecEnv:
    def __init__(self, num_envs, num_workers, seed=0, randomize=True):
        ctx = mp.get_context("spawn")
        per = np.array_split(np.arange(num_envs) + seed * 100_000, num_workers)
        self.slices = [len(p) for p in per]
        self.remotes, self.procs = [], []
        for seeds in per:
            parent, child = ctx.Pipe()
            proc = ctx.Process(target=_worker, args=(child, list(seeds), randomize), daemon=True)
            proc.start()
            child.close()
            self.remotes.append(parent)
            self.procs.append(proc)
        self.num_envs = num_envs

    def reset(self):
        for r in self.remotes:
            r.send(("reset", None))
        out = [r.recv() for r in self.remotes]
        return np.concatenate([o for o, _ in out]), np.concatenate([p for _, p in out])

    def step(self, actions):
        i = 0
        for r, n in zip(self.remotes, self.slices):
            r.send(("step", actions[i:i + n]))
            i += n
        out = [r.recv() for r in self.remotes]
        return tuple(np.concatenate([o[k] for o in out]) for k in range(7))

    def set_attr(self, **kwargs):
        for r in self.remotes:
            r.send(("set", kwargs))
        for r in self.remotes:
            r.recv()

    def close(self):
        for r in self.remotes:
            r.send(("close", None))
        for p in self.procs:
            p.join(timeout=5)
