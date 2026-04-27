---
title: VLA Research Hub — Master Map of Content
tags:
  - MOC
  - VLA
  - robotics
  - research
aliases:
  - Hub
  - Research Home
date: 2026-04-27
cssclasses:
  - moc
---

# 🧠 VLA Research Hub

> [!important] Mission Statement
> Design, validate, and publish **PRISM-VLA** — a sub-500M parameter Visual Language Action model that achieves **≥99% on LIBERO** and **≥80% on MetaWorld MT-50** through a fundamentally novel *Predictive Residual Input Sparse Modulation* architecture. This is PhD-level original science, fully claimable, and real-world deployable.

---

## 🗺️ The Research Map

```mermaid
graph TD
    A["🏠 VLA Research Hub"] --> B["🔬 Research Foundations"]
    A --> C["🏗️ Novel Architecture\n(PRISM-VLA)"]
    A --> D["📊 Benchmarks"]
    A --> E["📚 Literature Review"]
    A --> F["🧪 Experiments"]
    A --> G["🤖 Real World Deployment"]
    A --> H["📝 Paper Draft"]

    B --> B1["Problem Space"]
    B --> B2["Why VLAs Fail"]
    B --> B3["Key Insight"]

    C --> C1["PRISM Architecture"]
    C --> C2["DVE Module"]
    C --> C3["PACE Module"]
    C --> C4["EAS Module"]
    C --> C5["Parameter Budget"]

    D --> D1["LIBERO Suite"]
    D --> D2["MetaWorld MT-50"]
    D --> D3["LIBERO-PRO"]

    E --> E1["SmolVLA"]
    E --> E2["pi0 / pi0.5"]
    E --> E3["OpenVLA"]
    E --> E4["RoboVLMs"]
    E --> E5["Mamba Policy"]

    F --> F1["Ablation Plan"]
    F --> F2["Experiment Log"]
    F --> F3["Baseline Results"]

    G --> G1["Real Robot Setup"]
    G --> G2["Deployment Protocol"]
```

---

## 📁 Vault Structure

| Folder | Purpose |
|---|---|
| [[VLA Research Hub]] | You are here — master MOC |
| `01 - Research Foundations` | The "why" — problems, gaps, key insight |
| `02 - Novel Architecture` | PRISM-VLA design documents |
| `03 - Benchmarks` | LIBERO, MetaWorld, LIBERO-PRO specs |
| `04 - Literature Review` | Annotated papers |
| `05 - Experiments` | Ablations, logs, results |
| `06 - Real World Deployment` | Robot setup, deployment notes |
| `07 - Paper Draft` | LaTeX-ready sections |
| `08 - Daily Log` | Daily research journal |
| `09 - Resources` | Datasets, codebases, links |
| `10 - Code & Implementation` | Architecture pseudocode, configs |

---

## 🎯 Project North Stars

- [ ] **LIBERO Suite**: ≥99% mean success across all 4 suites
- [ ] **LIBERO-PRO**: ≥80% (robustness target — generalization, not memorization)
- [ ] **MetaWorld MT-50**: ≥80% mean success rate
- [ ] **Parameter count**: < 500M total
- [ ] **Inference speed**: ≥10Hz on single A100 (real-robot deployable)
- [ ] **Novelty**: ≥3 novel technical contributions, all prior-art-checked
- [ ] **Publication**: NeurIPS / ICLR / ICRA ready

---

## 🔥 The Core Novel Idea (In One Sentence)

> **PRISM-VLA** exploits the *temporal redundancy* of visual observations in robotic manipulation — encoding only what *changed* and *why it matters* — to free the model's full capacity for action generation, achieving superior performance at a fraction of the compute.

→ [[PRISM-VLA Architecture Overview]]
→ [[The Core Scientific Insight]]
→ [[Novelty Claims & Prior Art Check]]

---

## Autoresearch Integration

> Source: [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch)
> Working translation for this vault: use autonomous loops only where the success signal is mechanical, bounded, and repeatable.

### Why it matters for PRISM-VLA

- The repo's core pattern is: one goal, one metric, one focused change, one verification loop.
- That fits this project well because the main targets are measurable: LIBERO success, MetaWorld success, parameter count, and inference speed.
- The caution is equally important: do not use autoresearch for vague scientific judgment. Use it for measurable subproblems, then do human review for theory and claim framing.

