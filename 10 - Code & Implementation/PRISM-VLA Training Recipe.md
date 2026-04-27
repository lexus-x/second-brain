---
title: PRISM-VLA Training Recipe
tags:
  - training
  - recipe
  - implementation
date: 2026-04-27
aliases:
  - Training Recipe
  - How to Train PRISM
---

# 🍳 PRISM-VLA Full Training Recipe

---

## Prerequisites

```bash
# Environment setup
conda create -n prism-vla python=3.10
conda activate prism-vla
pip install torch==2.3.0 torchvision transformers accelerate
pip install lerobot gymnasium==0.26 metaworld
pip install einops timm wandb

# Clone base repo
git clone https://github.com/huggingface/lerobot
cd lerobot

# Install our PRISM-VLA extension (our code)
pip install -e ".[prism]"
```

---

## Step 0: Prepare Datasets

```bash
# Download LIBERO demonstrations
python scripts/download_libero.py --suite all --save_dir data/libero

# Download Open-X Embodiment subset (for DVE pretraining)
python scripts/download_openx.py \
  --subset bridge_v2,fractal \
  --max_episodes 100000 \
  --save_dir data/openx_subset

# Collect MetaWorld MT-50 demonstrations
python scripts/collect_metaworld.py \
  --tasks all_50 \
  --episodes_per_task 100 \
  --policy scripted \
  --save_dir data/metaworld_mt50
```

---

## Step 1: Compute Action Eigenspaces

```python
# prism/eigenspace.py
python scripts/compute_eigenspaces.py \
  --data_dir data/libero \
  --n_components 4 \
  --save_path configs/eigenspaces_libero.pt

python scripts/compute_eigenspaces.py \
  --data_dir data/metaworld_mt50 \
  --n_components 4 \
  --task_grouped true \
  --save_path configs/eigenspaces_mt50.pt
```

Output: `configs/eigenspaces_libero.pt` containing:
```python
{
  'REACH': {'eigenvectors': R^{4×7}, 'mean': R^7},
  'GRASP': {'eigenvectors': R^{4×7}, 'mean': R^7},
  'MANIPULATE': {'eigenvectors': R^{4×7}, 'mean': R^7},
  'RETRACT': {'eigenvectors': R^{4×7}, 'mean': R^7},
  'IDLE': {'eigenvectors': R^{4×7}, 'mean': R^7},
}
```

---

## Step 2: Extract Phase Labels

```python
# Auto-label phases from proprioception trajectories
python scripts/label_phases.py \
  --data_dir data/libero \
  --output_dir data/libero_labeled \
  --velocity_threshold 0.05 \
  --gripper_threshold 0.3

# Validate labeling quality (optional, requires some manual check)
python scripts/validate_phase_labels.py \
  --labeled_dir data/libero_labeled \
  --sample_n 100
# Expected output: ~92% agreement with random manual checks
```

---

## Step 3: Pretrain DVE Delta Encoder

```bash
python train_dve.py \
  --dataset data/openx_subset \
  --output_dir checkpoints/dve_pretrained \
  --epochs 20 \
  --batch_size 128 \
  --lr 1e-4 \
  --lambda_reconstruct 0.1 \
  --lambda_align 0.5 \
  --wandb_project prism-vla \
  --wandb_run_name dve-pretrain
# Expected time: ~48 hours on 1× A100 80GB
```

---

## Step 4: Pretrain Phase Classifier

```bash
python train_phase_classifier.py \
  --dataset data/libero_labeled \
  --output_dir checkpoints/phase_cls \
  --epochs 50 \
  --batch_size 256 \
  --lr 1e-3 \
  --wandb_project prism-vla \
  --wandb_run_name phase-cls-pretrain
# Expected time: ~4 hours on 1× A100
```

---

## Step 5: Main LIBERO Training — Phase 3 (LoRA Frozen Backbone)

