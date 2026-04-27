---
title: SmolVLA Paper Notes
tags:
  - literature
  - SmolVLA
  - baseline
  - VLA
date: 2026-04-27
aliases:
  - SmolVLA
  - SmolVLA baseline
---

# 📄 SmolVLA — Annotated Paper Notes

**Authors**: HuggingFace Robotics team  
**Year**: 2025 (June)  
**Venue**: Preprint (arXiv)  
**Link**: https://huggingface.co/papers/smolvla  
**Model**: 450M parameters

---

## What SmolVLA Does

SmolVLA is designed as an **efficient, open-source VLA** that fits on consumer hardware. Key design choices:

### Architecture
- **VLM Backbone**: SmolVLM-2 (first 16 layers only) ≈ 350M params
- **Action Expert**: Separate transformer module ≈ 100M params
- **Action Generation**: **Flow Matching** (not diffusion) — faster inference
- **Visual Tokens**: **64 tokens per frame** (fixed, capped)
- **Inference**: Asynchronous — decouples observation processing from action execution

### Key Architectural Innovations in SmolVLA
1. **Layer Skipping**: Only uses first 16 of 24 VLM layers — trades accuracy for speed
2. **64-token cap**: Hard limit on visual tokens prevents quadratic attention blowup
3. **Flow Matching action expert**: One-step action generation (vs. iterative diffusion)
4. **Async inference stack**: Reduces wall-clock latency ~30% by pipelining observation and action

---

## What SmolVLA Gets Right (We Should Keep)

- ✅ Flow Matching as the action generation mechanism — **EAS builds on top of this**
- ✅ Separate action expert module — **EAS is our enhanced version**
- ✅ SmolVLM-2 backbone — **We use the same frozen backbone**
- ✅ Layer skipping (first 16 layers) — **We adopt this**
- ✅ Asynchronous inference — **We adopt this pattern**

---

## What SmolVLA Gets Wrong (Our Improvements)

| SmolVLA Limitation | PRISM-VLA Solution |
|---|---|
| 64 visual tokens per frame, re-encoded each step | DVE: 9 tokens/step (1 BMT + 8 residual) |
| No temporal modeling between frames | DVE: temporal difference encoding |
| Language-conditioned attention, but phase-agnostic | PACE: phase-conditioned attention routing |
| 7D raw action prediction | EAS: 4D eigenspace prediction per phase |
| Single action head for all task phases | EAS: phase-blended eigenspace |
| No MT-50 multi-task strategy | PRISM: task-grouped LoRA + phase structure |

---

## SmolVLA Performance (Reported)

| Benchmark | SmolVLA | Notes |
|---|---|---|
| LIBERO-Spatial | ~92% | Our target: 99% |
| LIBERO-Object | ~90% | Our target: 99% |
| LIBERO-Goal | ~88% | Our target: 99% |
| LIBERO-Long | ~79% | Our target: 99% |
| LIBERO Mean | ~87% | Our target: 99% |
| MetaWorld MT-50 | ~55–62% (estimated) | Our target: 80% |

> [!note] Note on SmolVLA MT-50 numbers
> SmolVLA does not officially report MT-50 results. The 55–62% estimate is based on scaling from OpenVLA's performance and SmolVLA's relative improvement on LIBERO. Must verify by running SmolVLA on MT-50 as our baseline.

---

## Key Insight from SmolVLA Failure Analysis

SmolVLA's most common failure modes on LIBERO-Long:
1. **Phase confusion at transitions**: Doesn't know when to switch from REACH to GRASP
2. **Distractor attention**: Looks at the wrong object when scene has multiple similar items
3. **Accumulated error in long tasks**: Small errors compound over 5+ steps

All three are addressed by PRISM-VLA's PACE + DVE combination.

---

## SmolVLA as Our Baseline

**Baseline Protocol**:
- Download SmolVLA-450M from HuggingFace
- Run on LIBERO (all 4 suites, 20 trials per task, standard eval)
- Run on MetaWorld MT-50 (50 trials per task, success criteria per task spec)
- Record per-task, per-phase failure modes
- Use this as ground truth baseline

**Expected time**: 2 days of GPU compute for full baseline eval

→ [[Experiment Log]]
→ [[PRISM-VLA Architecture Overview]]
