---
title: Resources & Codebases
tags:
  - resources
  - links
  - datasets
  - code
date: 2026-04-27
aliases:
  - Resources
  - Links
---

# 🔗 Resources & Codebases

---

## Key Codebases

| Repo | Purpose | Link |
|---|---|---|
| LeRobot | Framework for SmolVLA + PRISM-VLA | https://github.com/huggingface/lerobot |
| LIBERO | Benchmark simulation | https://github.com/Lifelong-Robot-Learning/LIBERO |
| MetaWorld | MT-50 benchmark | https://github.com/Farama-Foundation/Metaworld |
| LIBERO-PRO | Robustness evaluation | https://github.com/Zxy-MLlab/LIBERO-PRO |
| SmolVLM-2 | VLM backbone | https://huggingface.co/HuggingFaceTB/SmolVLM2 |
| Open-X Embodiment | DVE pretraining data | https://github.com/google-deepmind/open_x_embodiment |

---

## Key Papers to Read

### Essential (Read First)

- [ ] **SmolVLA** (HuggingFace, 2025) — Our primary baseline
  - arXiv: TBD / HuggingFace blog
  - Notes: [[SmolVLA Paper Notes]]

- [ ] **pi0: A Vision-Language-Action Flow Model** (Black et al., Physical Intelligence, 2024)
  - arXiv: 2410.24164
  - Why: Best large VLA, our stretch comparison target

- [ ] **LIBERO-PRO** (Zhou et al., 2025)
  - GitHub: https://github.com/Zxy-MLlab/LIBERO-PRO
  - Why: Defines the robustness benchmark we must ace

- [ ] **OpenVLA** (Kim et al., 2024)
  - arXiv: 2406.09246
  - Why: Classic VLA baseline, in all tables

### Architecture Insights

- [ ] **Flow Matching for Generative Modeling** (Lipman et al., ICLR 2023)
  - arXiv: 2210.02747
  - Why: Foundation for EAS flow matching head

- [ ] **Predictive Coding** (Rao & Ballard, Nature Neuroscience 1999)
  - DOI: 10.1038/2035
  - Why: Theoretical foundation for DVE

- [ ] **VideoMAE** (He et al., NeurIPS 2022)
  - arXiv: 2203.12602
  - Why: Distinguish DVE from temporal masking

- [ ] **Mamba Policy** (IROS 2025)
  - Why: Understand SSM-based policy efficiency claims (compare/contrast)

### MT-50 Relevant

- [ ] **MetaWorld** (Yu et al., CoRL 2020)
  - arXiv: 1910.10897
  - Why: MT-50 original paper, task definitions

- [ ] **CARE** (multi-task RL baseline)
  - Why: Current best on MT-50 with non-VLA methods

### Real World

- [ ] **DINOv2** (Oquab et al., TMLR 2024)
  - arXiv: 2304.07193
  - Why: Potential alternative visual backbone for DVE

---

## Datasets

| Dataset | Size | Use | Access |
|---|---|---|---|
| LIBERO Demonstrations | 50 demos × 40 tasks | Main training | https://huggingface.co/datasets/lerobot/libero |
| Open-X Embodiment | ~1M episodes | DVE pretraining | https://robotics-transformer-x.github.io |
| MetaWorld MT-50 scripted | 100 demos × 50 tasks | MT-50 training | Generated via metaworld env |
| Bridge v2 | ~60k demos | Optional additional DVE pretraining | https://rail.eecs.berkeley.edu/datasets/bridge_release |

---

## Compute Resources

| Resource | Spec | Use |
|---|---|---|
| A100 80GB (×1) | Primary GPU | Training + eval |
| A100 80GB (×2) | If available | MT-50 training (2× faster) |
| CPU (32 core) | Data preprocessing, eigenspace computation | |

### Estimated Compute Budget

| Step | Time (1× A100) |
|---|---|
| DVE Pretraining | 48h |
| Phase Classifier | 4h |
| LIBERO Phase 3 (LoRA) | 24h |
| LIBERO Phase 4 (Full FT) | 12h |
| MT-50 Joint Training | 72h |
| Evaluation (all benchmarks) | 24h |
| **Total** | **~184h = ~8 days** |

> [!tip] Optimization
> Phase 3 + Phase Classifier can be parallelized (different GPUs). Total wall clock with 2× A100: ~5–6 days.

---

## Software Environment

```bash
# Core
Python 3.10
PyTorch 2.3.0 + CUDA 12.1
transformers 4.40+
accelerate 0.28+

# Robotics
lerobot (latest)
gymnasium 0.26
metaworld (latest)
libero (latest)

# Training
wandb  # experiment tracking
einops  # tensor operations
timm    # vision backbones (ResNet-18)
scikit-learn  # PCA for eigenspaces

# Visualization
matplotlib
seaborn
opencv-python
```

---

## Useful Commands Cheatsheet

```bash
# Check GPU status
nvidia-smi

# Start experiment tracking
wandb login

# Run LIBERO eval (quick check, 5 trials per task)
python eval.py --model checkpoint.pt --n_trials 5 --suite libero_long

# Profile inference time
python profile_inference.py --model checkpoint.pt --n_steps 100

# Compute eigenspace (quick test on small dataset)
python scripts/compute_eigenspaces.py --data_dir data/libero --n_episodes 10 --debug
```