```bash
python train_prism.py \
  --config configs/prism_libero_phase3.yaml \
  --dataset data/libero_labeled \
  --dve_ckpt checkpoints/dve_pretrained/best.pt \
  --phase_cls_ckpt checkpoints/phase_cls/best.pt \
  --eigenspaces configs/eigenspaces_libero.pt \
  --output_dir checkpoints/prism_libero_phase3 \
  --wandb_project prism-vla \
  --wandb_run_name prism-libero-p3
# Expected time: ~24 hours on 1× A100
```

Config (`prism_libero_phase3.yaml`):
```yaml
model:
  backbone_frozen: true
  lora_rank: 16
  lora_alpha: 32
  dve_frozen: false
  pace_frozen: false
  eas_frozen: false

training:
  steps: 100000
  batch_size: 64
  lr_schedule: cosine
  lr_action_head: 1.0e-4
  lr_dve: 1.0e-5
  lr_lora: 5.0e-5
  lr_pace: 1.0e-4
  gradient_clip: 1.0
  
loss:
  lambda_phase: 0.1
  
eval:
  eval_every: 5000
  n_eval_episodes: 10
  suite: libero_long  # most informative
```

---

## Step 6: Full Fine-tuning — Phase 4

```bash
python train_prism.py \
  --config configs/prism_libero_phase4.yaml \
  --resume checkpoints/prism_libero_phase3/best.pt \
  --output_dir checkpoints/prism_libero_phase4 \
  --wandb_project prism-vla \
  --wandb_run_name prism-libero-p4
# Expected time: ~12 hours on 1× A100
```

Config changes for Phase 4:
```yaml
model:
  backbone_frozen: false  # unfreeze for full fine-tune
  phase_cls_frozen: false  # unfreeze phase classifier

training:
  steps: 30000
  lr_action_head: 5.0e-5  # lower LR for fine-tune
  lr_backbone: 2.0e-5
  early_stopping_metric: libero_long_success
  early_stopping_patience: 5000
```

---

## Step 7: MetaWorld MT-50 Training

```bash
# First compute MT-50 eigenspaces
python scripts/compute_eigenspaces.py \
  --data_dir data/metaworld_mt50 \
  --task_grouped true \
  --save_path configs/eigenspaces_mt50.pt

# Train MT-50 policy
python train_prism_mt50.py \
  --config configs/prism_mt50.yaml \
  --dataset data/metaworld_mt50 \
  --dve_ckpt checkpoints/dve_pretrained/best.pt \
  --phase_cls_ckpt checkpoints/phase_cls/best.pt \
  --eigenspaces configs/eigenspaces_mt50.pt \
  --output_dir checkpoints/prism_mt50 \
  --wandb_project prism-vla \
  --wandb_run_name prism-mt50
# Expected time: ~72 hours on 2× A100 (longer due to 50 tasks)
```

---

## Step 8: Evaluation

```bash
# LIBERO evaluation (standard)
python eval.py \
  --model checkpoints/prism_libero_phase4/best.pt \
  --benchmark libero_all \
  --n_trials 20 \
  --output results/prism_libero_results.json

# LIBERO-PRO evaluation (robustness)
python eval_libero_pro.py \
  --model checkpoints/prism_libero_phase4/best.pt \
  --n_trials 20 \
  --output results/prism_libero_pro_results.json

# MetaWorld MT-50 evaluation
python eval_mt50.py \
  --model checkpoints/prism_mt50/best.pt \
  --n_trials 50 \
  --output results/prism_mt50_results.json
```

---

## Debugging Checklist

- [ ] DVE produces exactly 9 tokens per step? `assert visual_tokens.shape[1] == 9`
- [ ] Phase probabilities sum to 1? `assert phase_probs.sum(-1).allclose(1.0)`
- [ ] EAS reconstructions close to ground truth? `check_eigenspace_reconstruction(demo)`
- [ ] PACE biases initialized to 0? `assert pace_bias.abs().max() < 1e-5`
- [ ] LoRA not affecting frozen backbone? `verify_frozen_params(model.backbone)`
- [ ] Eigenspaces loaded correctly? `verify_eigenspace_variance(eigenspaces, min_var=0.95)`
