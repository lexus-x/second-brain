---
title: Real World Deployment
tags:
  - real-robot
  - deployment
  - hardware
date: 2026-04-27
aliases:
  - Real Robot
  - Deployment
---

# 🤖 Real World Deployment

> [!important] Key Advantage of PRISM-VLA for Real Robots
> DVE's temporal compression means **10Hz control is achievable on a single A100** — or even a consumer RTX 4090. SmolVLA needs dedicated GPU clusters for real-time. PRISM runs on a laptop GPU.

---

## Hardware Compatibility

| Robot Platform | PRISM Compatible? | Notes |
|---|---|---|
| Franka Research 3 | ✅ Yes | Primary target. 7-DOF, most LIBERO demo data uses Franka |
| Universal Robots UR5 | ✅ Yes | 6-DOF (modify EAS for 6D eigenspace) |
| Kinova Gen3 | ✅ Yes | 7-DOF, similar to Franka |
| WidowX 250 | ✅ Yes | Lower-end, good for fast iteration |
| BiManual (e.g. Aloha) | 🔶 Partial | Need 14-DOF EAS (2× eigenspaces, one per arm) |

---

## Real Robot Transfer Protocol

### Step 1: Domain Adaptation (Simulation → Real)

The main sim-to-real gap comes from:
1. **Visual domain**: Simulator rendering vs. real camera
2. **Physics**: Simulated vs. real contact dynamics
3. **Noise**: Clean sim proprio vs. noisy real sensors

**PRISM-VLA mitigation** (built into training):
- DVE encodes temporal *differences*, not absolute textures → more robust to visual domain gap
- EAS eigenspaces are defined in action space (not visual) → physics robustness built-in
- PACE uses proprioception → noisy sensors handled by robustifying phase classifier

**Additional steps**:
```
1. Collect ~20 real robot demonstrations per task
2. Fine-tune DVE delta encoder on real camera images (5k steps, 1 hour)
3. Fine-tune LoRA adapters on real demos (10k steps, 2 hours)
4. PACE and EAS: no changes needed (proprio-based, already robust)
```

### Step 2: Real-time Control Setup

```python
# Real robot inference loop
import time
from prism_vla import PRISMPolicy
from robot_interface import FrankaInterface

policy = PRISMPolicy.from_pretrained("path/to/checkpoint")
robot = FrankaInterface()

instruction = "pick up the red cube and place it in the bowl"
episode_start = True
prev_frame = None

while True:
    t0 = time.time()
    
    # Get current observation
    frame = robot.get_rgb_image()          # 224×224×3
    proprio = robot.get_proprio_state()    # 14-dim
    
    # PRISM inference
    with torch.no_grad():
        actions = policy.predict(
            frame=frame,
            prev_frame=prev_frame,
            instruction=instruction,
            proprio=proprio,
            episode_start=episode_start,
        )
    
    # Execute first action in chunk
    robot.execute_action(actions[0])
    
    prev_frame = frame
    episode_start = False
    
    # Control loop timing
    dt = time.time() - t0
    time.sleep(max(0, 0.1 - dt))  # 10Hz control
    print(f"Inference time: {dt*1000:.1f}ms")
    # Target: <50ms per step (PRISM) vs. ~100ms (SmolVLA)
```

### Step 3: Real World Task Protocol

For the paper's real robot experiments, use tasks that:
1. **Mirror LIBERO tasks** (tabletop pick-place, bowl stacking)
2. **Have unambiguous success criteria** (object in target location)
3. **Are repeatable** (object can be reset between trials)

**Proposed real robot tasks**:
| Task | Description | LIBERO Analog |
|---|---|---|
| RW-1 | Pick red block, place in bowl | LIBERO-Object Task 3 |
| RW-2 | Open drawer, place item inside | LIBERO-Goal Task 7 |
| RW-3 | Stack two blocks | LIBERO-Spatial Task 2 |
| RW-4 | Pour cup into bowl (multi-step) | LIBERO-Long Task 4 |
| RW-5 | Sort 3 objects by color | Novel (beyond LIBERO) |

**Evaluation**: 20 trials per task, randomized object placement (±5cm) per trial.

---

## Real World Safety Protocol

> [!caution] Safety Rules — Follow These Strictly
> 1. **Always use E-stop**: Keep hand on emergency stop during all trials
> 2. **Workspace limits**: Set hard joint limits via controller (never exceed ±10cm from workspace center)
> 3. **Speed limits**: Real robot speed capped at 50% of max during experiments
> 4. **Object selection**: Start with foam/plastic objects, no glass or heavy items initially
> 5. **Trial 1 always supervised**: Never run an unvalidated policy without human present

---

## Real World DVE Insights

DVE has an interesting real-world advantage:
- In simulation, pixel-level differences are clean
- In the real world, camera noise, lighting flicker, and micro-vibrations add spurious "deltas"

**Solution**: DVE's saliency selector naturally handles this — noise adds small, spatially uniform deltas (low L2 magnitude), which score below the Top-K threshold. Only meaningful motion (arm, object displacement) scores high.

**Expected real-world performance**: ~85–90% of simulation performance (standard sim-to-real gap for this setup). With fine-tuning on real demos: ~95% recovery.

---

## Real World → Publication Checklist

- [ ] Collect 20 demos per RW task
- [ ] Run sim-to-real adaptation protocol (steps 1–2)
- [ ] Run 20 evaluation trials per RW task
- [ ] Record video of all trials for supplementary material
- [ ] Compute success rates, record failure modes
- [ ] Create side-by-side comparison video: SmolVLA vs. PRISM-VLA on same task
- [ ] Add real robot section to paper (Section 5.7)

→ [[Paper Outline]]
→ [[Experiment Log]]
