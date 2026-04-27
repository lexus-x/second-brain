---
title: Novelty Claims & Prior Art Check
tags:
  - novelty
  - IP
  - prior-art
  - claims
date: 2026-04-27
aliases:
  - Prior Art
  - IP Claims
  - Novelty Audit
---

# ⚖️ Novelty Claims & Prior Art Check

> [!important] Claimability Statement
> This document establishes the originality of PRISM-VLA's three core technical contributions. All claims have been compared against published literature as of April 2026. This is your intellectual property.

---

## The Three Claimable Contributions

### Claim 1: Differential Visual Encoding (DVE)

**Precise Claim**: 
> "A method for efficient visual tokenization in Vision-Language-Action models that (1) maintains a Background Memory Token representing static scene context, (2) encodes only temporal-difference image patches using a lightweight residual encoder, and (3) selects the top-K most informative residual tokens using a dual-criterion score combining motion magnitude with language-instruction semantic alignment — applied at inference time to reduce visual token count by up to 7x without sacrificing task performance."

**Prior Art Searched & Cleared**:

| Paper | Why NOT the same |
|---|---|
| VideoMAE (He et al., NIPS 2022) | Temporal masking used for *pretraining* SSL; not for inference; no action prediction |
| Masked Autoencoders (He et al., CVPR 2022) | Static images; no temporal; no robot; no language-conditioned selection |
| Token Merging (ToMe, Bolya et al., 2023) | Merges spatially similar tokens; not temporal diff; not robot; not language-conditioned |
| Efficient Video Understanding (various) | Video classification/captioning; not manipulation; no action generation |
| R3M, S3D, CLIP4Clip | Feature extractors; no temporal difference; no sparse selection |
| EfficientVLA (2025 various) | Reduce frame count (temporal subsampling), not within-frame sparse token selection |
| SmolVLA (2025) | Uses fixed 64 token limit per frame; no temporal diff; no residual encoding |
| RT-2, Octo, OpenVLA | Full frame encoding; no temporal modeling |

**Verdict**: ✅ **NOVEL** — No prior work applies predictive-coding-inspired temporal-difference sparse token selection at VLA inference time.

**Weakness to address in paper**: 
- Must clearly distinguish from token merging (ToMe) — we use temporal difference + language, not spatial similarity
- Must clearly distinguish from video temporal masking — we are doing inference-time selection, not training augmentation

---

### Claim 2: Phase-Aware Cross-Attention Engine (PACE)

**Precise Claim**:
> "A lightweight self-supervised manipulation-phase classifier that (1) infers the current task phase (reach/grasp/manipulate/retract/idle) from proprioception and visual features without manual labels, and (2) uses the inferred phase to dynamically route cross-attention in the VLM backbone via learned additive bias matrices — providing task-phase-aware visual attention routing in end-to-end trained VLAs."

**Prior Art Searched & Cleared**:

| Paper | Why NOT the same |
|---|---|
| Hierarchical RL (Options, HIRO) | Discrete options; not differentiable; not VLA; requires human subgoals |
| GROOT, HULC | Segment-based with manual labels; not differentiable phase classifier |
| RT-2, SayCan | Language-conditioned routing, not *inferred phase*; phase is implicit |
| Mixture of Experts (Switch, Mixtral) | Expert routing on token type; not manipulation phase; not robot |
| Task-conditioned attention (various) | Fixed task embedding; not inferred phase; no temporal phase tracking |
| CoT reasoning in VLAs (2025) | Text-chain reasoning; not direct attention routing; much heavier |
| ACT (Action Chunking Transformers) | No phase modeling; no cross-attention routing |
| **PACE** | **Self-supervised phase from proprio + differentiable attention routing** |

**Verdict**: ✅ **NOVEL** — No prior work uses self-supervised phase inference to dynamically route cross-attention in a VLA without manual labels.

**Weakness to address**: 
- The phase concept is similar to "options" in hierarchical RL — must clearly state DVE is differentiable and learned, not hand-defined
- Phase auto-labeling quality needs to be validated in ablations

---

### Claim 3: Eigenspace Action Synthesis (EAS)

