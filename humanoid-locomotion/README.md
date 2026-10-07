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
- **Control:** action → leg joint offset (×0.25 rad) from the `knees_bent` pose, tracked by the model's
  PD position actuators (Kp 75 hips/knees, 20 ankles; torque limits 50–139 Nm) at 250 Hz; policy at 50 Hz.
- **Actor observation (47 × 3 frames):** pelvis gyro, projected gravity, command, leg joint
  positions/velocities, previous action, gait phase — with sensor noise.
- **Critic observation:** clean frame + base linear velocity, height, friction, added mass, foot contacts.
- **Reward:** the weighted terms from the doc's reward table (+ a small hip roll/yaw pose term),
  each × the 0.02 s control step.
- **Curriculum:** each time linear-velocity tracking passes 80 % of its maximum, the command range widens,
  domain randomization strengthens toward the doc's ranges (friction 0.2–1.5, mass −1 to +5 kg,
  motor strength ±20 %, 0–20 ms latency), and from level 2 random pushes switch on (0.5 → 1.0 m/s).
- **PPO:** 256 envs × 24 steps, 5 epochs × 4 mini-batches, lr 1e-3 adaptive on KL 0.01, γ 0.99, λ 0.95,
  clip 0.2, initial action std 0.5, entropy 0.003 → 0.001.

## What differs from the doc

- Initial action std 0.5 (doc 1.0) and entropy 0.003 (doc 0.01): with the doc's values exploration noise
  grew during training instead of shrinking.
- PD gains are the G1 model's own (Kp 75 / 20), not the doc's 100–200 example.
- Flat ground only; the doc's terrain curriculum and teacher-student distillation are not implemented
  (the critic's privileged inputs play the teacher's role).
- 256 CPU environments instead of 4096 GPU ones, so far fewer samples than a GPU run.
