"""PPO with an asymmetric actor-critic.

The actor sees only deployable sensors (with history); the critic also sees
privileged simulator state, which it needs only during training.
"""
import torch
import torch.nn as nn


class RunningNorm(nn.Module):
    """Running mean/std observation normalizer, frozen at deployment."""

    def __init__(self, dim, clip=5.0):
        super().__init__()
        self.register_buffer("mean", torch.zeros(dim))
        self.register_buffer("var", torch.ones(dim))
        self.register_buffer("count", torch.tensor(1e-4))
        self.clip = clip

    @torch.no_grad()
    def update(self, x):
        b_mean, b_var, b_count = x.mean(0), x.var(0, unbiased=False), x.shape[0]
        delta = b_mean - self.mean
        total = self.count + b_count
        self.mean += delta * b_count / total
        self.var = (self.var * self.count + b_var * b_count + delta**2 * self.count * b_count / total) / total
        self.count = total

    def forward(self, x):
        return torch.clamp((x - self.mean) / torch.sqrt(self.var + 1e-8), -self.clip, self.clip)


def mlp(inp, out, hidden=(512, 256, 128)):
    layers, d = [], inp
    for h in hidden:
        layers += [nn.Linear(d, h), nn.ELU()]
        d = h
    layers.append(nn.Linear(d, out))
    return nn.Sequential(*layers)


class ActorCritic(nn.Module):
    def __init__(self, obs_dim, priv_dim, act_dim, init_std=1.0):
        super().__init__()
        self.obs_norm = RunningNorm(obs_dim)
        self.priv_norm = RunningNorm(priv_dim)
        self.actor = mlp(obs_dim, act_dim)
        self.critic = mlp(priv_dim, 1)
        self.log_std = nn.Parameter(torch.full((act_dim,), float(init_std)).log())
        nn.init.uniform_(self.actor[-1].weight, -1e-3, 1e-3)
        nn.init.zeros_(self.actor[-1].bias)

    def dist(self, obs):
        mu = self.actor(self.obs_norm(obs))
        return torch.distributions.Normal(mu, self.log_std.exp().expand_as(mu))

    def value(self, priv):
        return self.critic(self.priv_norm(priv)).squeeze(-1)

    def act_deterministic(self, obs):
        return self.actor(self.obs_norm(obs))


class DeployPolicy(nn.Module):
    """Actor + frozen normalizer, for TorchScript export."""

    def __init__(self, ac):
        super().__init__()
        self.norm, self.actor = ac.obs_norm, ac.actor

    def forward(self, obs):
        return torch.clamp(self.actor(self.norm(obs)), -1.0, 1.0)


class PPO:
    def __init__(self, ac, lr=1e-3, epochs=5, minibatches=4, clip=0.2, gamma=0.99, lam=0.95,
                 entropy_coef=0.01, value_coef=1.0, desired_kl=0.01, max_grad_norm=1.0):
        self.ac = ac
        self.opt = torch.optim.Adam(ac.parameters(), lr=lr)
        self.lr = lr
        self.epochs, self.minibatches, self.clip = epochs, minibatches, clip
        self.gamma, self.lam = gamma, lam
        self.entropy_coef, self.value_coef = entropy_coef, value_coef
        self.desired_kl, self.max_grad_norm = desired_kl, max_grad_norm

    def compute_returns(self, rew, done, values, last_value):
        T = rew.shape[0]
        adv = torch.zeros_like(rew)
        gae = torch.zeros_like(last_value)
        for t in reversed(range(T)):
            next_v = last_value if t == T - 1 else values[t + 1]
            not_done = 1.0 - done[t]
            delta = rew[t] + self.gamma * next_v * not_done - values[t]
            gae = delta + self.gamma * self.lam * not_done * gae
            adv[t] = gae
        return adv + values, adv

    def update(self, batch):
        obs, priv, act, old_logp, old_mu, old_std, ret, adv, old_v = batch
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        n = obs.shape[0]
        mb = n // self.minibatches
        stats = {"policy_loss": 0.0, "value_loss": 0.0, "entropy": 0.0, "kl": 0.0}
        count = 0
        for _ in range(self.epochs):
            perm = torch.randperm(n)
            for i in range(self.minibatches):
                idx = perm[i * mb:(i + 1) * mb]
                d = self.ac.dist(obs[idx])
                logp = d.log_prob(act[idx]).sum(-1)
                with torch.no_grad():
                    kl = (torch.log(d.stddev / old_std[idx])
                          + (old_std[idx] ** 2 + (old_mu[idx] - d.mean) ** 2) / (2 * d.stddev**2) - 0.5).sum(-1).mean()
                    if kl > 2 * self.desired_kl:
                        self.lr = max(1e-5, self.lr / 1.5)
                    elif 0 < kl < self.desired_kl / 2:
                        self.lr = min(1e-2, self.lr * 1.5)
                    for g in self.opt.param_groups:
                        g["lr"] = self.lr
                ratio = torch.exp(logp - old_logp[idx])
                a = adv[idx]
                pl = -torch.min(ratio * a, torch.clamp(ratio, 1 - self.clip, 1 + self.clip) * a).mean()
                v = self.ac.value(priv[idx])
                v_clip = old_v[idx] + torch.clamp(v - old_v[idx], -self.clip, self.clip)
                vl = torch.max((v - ret[idx]) ** 2, (v_clip - ret[idx]) ** 2).mean()
                ent = d.entropy().sum(-1).mean()
                loss = pl + self.value_coef * vl - self.entropy_coef * ent
                self.opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.ac.parameters(), self.max_grad_norm)
                self.opt.step()
                stats["policy_loss"] += pl.item(); stats["value_loss"] += vl.item()
                stats["entropy"] += ent.item(); stats["kl"] += kl.item()
                count += 1
        return {k: v / count for k, v in stats.items()}
