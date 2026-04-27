---
title: GAUSS-VLA Thesis — First Calibrated, Geometry-Aware VLA
tags:
  - thesis
  - GAUSS-VLA
  - committed-direction
  - SE3
  - calibration
  - Q1-publication
  - T-RO
date: 2026-04-27
aliases:
  - GAUSS-VLA
  - The Thesis
  - Geometric Action with Uncertainty
cssclasses:
  - thesis
---

# 🎯 GAUSS-VLA: First Calibrated, Geometry-Aware VLA

> [!important] Status — COMMITTED RESEARCH DIRECTION
> After [[PRISM-VLA Brutal Critique & Redesign|PRISM was declared dead]] and STRATOS was attacked in [[Adversarial Debate — Sub-500M VLA Premise|the adversarial debate]], **GAUSS-VLA** is the committed thesis. **G**eometric **A**ction with **U**ncertainty for **S**ub-500M **S**ystems. Target venue: **IEEE Transactions on Robotics (T-RO)** primary, **IJRR** secondary.

---

## The Single-Line Thesis

> All published VLAs — SmolVLA, π0, OpenVLA, RDT-1B, ACT, Diffusion Policy — treat the action space as flat R⁶/R⁷ and provide no calibrated uncertainty. We prove this is theoretically suboptimal on SE(3), introduce the first geometry-aware flow-matching VLA with calibrated action uncertainty and adaptive replanning horizon, and demonstrate predicted gains on rotation-heavy and long-horizon manipulation at sub-500M parameters.

---

## Why This Thesis (And Not the Previous Ones)

### The Journey to GAUSS

