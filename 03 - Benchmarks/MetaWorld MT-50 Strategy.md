---
title: MetaWorld MT-50 Strategy
tags:
  - benchmark
  - MetaWorld
  - MT-50
  - strategy
  - target-80%
date: 2026-04-27
aliases:
  - MT-50 Strategy
  - MetaWorld Strategy
---

# 📊 MetaWorld MT-50 Strategy — Target: ≥80%

---

## MT-50 Overview

MetaWorld MT-50 is the **hardest multi-task manipulation benchmark**. 50 distinct tasks, trained simultaneously as a single policy.

| Difficulty Factor | Why It's Hard |
|---|---|
| 50 tasks simultaneously | Policy must generalize across radically different manipulation types |
| Single policy, no task-switching | No task ID at inference — must infer from image + language alone |
| Dense reward evaluation | Success requires precise completion, not just partial progress |
| No demonstration data (originally) | Designed for RL; VLAs use collected demos |
| Task interference | Learning "push button" can interfere with "open door" |

**Current SOTA (sub-500M)**: SmolVLA ~55–62% (not publicly confirmed — needs verification)  
**Current SOTA (any size)**: Larger VLAs ~65–72%  
**PRISM-VLA target**: **≥80%**

---

## Why MT-50 is the Real Test

> [!caution] LIBERO vs. MT-50
> LIBERO is essentially a **memorization benchmark** — high diversity but the test set closely mirrors training. MT-50 requires genuine **multi-task generalization**: the same policy must reach, grasp, push, turn, open, close, and assemble across 50 task types without forgetting any.

Hitting 80% on MT-50 with <500M parameters would be a **landmark result** that significantly advances the field. No sub-500M model has done this.

---

## Task Taxonomy & PRISM Mapping

MT-50 tasks can be grouped by manipulation primitive:

```
Group A — REACH/TOUCH (8 tasks):
  reach, reach-wall, button-press-topdown, button-press, 
  button-press-topdown-wall, button-press-wall, coffee-button, handle-press
  → Predominantly REACH + GRASP phases
  → DVE benefit: high (arm is the main moving thing)
  → EAS benefit: medium

Group B — PUSH/SLIDE (9 tasks):
  push, push-wall, push-back, soccer, coffee-push, 
  shelf-place, plate-slide, plate-slide-side, plate-slide-back
  → REACH + MANIPULATE phases
  → DVE benefit: high
  → PACE benefit: high (need to track object displacement)

Group C — PICK/PLACE (7 tasks):
  pick-place, pick-place-wall, pick-out-of-hole, 
  assembly, disassemble, box-close, bin-picking
  → Full phase sequence (all 5 phases)
  → Most benefited by EAS (full eigenspace diversity)
  → PACE most critical here

Group D — OPEN/CLOSE (10 tasks):
  door-open, door-close, drawer-open, drawer-close, 
  window-open, window-close, faucet-open, faucet-close,
  coffee-button, handle-press-side  
  → REACH + GRASP + MANIPULATE with rotation
  → EAS: rotation-dominant eigenspace matters most

Group E — COMPLEX/MULTI-STEP (16 tasks):
  hammer, peg-insert-side, peg-unplug-side, stick-push, stick-pull,
  basketball, hand-insert, lever-pull, rope, sweep, sweep-into,
  dial-turn, door-unlock, door-lock, nut-assemble, wrench
  → Multiple sub-tasks within one task
  → PACE phase tracking most critical
  → DVE temporal continuity helps most
```

---

## MT-50 Specific Challenges for PRISM-VLA

### Challenge 1: Task Interference

**Problem**: LoRA adapters trained on all 50 tasks may interfere. A "push" signal might partially activate "pick" patterns.

**Solution**: 
- Task-grouped LoRA: separate LoRA adapter sets for Groups A–E (5 sets × 3M = 15M additional params — still within budget)
- Task-type is inferred from language embedding: "push" → Group B LoRA activated
- This is NOT task-specific fine-tuning — groups share parameters within group

### Challenge 2: Reward Signal Quality

**Problem**: MT-50 success is binary — full task completion or 0. This is a sparse reward for training.

**Solution**:
- Use **phase-level reward shaping** during training: `R = R_success + α*R_phase_completion`
- Phase completion reward: +0.1 each time PACE detects a phase transition in the right direction
- This densifies the reward without manual annotation (PACE auto-labels phases)

### Challenge 3: Camera Configuration Variation

**Problem**: MT-50 has a single fixed camera, but the gripper-relative view changes drastically across tasks.

**Solution**: 
- DVE's BMT captures the task-specific scene efficiently
- Residual encoding adapts to task-specific movement patterns
- Data augmentation: random camera offset ±10% during training

---

## MT-50 Training Recipe

### Demonstration Data Collection

```
MT-50 demonstrations: 50 episodes per task × 50 tasks = 2,500 episodes
Using scripted expert policy (MetaWorld provides) + small amount of human corrections
Target: 5,000 episodes after human-corrected rollouts
```

### Training Phases

**Phase 1: Phase Eigenspace Computation for MT-50**
```
Compute per-phase PCA across ALL 50 tasks jointly
Then compute per-task-group eigenspace (5 groups × 5 phases = 25 eigenspaces)
This is the MT-50 EAS configuration
```

**Phase 2: Multi-task Joint Training (2–3 days on 2× A100)**
```
Batch sampling: stratified by task group (equal samples per group)
Trainable: DVE, PACE, EAS flow head, task-grouped LoRA (5 sets)
Frozen: backbone weights (except LoRA)
LR: cosine schedule 1e-4 → 1e-6 over 200k steps
Loss: L_flow + 0.1*L_phase + 0.05*L_task_type
```

**Phase 3: Per-Group Fine-tuning (12 hours × 5 groups)**
```
After joint training, fine-tune each group LoRA independently for 10k steps
Prevents catastrophic interference while maintaining shared knowledge
```

---

## Expected Results Analysis

**Conservative estimate (assuming no synergistic effects)**:
- SmolVLA baseline: ~58% on MT-50
- DVE contribution: +5% (better visual tracking in cluttered scenes)
- PACE contribution: +8% (phase structure reduces task interference)
- EAS contribution: +5% (better manipulation precision)
- Task-grouped LoRA: +5% (reduces interference)
- **Total conservative**: ~81%

**Aggressive estimate (with synergistic effects)**:
- Up to ~87% if eigenspaces generalize well within groups

**Risk**: Task Group E (complex multi-step) is hardest. May only reach 65–70% on that group. This drags down the mean. Mitigation: allocate more training steps to Group E.

---

## Comparison Table (Target)

| Model | Params | MT-50 Success |
|---|---|---|
| MTRL-CARE | - | ~45% |
| OpenVLA (7B, adapted) | 7B | ~55% |
| SmolVLA (estimated) | 450M | ~58% |
| pi0-adapted | 3.3B | ~68% |
| **PRISM-VLA (Target)** | **439M** | **≥80%** |

If PRISM-VLA achieves 80% on MT-50 at 439M parameters, this is the **best-ever result for sub-500M models** and competitive with 3B+ models.

→ [[LIBERO Benchmark Strategy]]
→ [[Ablation Plan EAS]]
→ [[Experiment Log]]
