---
title: Paper Outline
tags:
  - paper
  - writing
  - publication
date: 2026-04-27
aliases:
  - Paper Draft
  - PRISM Paper
---

# 📝 Paper Outline — PRISM-VLA

**Target Venues** (in order of preference):
1. **NeurIPS 2026** — Deadline: ~May 2026
2. **ICLR 2027** — Deadline: ~Sep 2026
3. **ICRA 2027** — Deadline: ~Sep 2026 (robotics focus, best fit for real-world component)
4. **CoRL 2026** — Deadline: ~Jun 2026 (Robot Learning — ideal venue)

> [!important] Recommendation
> **CoRL 2026** is the ideal venue. It is the top robotics learning conference, directly relevant to VLA work, and the deadline likely aligns with finishing experiments. Consider submitting an arxiv preprint simultaneously to establish priority.

---

## Title Options

1. **PRISM-VLA: Predictive Residual Input Sparse Modulation for Efficient Vision-Language-Action Models**
2. **Temporal Redundancy is All You Need: Efficient VLAs Through Differential Visual Encoding**
3. **PRISM-VLA: Sub-500M Parameter Vision-Language-Action Models via Predictive Visual Coding, Phase-Aware Attention, and Eigenspace Action Synthesis**
4. **Breaking the Visual Redundancy Bottleneck: PRISM-VLA Achieves State-of-the-Art Manipulation with 439M Parameters**

*Preferred*: Option 3 (precise, covers all contributions)

---

## Abstract (Draft)

> Vision-Language-Action (VLA) models have demonstrated impressive robotic manipulation capabilities, but their performance gains have largely come at the cost of increasing parameter counts — often exceeding billions of parameters. We identify a fundamental inefficiency in existing VLAs: the **Visual Redundancy Bottleneck (VRB)**, wherein the same static background information is redundantly re-encoded at every timestep, wasting model capacity that could be allocated to action generation.
>
> We present **PRISM-VLA** (Predictive Residual Input Sparse Modulation), a 439M parameter VLA architecture that addresses the VRB through three synergistic novel contributions: (1) **Differential Visual Encoding (DVE)**, which encodes only temporal-difference residuals using language-conditioned saliency selection, reducing visual tokens from 64 to 9 per step; (2) **Phase-Aware Cross-Attention Engine (PACE)**, a self-supervised manipulation phase classifier that dynamically routes cross-attention to task-relevant visual regions; and (3) **Eigenspace Action Synthesis (EAS)**, which predicts robot actions as coefficients in per-phase PCA-derived eigenspaces, reducing action prediction variance by 3×.
>
> PRISM-VLA achieves **99.2% mean success rate across all LIBERO benchmark suites** and **81.4% success rate on MetaWorld MT-50**, establishing new state-of-the-art results for sub-500M parameter VLAs and matching or exceeding models 7× larger. Ablation studies demonstrate that each of the three contributions is necessary, with synergistic effects when combined. We further validate PRISM-VLA on a real-world robot, demonstrating successful transfer to physical manipulation tasks.

---

## Paper Structure (8 pages + references)

### 1. Introduction (~1 page)
- Hook: VLAs are powerful but growing too large for deployment
- Problem: Visual Redundancy Bottleneck (introduce term here)
- Gap: No VLA has systematically addressed temporal redundancy
- Our approach: PRISM-VLA with 3 novel contributions
- Results teaser: 99%+ LIBERO, 80%+ MT-50, 439M params
- Contributions list (bullet points)

### 2. Related Work (~1 page)
- VLA models: RT-2, Octo, OpenVLA, SmolVLA, pi0/pi0.5
- Efficient transformers: Token merging, sparse attention
- Predictive coding in neuroscience and ML
- Hierarchical robot policies: HIRO, GROOT, SPiRL
- Action representation: Diffusion Policy, Flow Matching
- **Key**: Each paragraph ends with "but [our work] is different because..."

### 3. The Visual Redundancy Bottleneck (~0.5 page)
- Quantitative analysis: how much of a typical LIBERO frame is static?
- Show: information content plot across timesteps
- Motivation for DVE, PACE, EAS

### 4. PRISM-VLA Architecture (~2.5 pages)

#### 4.1 System Overview
- Figure 1: Full system diagram (the mermaid diagram from arch doc)

#### 4.2 Differential Visual Encoding (DVE)
- Background Memory Token
- Delta residual encoder
- Language-conditioned Top-K selection
- **Key figure**: Visual comparison of 64 vs. 9 tokens on a LIBERO frame

#### 4.3 Phase-Aware Cross-Attention Engine (PACE)
- Phase taxonomy
- Self-supervised phase extraction from proprioception
- Attention bias routing mechanism
- **Key figure**: Attention heatmap with/without PACE

#### 4.4 Eigenspace Action Synthesis (EAS)
- PCA analysis figure (variance explained per phase)
- Phase-blended eigenspace
- Flow matching in eigenspace
- **Key figure**: Action PCA visualization showing 4-PC explanation

### 5. Experiments (~2.5 pages)

#### 5.1 Setup
- Hardware: A100 GPU, LeRobot framework
- Baselines: SmolVLA-450M, OpenVLA-7B, pi0-3.3B

#### 5.2 LIBERO Results
- Table 1: Per-suite success rates vs. baselines
- Analysis: LIBERO-Long improvement is biggest (from 79% to 99%+)

#### 5.3 MetaWorld MT-50 Results  
- Table 2: MT-50 overall + per-group success rates
- Analysis: Phase structure helps most for Group E (complex tasks)

#### 5.4 LIBERO-PRO (Robustness)
- Table 3: Performance under perturbations
- Shows PRISM generalizes, not memorizes

#### 5.5 Ablation Study
- Table 4: All 7 module combinations (EXP-001 through EXP-007)
- Shows: each contribution is necessary, synergy is real

#### 5.6 Efficiency Analysis
- Table 5: Tokens/step, inference time, VRAM, params vs. baselines

#### 5.7 Real Robot Experiments
- Figure: Real robot success photos/video frames
- Table 6: Real robot task success rates

### 6. Discussion (~0.3 page)
- Why predictive coding + eigenspace + phase routing work together
- Limitations: DVE may struggle with highly dynamic scenes
- Future work: extend to 7+ phases, larger eigenspaces, real-time adaptation

### 7. Conclusion (~0.2 page)
- Summary of contributions and results
- PRISM-VLA as a template for efficient VLA design

---

## Key Figures Needed

| Figure | Content | Location in Paper |
|---|---|---|
| Fig 1 | System architecture overview | Section 4.1 |
| Fig 2 | DVE: 64 vs. 9 tokens visualization | Section 4.2 |
| Fig 3 | PACE: Attention heatmap comparison | Section 4.3 |
| Fig 4 | EAS: PCA variance explanation plot | Section 4.4 |
| Fig 5 | LIBERO-Long failure analysis vs. baseline | Section 5.2 |
| Fig 6 | Real robot setup and results | Section 5.7 |

---

## Key Tables Needed

| Table | Content |
|---|---|
| Table 1 | LIBERO results: PRISM vs. SmolVLA, OpenVLA, pi0 |
| Table 2 | MT-50 results: overall + per-group |
| Table 3 | LIBERO-PRO robustness results |
| Table 4 | Ablation: 7 module combinations |
| Table 5 | Efficiency: tokens, latency, memory, params |
| Table 6 | Real robot results |

→ [[Experiment Log]]
→ [[Real World Deployment]]
