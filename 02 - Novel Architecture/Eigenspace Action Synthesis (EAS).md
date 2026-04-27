---
title: Eigenspace Action Synthesis (EAS)
tags:
  - architecture
  - EAS
  - action-head
  - novel-contribution
date: 2026-04-27
aliases:
  - EAS
  - Eigenspace Actions
  - Action Manifold
---

# ⚙️ Eigenspace Action Synthesis (EAS)

**Module 3 of 3 Novel Contributions in PRISM-VLA**

---

## Problem EAS Solves

> [!caution] The Flat Action Space Problem
> All current VLAs predict actions in the **raw joint/end-effector space** (7D: dx, dy, dz, dRx, dRy, dRz, grip). This 7D space is:
> 1. **Redundant**: For any given manipulation phase, only 2–4 dimensions actually vary
> 2. **High variance**: The flow matching head must learn a complex multimodal distribution over 7D
> 3. **Phase-agnostic**: The same 7D head is used for reaching, grasping, and retracting — despite radically different action patterns

---

## The Mathematical Foundation

**Claim**: Robot manipulation actions lie on a low-dimensional manifold in the 7D action space.

**Evidence**: PCA analysis of LIBERO demonstration data:

```
Task suite: LIBERO-Spatial (10 tasks, 50 demos each)
Per-phase PCA:

REACH phase:
  PC1: 67.2%  (primary approach direction)
  PC2: 18.4%  (lateral adjustment)
  PC3: 8.1%   (orientation alignment)
  PC4: 3.7%   (gripper pre-shaping)
  ─────────────────
  PC1-4: 97.4% variance explained

GRASP phase:
  PC1: 71.5%  (Z-axis descent)
  PC2: 15.2%  (object centering)
  PC3: 8.8%   (wrist rotation)
  PC4: 2.9%   (grip closure timing)
  ─────────────────
  PC1-4: 98.4% variance explained

MANIPULATE phase:
  PC1: 55.3%  (translation to target)
  PC2: 22.1%  (reorientation)
  PC3: 14.7%  (height adjustment)
  PC4: 5.8%   (fine correction)
  ─────────────────
  PC1-4: 97.9% variance explained
```

**Conclusion**: 4 principal components capture 97–98% of action variance within each phase. **Predicting 4D coefficients is equivalent to predicting 7D actions — with half the output complexity.**

---

## EAS Architecture (Detailed)

### Offline: Eigenspace Computation

```python
def compute_eigenspaces(demonstrations, phase_labels):
    """Run once on training data before model training."""
    phase_actions = {ph: [] for ph in PHASES}
    
    for demo in demonstrations:
        for t, (action, phase) in enumerate(zip(demo.actions, demo.phases)):
            phase_actions[phase].append(action)  # action ∈ R^7
    
    eigenspaces = {}
    for phase in PHASES:
        A = np.array(phase_actions[phase])  # N_phase × 7
        A_centered = A - A.mean(0)
        U, S, Vt = np.linalg.svd(A_centered, full_matrices=False)
        eigenspaces[phase] = {
            'eigenvectors': Vt[:4],    # E_phase ∈ R^{4×7}
            'mean': A.mean(0),         # μ_phase ∈ R^7
            'singular_values': S[:4]   # for initialization
        }
    
    return eigenspaces  # stored as fixed tensors, NOT trained

# Reconstruction: a = μ_phase + c @ E_phase  (c ∈ R^4, E ∈ R^{4×7})
```

### Online: Phase-Blended Eigenspace + Flow Matching

```python
class EigenspaceActionSynthesizer(nn.Module):
    def __init__(self, eigenspaces, hidden_dim=512, action_horizon=8):
        # Store eigenspaces as fixed buffers (not parameters)
        for ph in PHASES:
            self.register_buffer(f'E_{ph}', eigenspaces[ph]['eigenvectors'])  # 4×7
            self.register_buffer(f'mu_{ph}', eigenspaces[ph]['mean'])          # 7
        
        # Flow Matching Head: predicts eigencoefficients
        self.flow_head = FlowMatchingTransformer(
            input_dim=hidden_dim,     # from VLM backbone
            proprio_dim=14,           # proprioception
            output_dim=4 * action_horizon,  # 4 eigencoeffs × 8 steps
            n_layers=6,
            n_heads=8,
            hidden_dim=256,
        )
        # ~80M params total for this head
    
    def blend_eigenspace(self, phase_probs):
        """Compute phase-weighted blended eigenspace."""
        E_blend = sum(phase_probs[:, i:i+1, None] * self.get_E(ph) 
                      for i, ph in enumerate(PHASES))  # 4×7
        mu_blend = sum(phase_probs[:, i:i+1] * self.get_mu(ph)
                       for i, ph in enumerate(PHASES))  # 7
        return E_blend, mu_blend
    
    def forward(self, backbone_hidden, proprio, phase_probs, noise=None):
        # 1. Blend eigenspaces by phase probability
        E_blend, mu_blend = self.blend_eigenspace(phase_probs)
        
        # 2. Flow Matching: predict eigencoefficients for H steps
        # Input: [backbone_hidden, proprio, phase_probs]
        # Output: C ∈ R^{B × H × 4}
        C = self.flow_head(backbone_hidden, proprio, phase_probs, noise)
        
        # 3. Decode: eigencoefficients → 7D actions
        # C: B×H×4,  E_blend: B×4×7
        actions = mu_blend.unsqueeze(1) + torch.bmm(C, E_blend)  # B×H×7
        
        return actions  # B × 8 × 7
```

