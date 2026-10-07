"""Velocity-command locomotion environment for the Unitree G1 humanoid in MuJoCo.

The robot model is MuJoCo Menagerie's `unitree_g1/scene_mjx.xml` (29 joints,
simplified colliders). The policy controls the 12 leg joints: it outputs joint
position offsets at 50 Hz, and the model's PD position actuators (250 Hz
physics, torque-limited) track them. Waist and arms hold their default pose.

Observations follow the policy spec in the doc:
  actor  : pelvis gyro, projected gravity, command, leg joint pos/vel, previous
           action, gait phase (47 numbers) -- with sensor noise, stacked over
           HISTORY frames
  critic : the clean actor frame + privileged terms (base linear velocity,
           base height, friction, added mass, foot contacts)
"""
import copy
import os

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get(
    "G1_SCENE", os.path.join(HERE, "mujoco_menagerie", "unitree_g1", "scene_mjx.xml"))

SIM_DT = 0.004          # physics step, s (model default)
DECIMATION = 5          # physics steps per policy step -> 50 Hz policy
CTRL_DT = SIM_DT * DECIMATION
EPISODE_S = 20.0
MAX_STEPS = int(EPISODE_S / CTRL_DT)
HISTORY = 3
ACTION_SCALE = 0.25     # rad per unit action
GAIT_PERIOD = 0.8       # s, one full left + right stride
NUM_LEG = 12            # first 12 actuators are the legs

# Reward weights (doc "Reward design" table, plus a small pose term for the
# hip roll/yaw joints); every term is multiplied by CTRL_DT.
REWARD_WEIGHTS = {
    "lin_vel_tracking": 1.0,
    "yaw_rate_tracking": 0.5,
    "feet_air_time": 1.0,
    "gait_phase_contact": 0.2,
    "base_height": -10.0,
    "orientation": -1.0,
    "vertical_velocity": -2.0,
    "torques": -1e-5,
    "joint_acc": -2.5e-7,
    "action_rate": -0.01,
    "joint_limits": -10.0,
    "foot_slip": -0.1,
    "body_contact": -1.0,
    "hip_pose": -0.5,
    "termination": -200.0,
}


_PHYSICS_MODEL = None


def load_model(visual=False):
    """The G1 scene. Without visuals, mesh geoms are stripped (about 200 MB -> 10 MB per
    copy); collision shapes and inertias are explicit in the file, so physics is unchanged."""
    global _PHYSICS_MODEL
    if visual:
        return mujoco.MjModel.from_xml_path(MODEL_PATH)
    if _PHYSICS_MODEL is None:
        spec = mujoco.MjSpec.from_file(MODEL_PATH)
        for g in list(spec.geoms):
            if g.type == mujoco.mjtGeom.mjGEOM_MESH:
                spec.delete(g)
        for mesh in list(spec.meshes):
            spec.delete(mesh)
        _PHYSICS_MODEL = spec.compile()
    return copy.deepcopy(_PHYSICS_MODEL)