### Best-fit uses in this research program

| Autoresearch command | Best use in this vault | Desired output |
|---|---|---|
| `$autoresearch plan` | Turn vague goals into bounded research loops | metric, scope, verify command |
| `$autoresearch` | Run architecture or training ablations with one change per iteration | keep/revert experiment history |
| `$autoresearch predict` | Generate ranked hypotheses before burning training time | prioritized failure / opportunity list |
| `$autoresearch scenario` | Enumerate failure modes for rollout, distractors, long-horizon control, and dataset shift | edge-case matrix |
| `$autoresearch reason` | Adversarially stress-test novelty claims and paper arguments | stronger claim set with weak points exposed |
| `$autoresearch ship --type research` | Pre-submission paper checklist | submission readiness report |

### VLA-specific metrics worth operationalizing

- `LIBERO mean success %`
- `MetaWorld MT-50 mean success %`
- `params_millions`
- `sim_inference_hz` or `real_robot_hz`
- `ablation_delta_vs_baseline`
- `PRISMA compliance %` for literature review structure
- `claim_evidence_coverage %` for novelty audit completeness

### Suggested command patterns

```text
$autoresearch plan
Goal: Raise LIBERO mean success above SmolVLA baseline without exceeding 500M params
```

```text
$autoresearch
Iterations: 15
Goal: Improve LIBERO mean success for PRISM-VLA
Scope: 02 - Novel Architecture/**, 05 - Experiments/**, 10 - Code & Implementation/**
Metric: LIBERO mean success % (higher is better)
Verify: run_libero_eval_and_extract_metric
Guard: check_params_under_500m && check_inference_hz
```

```text
$autoresearch predict --chain debug
Goal: Identify the most likely causes of weak long-horizon manipulation performance
Scope: training configs, architecture notes, baseline results, failure analysis notes
```

```text
$autoresearch scenario --depth deep --focus edge-cases
Scenario: PRISM-VLA succeeds on short-horizon tasks but degrades under distractors, viewpoint shift, and long-horizon sequencing
Domain: software
```

```text
$autoresearch reason --domain research
Task: Stress-test the claim that differential visual encoding is genuinely novel relative to SmolVLA, OpenVLA, pi0/pi0.5, and Mamba-style sequence models
```

```text
$autoresearch ship --type research
Target: 07 - Paper Draft/
```

### Practical rules for this vault

- Keep loops narrow: one benchmark, one module, one ablation family at a time.
- Prefer fast verify commands. If a loop takes hours, use autoresearch to plan and rank experiments first, not to brute-force everything.
- Treat `git log` as the experiment journal: every kept and reverted ablation should teach the next move.
- Use `$autoresearch reason` for novelty and paper argument quality, because those are partly subjective.
- Use `$autoresearch` only after the metric extractor is trustworthy and the baseline run is reproducible.

---

## 📅 Research Timeline

```mermaid
gantt
    title PRISM-VLA Research Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1 — Design
    Architecture Design          :done, 2026-04-27, 14d
    Novelty Audit & Prior Art    :active, 2026-04-27, 7d
    section Phase 2 — Simulation
    LIBERO baseline (SmolVLA)    :2026-05-11, 7d
    PRISM-VLA LIBERO training    :2026-05-18, 21d
    MetaWorld MT-50 training     :2026-06-08, 21d
    Ablations                    :2026-06-29, 14d
    section Phase 3 — Real World
    Real robot transfer          :2026-07-13, 21d
    Real world experiments       :2026-08-03, 30d
    section Phase 4 — Publication
    Paper writing                :2026-08-17, 30d
    Submission                   :milestone, 2026-09-15, 0d
```

---

## 🧭 Quick Navigation

- [[The Core Scientific Insight]] ← **Start here**
- [[PRISM-VLA Architecture Overview]] ← The full system
- [[Differential Visual Encoding (DVE)]] ← Novel module 1
- [[Phase-Aware Cross-Entropy (PACE)]] ← Novel module 2
- [[Eigenspace Action Synthesis (EAS)]] ← Novel module 3
- [[LIBERO Benchmark Strategy]] ← How to hit 99%
- [[MetaWorld MT-50 Strategy]] ← How to hit 80%
- [[Novelty Claims & Prior Art Check]] ← Claim your IP
- [[Experiment Log]] ← Live results
- [[Paper Outline]] ← Publication path