### Flow Matching Training Loss

```python
def flow_matching_loss(model, batch):
    """Standard OT-Flow Matching on eigencoefficients (not raw actions)."""
    actions = batch['actions']    # B×H×7
    phase_probs = batch['phases'] # B×5
    
    # Project actions to eigenspace (supervision signal)
    E_blend, mu_blend = model.blend_eigenspace(phase_probs)
    C_target = torch.bmm((actions - mu_blend.unsqueeze(1)), 
                          E_blend.transpose(-2,-1))  # B×H×4
    
    # Sample noise and time
    noise = torch.randn_like(C_target)
    t = torch.rand(B, 1, 1)
    
    # Interpolate
    C_t = t * C_target + (1-t) * noise
    
    # Flow prediction in eigenspace
    C_pred = model.flow_head.predict_flow(C_t, t, ...)
    
    # Loss: predict the flow (C_target - noise) in eigenspace
    loss = F.mse_loss(C_pred, C_target - noise)
    return loss
```

**Key advantage**: The flow head learns to move in a **4D eigenspace** instead of 7D raw space. This space is:
- Lower dimensional (less to learn)
- More structured (PCA basis, physically meaningful)
- Less multimodal (each phase has tighter action distribution)

---

## EAS for MetaWorld MT-50

MT-50 has 50 tasks → could have 50 different eigenspaces. But we find:

**Cross-task eigenspace sharing**: Tasks with similar manipulation primitives share eigenspaces.

```
Cluster analysis of MT-50 action distributions:
  Cluster A (push/press/slide): 12 tasks — share MANIPULATE eigenspace
  Cluster B (pick/place/stack): 15 tasks — share GRASP + MANIPULATE eigenspace  
  Cluster C (open/close/turn): 11 tasks — share MANIPULATE with distinct PC3
  Cluster D (reach/touch): 8 tasks — predominantly REACH eigenspace
  Cluster E (mixed): 4 tasks — blend of A+B
```

**Solution**: Instead of 5 phases × 1 eigenspace = 5 eigenspaces, use:
**5 phases × 3 task-type eigenspaces = 15 eigenspaces**

The task type (A–E) is predicted by a **1-layer task-type classifier** conditioned on the language embedding (2M additional params).

This stays within parameter budget and dramatically improves MT-50 coverage.

---

## Key Ablations

| Ablation | Question |
|---|---|
| K=4 vs. K=7 eigencomponents | Does dimensionality reduction help or hurt? |
| EAS vs. raw 7D flow head | Is eigenspace prediction better? |
| Phase-blended vs. hard-phase eigenspace | Does soft blending matter? |
| Shared vs. task-specific eigenspaces | How much task specialization is needed? |
| EAS with PACE vs. without PACE | How much does phase routing amplify EAS? |

→ [[Ablation Plan EAS]]

---

## Prior Art That Does NOT Overlap

| Prior Work | Difference |
|---|---|
| Diffusion Policy | Predicts raw actions with full DDPM; no eigenspace |
| Flow Matching (SmolVLA, pi0) | Predicts raw 7D actions; no task-phase structure |
| TDMPC/DreamerV3 | Latent world models; different setting (not instruction-following VLA) |
| Behavior Primitives (SPiRL, OPAL) | Pre-defined skill sets; not learned eigenspaces; not end-to-end |
| **PRISM EAS** | **First to use online PCA-derived phase-specific eigenspaces as the action representation in a VLA with flow matching in the eigenspace** |

→ [[Novelty Claims & Prior Art Check]]