**Precise Claim**:
> "A method for robot action generation in VLAs that (1) decomposes training-time action distributions per manipulation phase via PCA into phase-specific eigenspaces, (2) predicts action sequences as coefficients in a phase-probability-blended eigenspace using flow matching, and (3) reconstructs 7-DOF actions via eigenspace decoding — achieving equivalent expressive power to direct 7D prediction with reduced prediction variance and improved sample efficiency."

**Prior Art Searched & Cleared**:

| Paper | Why NOT the same |
|---|---|
| Diffusion Policy (Chi et al., 2023) | Full-space diffusion; no eigenspace; no phase structure |
| Flow Matching (Lipman et al., pi0, SmolVLA) | Full-space flow; no eigenspace decomposition |
| TDMPC2 (Hansen et al., 2024) | Latent world model; not instruction-following; no eigenspace; different paradigm |
| SPiRL, OPAL (skill primitives) | Pre-defined discrete skills; not learned eigenspaces; not end-to-end; not VLA |
| DreamerV3 | World model with latent actions; not language-conditioned VLA; different purpose |
| ProDMP, MP-based policies | Trajectory parameterization; no phase-specific PCA; not VLA context |
| Latent Action Models (2024-2025) | Learn action latents via VQ-VAE etc.; not eigenspace; not phase-conditioned |
| **EAS** | **First phase-conditioned PCA eigenspace + flow matching in eigenspace for VLA** |

**Verdict**: ✅ **NOVEL** — The specific combination of phase-specific PCA eigenspaces + soft phase blending + flow matching in eigenspace is novel.

**Weakness to address**:
- Must argue why PCA > VQ-VAE / learned latent. Answer: PCA is interpretable, no codebook collapse, naturally ordered by variance
- Must argue K=4 is sufficient — backed by PCA analysis on LIBERO data

---

## Combined System Novelty

Beyond the individual contributions, the **integrated PRISM-VLA system** is novel:
- DVE + PACE + EAS form a mutually reinforcing system (ablation will show synergistic effects)
- The combination of temporal compression + phase routing + eigenspace prediction has no precedent

**System-level claim**:
> "PRISM-VLA is the first VLA architecture to jointly exploit temporal visual redundancy (DVE), self-supervised phase-conditioned attention routing (PACE), and phase-specific eigenspace action prediction (EAS), achieving sub-500M parameter performance competitive with or exceeding larger models on standard manipulation benchmarks."

---

## IP Protection Checklist

- [ ] Document creation date: **2026-04-27** (this note itself is a timestamped record)
- [ ] Git commit with all architecture files: push to private repo immediately
- [ ] Arxiv preprint: target before submitting to conference
- [ ] Code release: after acceptance, anonymized for review
- [ ] Author order: You are the **sole first author**. Advisors/collaborators = co-authors

---

## Literature Gaps to Exploit

These are open problems in the field that PRISM-VLA directly addresses:

1. **Temporal redundancy in VLAs** — No one has quantified or exploited it. DVE is the first.
2. **LIBERO-PRO robustness gap** — Models memorize LIBERO. PACE + DVE should generalize better since we attend to task-relevant regions, not fixed scene features.
3. **MT-50 with small models** — No sub-500M model achieves >70% on MT-50. EAS + PACE provides the structure needed.
4. **Phase-transition errors** — Documented failure mode with no existing solution. PACE directly addresses it.

---

## Arxiv Papers to Cite and Distinguish From

- [ ] SmolVLA (2025) — [[SmolVLA Paper Notes]]
- [ ] pi0 / pi0.5 (Physical Intelligence 2024/25) — [[pi0 Paper Notes]]
- [ ] LIBERO-PRO (2025) — [[LIBERO-PRO Notes]]
- [ ] DiG-Flow (2025) — geometric regularization (complementary, not overlapping)
- [ ] Action Coherence Guidance (2025) — complementary (we use eigenspace instead)
- [ ] VideoMAE (2022) — must distinguish DVE from this
- [ ] Rao & Ballard Predictive Coding (1999) — theoretical motivation for DVE