1. **PRISM-VLA** (original): DVE + PACE + EAS. Killed by [[PRISM-VLA Brutal Critique & Redesign|Brutal Critique]] — DVE scooped (VLA-Cache, ADP, VLA-Pruner), PACE underpowered (30K params steering 256M backbone), EAS used PCA-on-SO(3) which is mathematically broken.
2. **STRATOS-VLA** (post-pivot): nonlinear AE per phase, learned changepoint detection (TPIN), uncertainty-driven token budgeting (ATB). Attacked in the [[Adversarial Debate — Sub-500M VLA Premise|Adversarial Debate]] — ATB has no formal definition, AE-on-axis-angle has the same SO(3) double-cover problem PCA had, hypernetwork is per-phase LoRA in disguise.
3. **PROGRESS-VLA** (debate counter): drop discrete phases, continuous τ + token-level MoE. Useful as decision-tool null architecture; rejected as a thesis because *"phases are wrong"* is a negative result, not Q1-headline material.
4. **GAUSS-VLA** (committed): subsumes the action-representation question (it's a Lie group, not an eigenspace) and adds what no current VLA has (calibration). This is the thesis.

### What This Means

The intuition behind EAS — that action space has structure — was correct. The structure is **a Lie group, not a linear subspace**. Once you accept this, PCA, eigenspaces, and per-phase autoencoders are all wrong abstractions. The right abstraction is Riemannian flow matching on SE(3).

---

## The Unsolved Problem (Measurable, Defensible)

### Problem A — Geometric

Rotations live on **SO(3)**, a 3-dimensional Lie group with non-trivial topology. Common parameterizations break:
- **Axis-angle** is a 2-cover: antipodal points $(\hat{n}, \pi)$ and $(-\hat{n}, \pi)$ map to the same rotation. Discontinuity at $\|\theta\| = \pi$.
- **Euler angles** have gimbal lock (singularities at certain configurations).
- **Quaternions** are a double-cover ($q$ and $-q$ are the same rotation), and naïve MSE loss penalizes equivalent representations.

**Every published VLA does flow matching or diffusion in flat R⁶ axis-angle ⊕ R³ translation coordinates.** Failure modes:
- Small action perturbations → large axis-angle output changes near $\|\theta\| = \pi$ → fragile policies
- ACT-style chunked prediction (H=8) crosses the antipodal boundary mid-chunk → discontinuous execution
- Euclidean MSE loss penalizes rotation pairs that are actually identical → wasted gradient signal

**The failure mode is empirically measurable**: on MT-50 rotation-heavy tasks (`dial-turn`, `door-unlock`, `faucet-open/close`, `nut-assemble`, `peg-insert-side`, `wrench`, `hammer`, `hand-insert`, `door-open/close`, `peg-unplug-side`, `window-open/close` — ~15 tasks), current VLAs accumulate execution error proportional to $\|\text{rotation}\|^2$ where $\|\text{rotation}\| > \pi/2$.

### Problem B — Epistemic

**No published VLA reports calibrated action uncertainty.** Flow matching and diffusion policies sample from an implicit distribution but don't quantify when the model is uncertain. Consequences:
- No principled stopping criterion for chunked prediction (ACT picks H=8 by hyperparameter search)
- No safe-deployment story (when to defer to a human?)
- No OOD detection (when is the policy outside its training distribution?)

### Together

Geometric error + uncalibrated uncertainty are the two silent failure modes that compound on rotation-heavy long-horizon tasks. **Closing both at the same time is the contribution that no current method addresses.**

---

## The Three Contributions (Coordinated, Not Independent)

### ① Riemannian Flow Matching on SE(3) — Theoretical Core

Formulate action prediction as a flow on the Lie group **SE(3) × R** using exponential coordinates and the log map for retraction. The flow matching loss on the Lie algebra $\mathfrak{se}(3)$:

$$\mathcal{L}_{SE(3)} = \mathbb{E}_{t, X_0, X_1} \left\| v_\theta(X_t, t) - \log_{X_t}(X_1) \right\|^2_{X_t}$$

where $X_t = \exp_{X_0}(t \cdot \log_{X_0}(X_1))$ is the geodesic interpolation on SE(3), and $\|\cdot\|_{X_t}$ is the Riemannian metric at $X_t$.

**Builds on**: Chen et al., *Flow Matching on General Geometries* (NeurIPS 2024) — proved the framework for Riemannian manifolds; **no one has applied it to robot actions in VLAs**.

#### Theorem 1 (Bounded Error of Euclidean Approximation) — to prove

Let $f^E$ be the optimal Euclidean flow matching policy on R⁶ axis-angle and $f^*$ the optimal SE(3) flow matching policy. For any rotation $R$ with $\|\log(R)\| = \theta$, the expected execution error satisfies

$$\mathbb{E}\|f^E(R) - f^*(R)\| \leq C \cdot \theta^2 + O(\theta^4)$$

for a constant $C$ depending on the data distribution. The bound is tight: there exist data distributions where Euclidean flow matching achieves the rate exactly.

> [!important] Why this theorem is the publication anchor
> Theorem 1 *predicts* the empirical gains in Contribution 3 — exactly what T-RO reviewers reward (theory→experiment alignment). It also bounds the silent error in every published Euclidean VLA, which is a clean motivational story.

### ② Calibrated Action Uncertainty via Low-Cost Ensembles — Empirical Core

A 3-head ensemble of small flow matchers (each ~20M params, 60M loaded total, ~20M active per step). Per-step disagreement provides epistemic uncertainty:

$$u(s_t, \ell) = \text{Var}_{i=1}^3 \left[ f_{\theta_i}(s_t, \ell) \right]$$

Calibrate against held-out execution error using **action-ECE** (the new metric we introduce):

$$\text{action-ECE} = \sum_b \frac{|B_b|}{N} \left| \text{conf}_b - \text{acc}_b \right|$$

where confidence is the inverse of $u$ (after temperature scaling) and accuracy is whether the action led to task progress on a held-out validation set.

**Novel framing**: no published VLA has reported calibration. **Action-ECE becomes the standard metric the field needs** — Q1 venues reward problem-opening more than problem-closing.

**Why ensembles, not MC-dropout or evidential**: variational dropout on flow matching is unstudied and tends not to calibrate well. Evidential deep learning requires likelihood structure that flow matching doesn't have. A 3-head ensemble is the *principled* choice; the cost is bounded and predictable.

### ③ Uncertainty-Driven Adaptive Replanning Horizon — Practical Core

Replace ACT's fixed H=8 chunking with an adaptive controller:

```python
def adaptive_horizon_policy(state, language, ensemble, threshold):
    chunk = ensemble.sample_action_chunk(state, language, H_max=8)
    for h in range(H_max):
        if ensemble.disagreement(chunk[h]) > threshold:
            return chunk[:h]   # commit chunk[:h], replan from h
    return chunk
```

#### Theorem 2 (Adaptive Horizon Contraction) — to prove

Under the calibrated uncertainty estimator from Contribution 2, the adaptive horizon policy is a contraction map on expected execution error with rate $\rho < 1$, while fixed-horizon policies achieve only $\rho = 1$ (no contraction).

This is the control-theoretic argument T-RO publishes — connects directly to receding-horizon control literature (Mayne et al.) and gives the empirical claim a formal anchor.

**Empirical claim**: measurable wins over fixed-H (ACT) and per-step (Diffusion Policy) on long-horizon tasks (LIBERO-Long, MT-50 Group E).

---

## Prior Art Positioning (No Surprises Like DVE)

| Prior work | What they do | Why GAUSS-VLA is novel against it |
|---|---|---|
| **Riemannian Flow Matching** (Chen et al., NeurIPS 2024) | General framework for flow matching on Riemannian manifolds | No robotics application; we apply to SE(3) for VLAs and prove the bounded-error theorem |
| **EquiBot / Equivariant Diffusion Policy** (2024) | SO(3)-equivariant diffusion policies | Equivariance ≠ geometric flow matching. Equivariance constrains the *function class*; we work in the proper *Riemannian metric*. Different and complementary. |
| **SE(3)-Diffuser** (2023) | SE(3)-aware diffusion for grasp generation | Diffusion not flow; grasp generation not full VLA; no calibration |
| **π0, RDT-1B, OpenVLA, SmolVLA** | Euclidean flow matching / diffusion in R⁶/R⁷ | Theorem 1 directly bounds their error on rotation-heavy tasks; we beat them where the bound is tight |
| **ACT** (Zhao et al., 2023) | Fixed-horizon chunked prediction (H=8) | Theorem 2 directly shows our adaptive horizon contracts where theirs doesn't |
| **Diffusion Policy** (Chi et al., 2023) | Per-step diffusion sampling | Subsumed by H=1 special case of our adaptive policy |
| **MC-dropout for VLAs** | (Gap — not done) | We introduce ensembles + action-ECE as the principled choice |
| **VLA-Cache, ADP, VLA-Pruner** | Visual token compression | Orthogonal — they handle perception efficiency; GAUSS handles action geometry+uncertainty. Citable as related work, not competition. |
| **Lie-group control theory** (Murray, Sastry, classical) | Control on Lie groups, no learning | Mathematical foundation we build on; we connect to learning-based VLAs |

**No scoops** for the combination. Specifically:
- Riemannian Flow Matching for *robot actions* — gap
- Calibrated VLA uncertainty with action-ECE — gap
- Adaptive replanning under calibrated SE(3) uncertainty — gap

---

## Parameter Budget

| Component | Loaded | Active per step |
|---|---|---|
| SmolVLM-2 backbone (frozen, 16 layers) | 256M | 256M |
| LoRA adapters (r=16) | 3M | 3M |
| 3× SE(3) flow heads (20M each) | 60M | 20M |
| Uncertainty-aware adaptive controller | 1M | 1M |
| SigLIP vision encoder (frozen, **fairly counted**) | 86M | 86M |
| **Total** | **406M** ✅ | **366M** |

Under 500M with SigLIP fairly counted — closing the accounting issue [[Parameter Budget Analysis|Brutal Critique #5]] flagged.

---

## What Carries Over from Existing Vault

| Existing component | Reuse in GAUSS-VLA |
|---|---|
| SmolVLM-2 backbone choice | Same backbone, frozen |
| Flow matching transformer architecture from [[Eigenspace Action Synthesis (EAS)]] | Reuse the 6-layer / 8-head transformer; drop the eigenspace decomposition; replace Euclidean output with SE(3) tangent-space output |
| LoRA configuration from [[Parameter Budget Analysis]] | Same r=16, same target modules (q_proj, v_proj, out_proj) |
| Training data pipeline from [[LIBERO Benchmark Strategy]] and [[MetaWorld MT-50 Strategy]] | Reuse, but revise targets (LIBERO demoted, LIBERO-PRO + rotation-heavy MT-50 promoted) |
| SmolVLA baseline protocol from [[SmolVLA Paper Notes]] | Run as primary same-scale baseline |

---

## What Dies Officially

- **DVE** — scooped, dead since the [[PRISM-VLA Brutal Critique & Redesign|Brutal Critique]]
- **PACE** — phases were the wrong abstraction; geometry-and-calibration is the right one
- **EAS in PCA form** — subsumed by SE(3) flow matching, which is mathematically more principled and doesn't need PCA at all
- **STRATOS's TPIN, ATB, per-phase AEs** — replaced by the three GAUSS contributions, which are coordinated rather than independent components
- **PROGRESS-VLA's MoE** — the simpler architecture won the *decision-tool* role in the debate but doesn't carry a Q1 thesis on its own

---

## Empirical Plan

### Datasets
- **LIBERO** (4 suites) — sanity check only (saturated)
- **LIBERO-PRO** — primary OOD test
- **MetaWorld MT-50** — primary multi-task benchmark with subset analysis

### Subsets for Causal Attribution
- **Rotation-heavy MT-50** (~15 tasks): `dial-turn`, `door-open/close`, `door-unlock/lock`, `faucet-open/close`, `nut-assemble`, `peg-insert-side`, `peg-unplug-side`, `wrench`, `hammer`, `hand-insert`, `window-open/close`
- **Long-horizon MT-50 Group E** (16 tasks, see [[MetaWorld MT-50 Strategy]])
- **LIBERO-Long** (10 tasks)

### Baselines
- **SmolVLA-450M** — primary same-scale baseline
- **OpenVLA-7B** — to demonstrate that geometry beats scale on rotation-heavy subset
- **π0-3.3B** — strongest competitor
- **ACT** — for adaptive horizon comparison
- **Diffusion Policy** — for per-step uncertainty comparison
- **GAUSS-VLA ablations**: (i) Euclidean flow only (no Theorem 1), (ii) single-head no calibration (no ② or ③), (iii) fixed-horizon (no ③)

### New Metric: Action-ECE
Report alongside success rate. Show every baseline is wildly miscalibrated. **This is the "introduce a metric" Q1 contribution.**

### Honest Expected Results

| Benchmark | SmolVLA | OpenVLA-7B | π0 | GAUSS-VLA | Headline gain |
|---|---|---|---|---|---|
| LIBERO mean (saturated) | 87.7 | 79.4 | 93.1 | 88–90 | ~tie |
| LIBERO-Long | 79 | 65 | 89 | 83–86 | +4–7 |
| LIBERO-PRO | low | low | low | +5–10 over SmolVLA | OOD |
| MT-50 mean | ~58 | ~55 | ~68 | 60–63 | +2–5 |
| **MT-50 rotation-heavy (15 tasks)** | ~50 | ~52 | ~65 | **62–68** | **+10–18** |
| MT-50 Group E long-horizon | ~45 | ~48 | ~60 | 53–58 | +6–13 |
| Action-ECE | not reported | not reported | not reported | **<0.05** | **first calibrated VLA** |

> [!important] The headline is NOT "we beat everything on average."
> The headline is: **"we beat the bound predicted by our theory on rotation-heavy tasks, are the first calibrated VLA, and do this at sub-500M parameters."**

---

## 6-Week Execution Plan (A100 Compute)

| Week | Deliverable | Compute |
|---|---|---|
| 1 | Theorem 1 proof draft + Riemannian flow matching loss derivation | None (pure theory) |
| 2 | Theorem 2 proof draft + adaptive horizon controller spec; SmolVLA MT-50 baseline run | 1 day A100 |
| 3 | SE(3) flow head implementation + ensemble training infrastructure | 2–3 days A100 |
| 4 | Calibration experiments; action-ECE harness; LIBERO sanity-check runs | 3 days A100 |
| 5 | Full LIBERO + MT-50 evaluation; ablations (Euclidean, single-head, fixed-horizon) | 5 days A100 |
| 6 | Paper writing + final ablations + rotation-heavy subset deep-dive | 2 days A100 |

**Total**: ~13–14 A100-days. 6 wall-clock weeks including theory-only Week 1.

---

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Theorem 1 doesn't have a clean form on full SE(3) | medium | Prove on SO(3) only, treat translation Euclideanly. Still novel, weaker theorem. |
| Theorem 2 contraction proof needs assumptions that don't hold | medium | Fall back to empirical comparison + monotonicity claim. Drop "contraction" language. |
| Ensemble too expensive at sub-500M | low | Reduce to 2 heads or share lower layers across ensemble |
| Adaptive horizon doesn't help empirically | medium | Drop Contribution ③, keep ①+②. Still publishable as a shorter T-RO paper. |
| Sub-500M just isn't enough capacity | low–medium | Frame headline at 1B parameter version; sub-500M becomes a deployment ablation. |
| Riemannian Flow Matching gets scooped by another VLA paper before submission | low | Submit early-access to T-RO Q3 2026; back up with arXiv |
| SE(3) implementation bugs (exp/log map numerical instability) | high | Use `geoopt`, `theseus`, `liegroups`; add unit tests for known SE(3) identities (exp(log(X)) = X, BCH formula) |

---

## Decision Triggers

This thesis is committed but not unconditional. Three triggers that would force re-evaluation:

1. **If Week 1 theory work shows Theorem 1 has a known counterexample** → pivot to (②+③) only, retitle paper around calibrated VLAs without the geometric theory headline.
2. **If SmolVLA MT-50 baseline (Week 2) shows the rotation-heavy subset is already at >70%** → the gap GAUSS targets is smaller than estimated; reduce scope to (①+②) and frame as deployment paper.
3. **If a Riemannian-flow-VLA paper appears on arXiv during Week 1–2** → accelerate timeline, lead with calibration contribution (which they likely won't have).

---

## Cross-References

- Tactical history: [[PRISM-VLA Brutal Critique & Redesign]]
- Strategic debate that led here: [[Adversarial Debate — Sub-500M VLA Premise]]
- Action-head architecture inheritance: [[Eigenspace Action Synthesis (EAS)]]
- Backbone choice and same-scale baseline: [[SmolVLA Paper Notes]]
- Benchmark targets (revised under this thesis): [[LIBERO Benchmark Strategy]], [[MetaWorld MT-50 Strategy]]
- Parameter accounting (now closed): [[Parameter Budget Analysis]]
- MOC: [[VLA Research Hub]]
- **Superseded** (kept for history, no longer active): [[PRISM-VLA Architecture Overview]], [[Differential Visual Encoding (DVE)]], [[Phase-Aware Cross-Attention Engine (PACE)]], [[Novelty Claims & Prior Art Check]]
