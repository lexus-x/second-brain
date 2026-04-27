---
title: Parameter Budget Analysis
tags:
  - architecture
  - parameters
  - budget
date: 2026-04-27
aliases:
  - Param Budget
  - Parameter Count
---

# 🧮 PRISM-VLA Parameter Budget Analysis

**Hard constraint**: < 500M total parameters

---

## Detailed Count

### Layer 1: DVE — Differential Visual Encoder

| Sub-component | Parameters | Notes |
|---|---|---|
| SigLIP Background Encoder | 86M | Frozen, not counted toward trainable |
| ResNet-18 Delta Encoder | 11.2M | Trainable, lightweight |
| Saliency Cross-Attention (Q,K) | 0.5M | 64-dim heads, one layer |
| BMT Compression MLP | 0.3M | 512→512, 2 layers |
| **DVE Total (trainable)** | **12.0M** | |

### Layer 2: VLM Backbone

| Sub-component | Parameters | Notes |
|---|---|---|
| SmolVLM-2 (16 layers) | 256M | Frozen during main training |
| LoRA Adapters (r=16) | ~3.0M | q_proj, v_proj, out_proj × 16 layers |
| **Backbone Total (frozen + LoRA)** | **259M** | Frozen: 256M, Trainable: 3M |

### Layer 3: PACE — Phase-Aware Cross-Attention Engine

| Sub-component | Parameters | Notes |
|---|---|---|
| Phase Classifier MLP | 2.0M | [in→256→128→5] |
| Attention Bias Vectors | 0.03M | 5 phases × 16 layers × (42×9) |
| **PACE Total** | **2.03M** | |

### Layer 4: EAS — Eigenspace Action Synthesizer

| Sub-component | Parameters | Notes |
|---|---|---|
| Eigenspace Buffers (E, μ) | 0.002M | Fixed buffers, not trainable |
| Flow Matching Transformer | 79.8M | 6 layers, 8 heads, dim=256, H=8 |
| **EAS Total** | **79.8M** | |

### MT-50 Additional (only for MT-50 model)

| Sub-component | Parameters | Notes |
|---|---|---|
| Task-Type Classifier | 1.5M | 1-layer MLP from language embedding |
| Additional LoRA sets (4 more groups) | ~12M | 5 groups × 3M = 15M (4 additional) |
| **MT-50 Additional** | **13.5M** | |

---

## Total Count Summary

### LIBERO Model

| Component | Frozen | Trainable | Total |
|---|---|---|---|
| DVE | 86.0M | 12.0M | 98.0M |
| VLM Backbone + LoRA | 256.0M | 3.0M | 259.0M |
| PACE | 0M | 2.03M | 2.03M |
| EAS | 0M | 79.8M | 79.8M |
| **LIBERO Total** | **342.0M** | **96.83M** | **438.83M** |

**Total: ~439M parameters** ✅ Under 500M limit

**Trainable: ~97M parameters** — this is what you actually train from scratch or fine-tune

### MT-50 Model

| Component | Total |
|---|---|
| LIBERO model | 439M |
| MT-50 additional | +13.5M |
| **MT-50 Total** | **452.5M** |

**MT-50 Total: ~453M parameters** ✅ Still under 500M limit

---

## Parameter Efficiency Comparison

| Model | Params | LIBERO | MT-50 | Params/Performance |
|---|---|---|---|---|
| OpenVLA | 7B | 79.4% | ~55% | Very inefficient |
| pi0 | 3.3B | 93.1% | ~68% | Moderate |
| SmolVLA | 450M | 87.7% | ~58% | Good |
| **PRISM-VLA** | **439M** | **≥99%** | **≥80%** | **Best** |

**PRISM-VLA achieves ~16× fewer parameters than OpenVLA while targeting ~25% better performance.**

---

## Budget Allocation Rationale

Why 79.8M for EAS flow head?

The EAS head is the most computationally expensive component because:
1. It generates actions autoregressively across H=8 timesteps
2. It must integrate backbone features, proprioception, and phase information
3. It handles the "synthesis" (hardest task) of the entire pipeline

The 6-layer transformer with 256 hidden dim was chosen by:
- Starting from SmolVLA's 100M action expert
- Replacing 7D flow matching with 4D eigenspace flow matching → 43% output reduction
- This allowed reducing the head to 80M while maintaining expressive power

**Alternative**: If DVE is later found to need more capacity, we can reduce EAS to 60M (4 layers) and expand DVE delta encoder to 30M. Total remains <500M.

---

## Safety Margin

Current: 439M / 500M = **87.8%** of budget used

**Remaining buffer: 61M parameters** — enough for:
- Larger DVE encoder (ResNet-34 instead of ResNet-18): +15M
- Deeper PACE (5-layer instead of 3-layer): +2M
- Additional task-type LoRA groups: +15M per group
- Real robot adaptation layers: +5M

→ [[PRISM-VLA Architecture Overview]]
