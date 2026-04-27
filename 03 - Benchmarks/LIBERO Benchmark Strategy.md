---
title: LIBERO Benchmark Strategy
tags:
  - benchmark
  - LIBERO
  - strategy
  - target-99%
date: 2026-04-27
aliases:
  - LIBERO Strategy
  - LIBERO 99%
---

# 📊 LIBERO Benchmark Strategy — Target: ≥99%

---

## LIBERO Suite Overview

| Suite | Tasks | Focus | SmolVLA (reported) | PRISM Target |
|---|---|---|---|---|
| LIBERO-Spatial | 10 | Spatial reasoning, object arrangement | ~92% | **≥99%** |
| LIBERO-Object | 10 | Object manipulation variety | ~90% | **≥99%** |
| LIBERO-Goal | 10 | Goal-conditioned tasks | ~88% | **≥99%** |
| LIBERO-Long | 10 | Long-horizon multi-step | ~79% | **≥99%** |
| **Mean** | **40** | | **~87%** | **≥99%** |

> [!important] Why 99% is Hard
> LIBERO-Long is the critical bottleneck. It requires 3–5 sub-tasks in sequence. One failure cascades. No VLA has cracked 95%+ on LIBERO-Long. This is where PRISM-VLA must prove DVE + PACE + EAS are synergistic.

---

## Why PRISM-VLA Should Hit 99%

### The Argument for LIBERO-Spatial/Object/Goal (≥99%)

SmolVLA gets ~90% on these. The gap to 99% is caused by:
1. **Occasional grasp failures** → EAS reduces grasp prediction variance → fewer missed grasps
2. **Distractors in scene** → PACE routes attention away from distractors → fewer wrong-object grasps  
3. **Approach jitter** → DVE detects fine-grained position changes → smoother reaching

Expected improvement per module:
- DVE alone: +3–4% (better reach precision)
- PACE alone: +2–3% (fewer distractor failures)  
- EAS alone: +2–3% (better grasp success)
- Combined (synergistic): +10–12% → ~99–100% on Spatial/Object/Goal

### The Argument for LIBERO-Long (≥99%)

LIBERO-Long fails because:
1. **Phase transition confusion** → exactly what PACE addresses
2. **Compounding errors over 3–5 steps** → DVE's temporal continuity helps (consistent visual state tracking)
3. **Spatial displacement during long tasks** → DVE's BMT reset mechanism handles scene changes

Expected improvement: +15–20% on LIBERO-Long

---

## Training Recipe for LIBERO

### Data

```
Total LIBERO demonstrations: 50 demos × 40 tasks = 2,000 episodes
Augmentation strategy:
  - Camera view jitter: ±5° pan, ±2° tilt
  - Object texture randomization (ResNet-level)
  - Object position jitter: ±2cm
  - Lighting variation: ±20% brightness
  - Language paraphrasing: 5 variants per instruction (use GPT-4o to generate)
  
After augmentation: ~10,000 effective episodes
```

### Training Phases

**Phase 0: DVE Pretraining (2 days on 1× A100)**
```
Dataset: Open-X Embodiment (subset, ~100k clips)
Objective: Reconstruction + Contrastive + Language Alignment
Epochs: 20
LR: 1e-4 → 1e-5 cosine
```

**Phase 1: Phase Classifier Pretraining (4 hours on 1× A100)**
```
Dataset: LIBERO demos with auto-extracted phase labels
Objective: Cross-entropy phase classification
Epochs: 50
LR: 1e-3
```

**Phase 2: Eigenspace Computation (30 minutes, CPU)**
```
Compute PCA per phase on LIBERO action distributions
Store E_phase, mu_phase as frozen buffers
```

**Phase 3: Main Training — Frozen Backbone + LoRA (1 day on 1× A100)**
```
Trainable: DVE delta encoder, saliency selector, PACE biases, EAS flow head
Frozen: SmolVLM-2 backbone (except LoRA adapters r=16)
Batch: 64
Steps: 100k
LR: 1e-4 (action head), 1e-5 (DVE), 5e-5 (LoRA)
Loss: L_flow + 0.1*L_phase
```

**Phase 4: Full Fine-tuning (12 hours on 1× A100)**
```
Unfreeze: all LoRA + Phase Classifier + DVE
LR: 5e-5 (all components, lower)
Steps: 30k
Early stopping on LIBERO-Long validation success rate
```

**Phase 5: LIBERO-PRO Robustness Fine-tuning (optional, 6 hours)**
```
Dataset: LIBERO-PRO augmented training split
Objective: Same + perturbation regularization
Goal: Robustness ≥80% on LIBERO-PRO
```

---

## Evaluation Protocol

```python
# Standard LIBERO evaluation
for suite in ['LIBERO-Spatial', 'LIBERO-Object', 'LIBERO-Goal', 'LIBERO-Long']:
    for task in suite.tasks:
        success_count = 0
        for trial in range(20):  # 20 trials per task (standard)
            result = run_episode(model, task, seed=trial)
            if result.success:
                success_count += 1
        task_success_rate = success_count / 20
    suite_success_rate = mean(task_success_rates)
```

**Target**: Mean suite success rate ≥99% across all 4 suites (= ≥99% mean across 40 tasks)

---

## Known Failure Modes to Monitor

| Failure Mode | Likely Cause | PRISM Fix |
|---|---|---|
| Wrong object grasped | Distractor in scene | PACE attention routing |
| Grasp slip (object falls) | Approach angle wrong | EAS + lower variance |
| Task abandoned mid-way | Phase transition confusion | PACE phase detection |
| Long-horizon error cascade | Early mistake corrupts state | DVE reset mechanism |
| Instruction misinterpretation | Ambiguous language | LoRA fine-tune + augmentation |

---

## Comparison Table (Target)

| Model | Params | LIBERO-S | LIBERO-O | LIBERO-G | LIBERO-L | Mean |
|---|---|---|---|---|---|---|
| OpenVLA | 7B | 84.7 | 88.4 | 79.2 | 65.3 | 79.4 |
| SmolVLA-450M | 450M | 92.1 | 90.8 | 88.3 | 79.4 | 87.7 |
| pi0 | 3.3B | 94.2 | 95.1 | 93.7 | 89.2 | 93.1 |
| **PRISM-VLA (Target)** | **439M** | **≥99** | **≥99** | **≥99** | **≥99** | **≥99** |

→ [[MetaWorld MT-50 Strategy]]
→ [[LIBERO-PRO Notes]]
→ [[Experiment Log]]
