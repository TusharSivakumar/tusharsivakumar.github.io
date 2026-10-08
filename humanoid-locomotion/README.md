# Humanoid locomotion policy (Unitree G1, PPO, MuJoCo)

Training code for the locomotion policy described in the
"Control Policies for an Autonomous Humanoid Robot" doc: a velocity-command
walking policy for the Unitree G1 humanoid, trained with PPO on CPU.

| File | What it does |
| --- | --- |
| `env.py` | G1 environment: 12 leg joint targets at 50 Hz, observations, rewards, domain randomization, pushes |
| `vec_env.py` | Runs many environments across worker processes |
| `ppo.py` | Asymmetric actor-critic (actor: sensors + history; critic: privileged state) and PPO with adaptive learning rate |
| `train.py` | Training loop, command / push / randomization curriculum, logging, checkpoints, TorchScript export |
| `evaluate.py` | Metrics (tracking error, survival, push recovery, cost of transport, smoothness), training curves, video |

## Run

```bash
pip install -r requirements.txt
git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git   # G1 model (or set G1_SCENE)
python train.py --num-envs 256 --workers 4 --max-minutes 150                    # -> logs/locomotion/
MUJOCO_GL=egl python evaluate.py --checkpoint logs/locomotion/model_final.pt    # -> results/
```

## Setup at a glance

- **Robot:** MuJoCo Menagerie `unitree_g1/scene_mjx.xml` (29 joints, 33 kg, simplified colliders).
  The policy drives the 12 leg joints; waist and arms hold the `knees_bent` pose. Visual meshes are
  stripped for training (physics unchanged), which cuts memory from ~200 MB to ~10 MB per environment.
- **Control:** leg joint target = `knees_bent` pose + reference gait + 0.25 rad × action, tracked by the
  model's PD position actuators (Kp 75 hips/knees, 20 ankles; torque limits 50–139 Nm) at 250 Hz; policy at 50 Hz.
- **Reference gait:** a 0.8 s gait clock flexes the swing leg's hip (−0.25 rad), knee (+0.5) and ankle (−0.25),
  so the feet lift from the first iteration; the policy learns a residual that balances and steers it.
- **Actor observation (47 × 3 frames):** pelvis gyro, projected gravity, command, leg joint
  positions/velocities, previous action, gait phase — with sensor noise.
- **Critic observation:** clean frame + base linear velocity, height, friction, added mass, foot contacts.
- **Reward:** the terms from the doc's reward table, each × the 0.02 s control step, with these changes:
  linear-velocity tracking 2.0 (doc 1.0), gait-phase contact 1.0 (doc 0.2), air time `min(t, 0.5) − 0.25`
  (doc `t − 0.4`), plus a swing-foot height term (−20 × (z − 0.08 m)²) and a hip roll/yaw pose term (−0.5).
- **Curriculum:** each time linear-velocity tracking passes 70 % of its maximum, the command range widens,
  domain randomization strengthens toward the doc's ranges (friction 0.2–1.5, mass −1 to +5 kg,
  motor strength ±20 %, 0–20 ms latency), and from level 2 random pushes switch on (0.5 → 1.0 m/s).
- **PPO:** 256 envs × 24 steps, 5 epochs × 4 mini-batches, lr 1e-3 adaptive on KL 0.01, γ 0.99, λ 0.95,
  clip 0.2, initial action std 0.5, entropy 0.003 → 0.001.

## What differs from the doc, and why

Training ran on 4 CPU cores (~4,000 steps/s), so the run sees ~20–25 M steps instead of the hundreds of
millions a 4096-env GPU run gets. Several changes were needed to get walking at that budget:

1. **Robot.** Gymnasium's 17-joint humanoid has no ankles and falls in ~1.2 s even with perfect PD hold;
   after 2.4 M steps it still fell within 2 s. Switched to the Unitree G1, which has ankles.
2. **Exploration noise.** Initial action std 0.5 (doc 1.0) and entropy 0.003 (doc 0.01): with the doc's
   values the noise grew instead of shrinking.
3. **Standing-still optimum.** With the doc's reward weights the G1 learned to balance (100 % survival)
   but never lifted a foot: 20 M steps, forward speed 0.0 m/s under a 1.0 m/s command. Re-weighting the
   stepping terms and adding the swing-height term alone did not fix it (feet still never left the ground
   after 5 M steps). Adding the reference gait did: feet lift 9–13 cm and the robot moves forward within 3 M steps.
4. **Curriculum threshold** 0.7 (doc 0.8): the standing-still policy plateaued at 0.73 and never advanced.
5. PD gains are the G1 model's own (Kp 75 / 20), not the doc's 100–200 example.
6. Flat ground only; the doc's terrain curriculum and teacher-student distillation are not implemented
   (the critic's privileged inputs play the teacher's role).