class HumanoidLocoEnv:
    """Single G1 environment with domain randomization, pushes and command resampling."""

    def __init__(self, seed=0, randomize=True, visual=False):
        self.rng = np.random.default_rng(seed)
        self.randomize = randomize
        self.model = load_model(visual)
        self.model.opt.timestep = SIM_DT
        self.data = mujoco.MjData(self.model)
        m = self.model

        self.nu = NUM_LEG
        jids = m.actuator_trnid[:, 0]
        self.qadr = m.jnt_qposadr[jids][:NUM_LEG]
        self.vadr = m.jnt_dofadr[jids][:NUM_LEG]
        self.joint_names = [m.joint(j).name for j in jids[:NUM_LEG]]
        key = m.key("knees_bent").id
        self.key_qpos = m.key_qpos[key].copy()
        self.ctrl_default = m.key_ctrl[key].copy()           # all 29 actuators
        self.q_default = self.ctrl_default[:NUM_LEG].copy()
        self.base_gain = m.actuator_gainprm[:, 0].copy()
        self.base_bias = m.actuator_biasprm[:, :3].copy()
        lo, hi = m.jnt_range[jids[:NUM_LEG], 0], m.jnt_range[jids[:NUM_LEG], 1]
        mid, half = (lo + hi) / 2, (hi - lo) / 2
        self.soft_lo, self.soft_hi = mid - 0.9 * half, mid + 0.9 * half
        self.hip_ry = np.array([i for i, n in enumerate(self.joint_names) if "hip_roll" in n or "hip_yaw" in n])

        self.pelvis = m.body("pelvis").id
        self.torso = m.body("torso_link").id
        self.floor = m.geom("floor").id
        self.foot_geoms = [
            {m.geom(f"left_foot{i}_collision").id for i in (1, 2, 3)},
            {m.geom(f"right_foot{i}_collision").id for i in (1, 2, 3)},
        ]
        self.foot_sites = np.array([m.site("left_foot").id, m.site("right_foot").id])
        self.gyro_adr = m.sensor_adr[m.sensor("gyro_pelvis").id]
        feet = self.foot_geoms[0] | self.foot_geoms[1]
        self.foot_pairs = np.array([p for p in range(m.npair)
                                    if m.pair_geom1[p] in feet or m.pair_geom2[p] in feet])
        self.base_pair_friction = m.pair_friction[:, :2].copy()
        self.base_torso_mass = m.body_mass[self.torso]

        # Curriculum-controlled settings (set by the trainer).
        self.cmd_ranges = np.array([[-0.3, 0.6], [-0.2, 0.2], [-0.3, 0.3]])
        self.push_vel = 0.0
        self.dr_scale = 1.0
        self._bq = None

        self.base_height_target = 0.75
        self.actor_frame_dim = 6 + 3 + 3 * self.nu + 2
        self.obs_dim = self.actor_frame_dim * HISTORY
        self.priv_dim = self.actor_frame_dim + 3 + 1 + 1 + 1 + 2
        self.act_dim = self.nu

    # ------------------------------------------------------------------ reset
    def reset(self):
        m, d = self.model, self.data
        mujoco.mj_resetData(m, d)
        d.qpos[:] = self.key_qpos
        d.qpos[self.qadr] += self.rng.uniform(-0.05, 0.05, self.nu)
        d.qvel[:] = self.rng.uniform(-0.1, 0.1, m.nv)
        d.ctrl[:] = self.ctrl_default

        if self.randomize:
            # Ranges from the doc; dr_scale (0..1, set by the curriculum) widens them
            # from the nominal value to the full range.
            k = self.dr_scale
            self.friction = self.rng.uniform(1.0 - 0.8 * k, 1.0 + 0.5 * k)               # 0.2 - 1.5
            self.added_mass = self.rng.uniform(-1.0 * k, 5.0 * k)                       # -1 to +5 kg
            self.motor_strength = self.rng.uniform(1 - 0.2 * k, 1 + 0.2 * k, m.nu)      # 0.8 - 1.2
            self.delay = int(self.rng.random() < 0.5 * k)  # 0 or 1 policy step (0 or 20 ms)
        else:
            self.friction, self.added_mass, self.delay = 1.0, 0.0, 0
            self.motor_strength = np.ones(m.nu)
        m.actuator_gainprm[:, 0] = self.base_gain * self.motor_strength
        m.actuator_biasprm[:, :3] = self.base_bias * self.motor_strength[:, None]
        m.pair_friction[self.foot_pairs, :2] = self.base_pair_friction[self.foot_pairs] * self.friction
        m.body_mass[self.torso] = self.base_torso_mass + self.added_mass
        mujoco.mj_setConst(m, d)
        mujoco.mj_forward(m, d)
        self._bq = None

        self.t = 0
        self.last_action = np.zeros(self.nu)
        self.prev_applied = np.zeros(self.nu)
        self.last_qvel = d.qvel[self.vadr].copy()
        self.air_time = np.zeros(2)
        self.last_contact = np.ones(2, dtype=bool)
        self.feet_prev = d.site_xpos[self.foot_sites, :2].copy()
        self.next_push = self._push_interval()
        self._resample_command()
        self.next_cmd = self.t + int(self.rng.uniform(4, 8) / CTRL_DT)
        frame = self._actor_frame(noisy=True)
        self.hist = np.tile(frame, (HISTORY, 1))
        return self._obs(), self._priv_obs()

    def _push_interval(self):
        return self.t + int(self.rng.uniform(5, 10) / CTRL_DT)

    def _resample_command(self):
        r = self.cmd_ranges
        self.cmd = np.array([self.rng.uniform(*r[0]), self.rng.uniform(*r[1]), self.rng.uniform(*r[2])])
        if self.rng.random() < 0.1:
            self.cmd[:] = 0.0  # practice standing still
        elif np.linalg.norm(self.cmd[:2]) < 0.1:
            self.cmd[:2] = 0.0

    def set_command(self, cmd):
        self.cmd = np.asarray(cmd, dtype=float)
        self.next_cmd = 10**9

    # ------------------------------------------------------------- state util
    def _rot(self):
        return self.data.xmat[self.pelvis].reshape(3, 3)

    def _base_quantities(self):
        """(gyro, projected gravity, heading-frame velocity); cached until the next physics step."""
        if self._bq is not None:
            return self._bq
        d = self.data
        R = self._rot()
        gyro = d.sensordata[self.gyro_adr:self.gyro_adr + 3].copy()
        grav = R.T @ np.array([0.0, 0.0, -1.0])
        yaw = np.arctan2(R[1, 0], R[0, 0])
        c, s = np.cos(yaw), np.sin(yaw)
        v = d.qvel[0:3]
        v_heading = np.array([c * v[0] + s * v[1], -s * v[0] + c * v[1], v[2]])
        self._bq = (gyro, grav, v_heading)
        return self._bq

    def _phase(self):
        p = 2 * np.pi * (self.t * CTRL_DT) / GAIT_PERIOD
        return np.array([np.sin(p), np.cos(p)])

    def _actor_frame(self, noisy):
        d = self.data
        gyro, grav, _ = self._base_quantities()
        q = d.qpos[self.qadr] - self.q_default
        qd = d.qvel[self.vadr]
        if noisy and self.randomize:
            k = self.dr_scale
            gyro = gyro + k * self.rng.uniform(-0.2, 0.2, 3)
            grav = grav + k * self.rng.uniform(-0.05, 0.05, 3)
            q = q + k * self.rng.uniform(-0.01, 0.01, self.nu)
            qd = qd + k * self.rng.uniform(-1.5, 1.5, self.nu)
        cmd_scaled = self.cmd * np.array([2.0, 2.0, 0.25])
        return np.concatenate([gyro * 0.25, grav, cmd_scaled, q, qd * 0.05, self.last_action, self._phase()])

    def _obs(self):
        return self.hist.reshape(-1).astype(np.float32)

    def _priv_obs(self):
        _, _, v = self._base_quantities()
        extra = np.concatenate([v * 2.0, [self.data.qpos[2] - self.base_height_target],
                                [self.friction], [self.added_mass / 5.0], self.last_contact.astype(float)])
        return np.concatenate([self._actor_frame(noisy=False), extra]).astype(np.float32)

    def _contacts(self):
        d = self.data
        feet = np.zeros(2, dtype=bool)
        bad = 0
        for i in range(d.ncon):
            g1, g2 = d.contact[i].geom1, d.contact[i].geom2
            if g1 != self.floor and g2 != self.floor:
                continue
            other = g2 if g1 == self.floor else g1
            if other in self.foot_geoms[0]:
                feet[0] = True
            elif other in self.foot_geoms[1]:
                feet[1] = True
            else:
                bad += 1
        return feet, bad

    # ------------------------------------------------------------------- step
    def step(self, action):
        m, d = self.model, self.data
        action = np.clip(action, -1.0, 1.0)
        applied = self.prev_applied if self.delay else action
        self.prev_applied = action
        d.ctrl[:NUM_LEG] = self.q_default + ACTION_SCALE * applied
        mujoco.mj_step(m, d, nstep=DECIMATION)
        self._bq = None
        tau = d.actuator_force[:NUM_LEG]
        tau_sq = float(np.dot(tau, tau))
        self.t += 1

        # Pushes and command resampling
        if self.push_vel > 0 and self.t >= self.next_push:
            d.qvel[0:2] += self.rng.uniform(-self.push_vel, self.push_vel, 2)
            self._bq = None
            self.next_push = self._push_interval()
        if self.t >= self.next_cmd:
            self._resample_command()
            self.next_cmd = self.t + int(self.rng.uniform(4, 8) / CTRL_DT)

        gyro, grav, v = self._base_quantities()
        qvel = d.qvel[self.vadr]
        qpos = d.qpos[self.qadr]
        feet, bad = self._contacts()
        moving = np.linalg.norm(self.cmd[:2]) > 0.1 or abs(self.cmd[2]) > 0.2

        # Feet air time: rewarded on touchdown
        first_contact = feet & ~self.last_contact
        self.air_time += CTRL_DT
        air_r = np.sum((self.air_time - 0.4) * first_contact) if moving else 0.0
        self.air_time[feet] = 0.0
        self.last_contact = feet

        # Phase: left foot in stance when sin >= 0, right when sin < 0
        s = self._phase()[0]
        want_stance = np.array([s >= 0, s < 0]) if moving else np.array([True, True])
        phase_r = np.mean(feet == want_stance)

        feet_xy = d.site_xpos[self.foot_sites, :2]
        foot_v = (feet_xy - self.feet_prev) / CTRL_DT
        self.feet_prev = feet_xy.copy()

        height = d.qpos[2]
        fell = height < 0.45 or grav[2] > -0.5
        terms = {
            "lin_vel_tracking": np.exp(-np.sum((self.cmd[:2] - v[:2]) ** 2) / 0.25),
            "yaw_rate_tracking": np.exp(-(self.cmd[2] - d.qvel[5]) ** 2 / 0.25),
            "feet_air_time": air_r,
            "gait_phase_contact": phase_r,
            "base_height": (height - self.base_height_target) ** 2,
            "orientation": np.sum(grav[:2] ** 2),
            "vertical_velocity": v[2] ** 2,
            "torques": tau_sq,
            "joint_acc": np.sum(((qvel - self.last_qvel) / CTRL_DT) ** 2),
            "action_rate": np.sum((action - self.last_action) ** 2),
            "joint_limits": np.sum(np.clip(self.soft_lo - qpos, 0, None) + np.clip(qpos - self.soft_hi, 0, None)),
            "foot_slip": np.sum(np.sum(foot_v**2, axis=1) * feet),
            "body_contact": float(bad),
            "hip_pose": np.sum((qpos[self.hip_ry] - self.q_default[self.hip_ry]) ** 2),
            "termination": float(fell),
        }
        reward = CTRL_DT * sum(REWARD_WEIGHTS[k] * v_ for k, v_ in terms.items())

        self.last_qvel = qvel.copy()
        self.last_action = action.copy()
        frame = self._actor_frame(noisy=True)
        self.hist = np.roll(self.hist, -1, axis=0)
        self.hist[-1] = frame

        timeout = self.t >= MAX_STEPS
        info = {
            "terms": terms,
            "v": v.copy(),
            "yaw_rate": d.qvel[5],
            "cmd": self.cmd.copy(),
            "tau_sq": tau_sq,
            "fell": fell,
        }
        return self._obs(), self._priv_obs(), reward, fell, timeout, info
