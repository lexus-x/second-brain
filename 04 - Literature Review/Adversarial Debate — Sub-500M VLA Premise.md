---
title: Adversarial Debate — Sub-500M VLA Premise
tags:
  - debate
  - adversarial
  - critique
  - strategy
  - openwolf
  - critic
date: 2026-04-27
aliases:
  - Sub-500M Debate
  - Three-Voice Debate
  - PROGRESS-VLA Counter
cssclasses:
  - critique
---

# 🥊 Adversarial Debate: Is the Sub-500M VLA Bet Worth Taking?

> [!important] Why this doc exists
> The [[PRISM-VLA Brutal Critique & Redesign]] (2026-04-27) was a tactical autopsy: it killed DVE, weakened PACE, and exposed PCA-on-SO(3) as unsound — then prescribed a STRATOS-VLA pivot. But it never questioned the **strategic premise**: that <500M params + LIBERO-99% + MT-50-80% is the right race to enter at all. This doc argues that question from three voices, then proposes a concrete competing architecture (**PROGRESS-VLA**) so the choice between commitments is on paper, not in your head.

**The three voices**

- 🐺 **Openwolf** — adversarial reviewer, AC-from-hell tone. No concessions. Goal: get this paper desk-rejected.
- 🧐 **Critic** — measured reviewer-2. Will concede when forced; demands experiments where claims are unbacked.
- 🛠 **Counter-Proposer** *(me)* — defending **PROGRESS-VLA**, a phase-free continuous alternative.

**Stakes**: which architecture gets the next ~6 weeks of implementation effort. Stay STRATOS, pivot PROGRESS, or hybrid (continuous τ feeding STRATOS's existing components).

---

## § 1. Openwolf opens — "The sub-500M bet is vanity"

🐺 *Five attacks on the strategic premise. None of them are about DVE/PACE/EAS — that ground is already burnt.*

**(a) Sub-500M is a self-imposed handicap.** Look at the field: RT-2 (55B), π0 (3.3B), RDT-1B (1B), OpenVLA (7B). The trajectory is clearly *up*. Choosing to play "smallest mediocre model" is the loser's bracket. The prize for winning sub-500M is being cited as a footnote in the next 7B paper that cleanly beats you on every metric. Where's the publication target where this matters? On-device deployment? Show me the deployment paper, not a benchmark paper.

**(b) LIBERO-99% is a memorization trophy and you already know it.** The [[PRISM-VLA Brutal Critique & Redesign|Brutal Critique]] line 110 literally says *"the community has known since 2025 that standard LIBERO is a saturated benchmark."* Yet [[LIBERO Benchmark Strategy]] still puts 99% as the headline target. Reporting this is reviewer-bait. AC reads "LIBERO 99%" and immediately asks why LIBERO-PRO is buried.

**(c) MT-50-80% has no anchor.** [[MetaWorld MT-50 Strategy]] says *"SmolVLA: ~55–62% (estimated) — Must verify by running SmolVLA on MT-50 as our baseline."* You haven't run the baseline. You have a target without a starting point. The arithmetic in line 159–165 ("DVE +5, PACE +8, EAS +5, LoRA +5 = 81%") is **additive guessing on an unmeasured base**. This is not a research plan, this is a roulette wheel with the numbers written on it.

**(d) Phases are 1990s robotics in transformer clothing.** Brutal Critique line 75: "1990s-era robot state machine logic relabeled as 'self-supervised.'" The field abandoned hand-crafted phase machines for end-to-end learning twenty years ago. STRATOS's TPIN learns phases instead of hard-coding them — fine — but it still **assumes the right number of phases is K=5**, that phases are discrete, and that they form a deterministic sequence. Manipulation isn't a finite-state machine. It's a continuous control problem with hierarchical structure that doesn't tile cleanly.

**(e) Your parameter accounting is unverified.** Brutal Critique #5 admits this. Until you verify whether SmolVLA's reported 450M includes its vision encoder, every comparison table in [[Parameter Budget Analysis]] is one footnote away from collapse. Today the comparison might be PRISM-525M-vs-SmolVLA-364M (you lose) or PRISM-439M-vs-SmolVLA-450M (you win). You're publishing a sub-500M claim without knowing which.

---

## § 2. Critic responds — measured defense

🧐 *Concedes more than you'd hope, but salvages a defensible core.*

**On (a) — sub-500M handicap**: The defense isn't "smallest mediocre"; it's **"largest deployable on $200 hardware."** Reframe the contribution narratively: not capability-vs-7B, but capability-per-FLOP-per-watt. Cite Jetson Nano / Orin spec ceilings. Position the work in the **on-device VLA literature** (where SmolVLA already lives), not the absolute-SOTA literature (where π0 lives). Under that frame, sub-500M is the entry ticket, not the handicap.

**On (b) — LIBERO saturation**: Conceded. The Brutal Critique is right; doubling down here is denial. **Demote LIBERO to secondary** and put **LIBERO-PRO as the primary metric**. Standard LIBERO is reported only as a sanity check that the model isn't *worse* than baseline on the saturated benchmark. The [[LIBERO Benchmark Strategy]] doc needs revision.

**On (c) — MT-50 has no baseline**: Conceded and **fixable in one day**. Run SmolVLA-450M on MT-50 with the standard MetaWorld eval harness. Get the actual number. Until then, every "+8% from PACE" claim is fiction.

**On (d) — phase discreteness**: This is the deepest attack and I won't fully concede. Discrete phases have empirical support in **short-horizon pick-and-place** — ALOHA, ACT, Diffusion Policy all observe sub-trajectory clustering. But on **long-horizon multi-step** (LIBERO-Long, MT-50 Group E), discreteness almost certainly breaks. The right empirical question is: *does TPIN's learned changepoint detection produce phase boundaries that are consistent across episodes for the same task?* If yes, phases carve nature. If no, Openwolf wins this round.

**On (e) — parameter accounting**: One afternoon's work to settle. Read SmolVLA's config, count its parameters, report. Stop publishing tables until that's done.

---

## § 3. Counter-Proposer — PROGRESS-VLA

🛠 *A concrete alternative that attacks the discrete-phase assumption directly.*

**Core idea**: replace the entire phase-conditioning machinery (PACE, TPIN, PCA-eigenspaces) with a single **continuous task-progress scalar τ ∈ [0, 1]** plus **token-level mixture-of-experts** in the upstream LM cross-attention.

### Architecture

**(1) Task-progress regression head.** A 0.5M-param MLP that takes (proprioception, language embedding, last-K visual residual norms) and predicts τ ∈ [0, 1]. Trained with a single supervision signal: *fraction of episode elapsed at success-conditioned timesteps* (only successful demos count). At inference, τ is the model's belief about how far through the task it is.

**(2) Token-level Mixture-of-Experts on the cross-attention FFN.** Replace the FFN in K=2 cross-attention layers (chosen by ablation) with a 4-expert MoE. Top-1 routing, capacity factor 1.25. **Router input is (τ, language_embedding_mean, layer_index)**. Each expert is ~7.5M params; total loaded ~30M, active per-token ~7.5M. Routing follows Switch Transformer (Fedus et al. 2022, [arXiv:2101.03961](https://arxiv.org/abs/2101.03961)) and the simpler-than-Mixtral routing formulation.

**(3) Single shared flow-matching action head.** Reuse the EAS flow-matching transformer from [[Eigenspace Action Synthesis (EAS)]] **but drop the eigenspace decomposition entirely**. Predict raw 7D actions (with rotations in 6D-rotation parameterization, Zhou et al. 2019, [arXiv:1812.07035](https://arxiv.org/abs/1812.07035)) conditioned on (backbone_hidden, proprio, τ, language).

### Why this is the right attack on STRATOS

STRATOS's three components — EAS, TPIN, ATB — are **all conditioned on phase**. If phases don't carve manipulation cleanly (Openwolf's attack (d), and Critic's open empirical question), the same flaw propagates through every component. PROGRESS-VLA is the **null hypothesis architecture for the phase question**: if continuous τ + MoE matches STRATOS on LIBERO-Long, the entire phase-conditioning research program is over-engineered.

### Parameter budget

| Component | Loaded | Active/token |
|---|---|---|
| SmolVLM-2 backbone (frozen, 16 layers) | 256M | 256M |
| LoRA (r=16) on backbone | 3M | 3M |
| τ regression head | 0.5M | 0.5M |
| 2× MoE layers, 4 experts × 7.5M | 60M | 15M |
| MoE routers (2 layers) | 0.1M | 0.1M |
| Flow-matching action head (no eigenspace) | 65M | 65M |
| SigLIP vision encoder (frozen, *fairly counted*) | 86M | 86M |
| **Total** | **470.6M** ✅ | **425.6M** |

Under 500M loaded **with SigLIP fairly counted** — the accounting Openwolf attacked.

### Reuses from existing vault work

- SmolVLM-2 backbone and frozen-layer choice from [[SmolVLA Paper Notes]]
- Flow-matching head from [[Eigenspace Action Synthesis (EAS)]] (with eigenspace stripped out)
- LoRA configuration from [[Parameter Budget Analysis]]
- Training data pipeline from [[LIBERO Benchmark Strategy]] and [[MetaWorld MT-50 Strategy]]

### Targets

Same numbers as STRATOS — **LIBERO-Long ≥85% (primary), LIBERO-PRO ≥80% (primary), MT-50 ≥75% (primary), standard LIBERO ≥95% (sanity)** — but the *headline empirical claim* changes: not "phases help" but **"continuous task-progress + sparse experts matches or beats discrete-phase architectures with simpler training and fewer assumptions."**

---

## § 4. Openwolf attacks PROGRESS-VLA

🐺 *Now you're the target.*

**(i) Your τ is regression on episode position. A linear baseline scoops you.** "Fraction of episode elapsed at success-conditioned timesteps" reduces, in expectation, to roughly *t/T_episode*. A single-parameter linear baseline (predict τ = t/T from a running counter) beats nothing because there's nothing there. Either show that learned τ deviates non-trivially from the trivial t/T baseline, or admit you're conditioning on a clock.

**(ii) MoE smuggles parameters back in through the side door.** You loaded 60M for experts and call 15M "active." Memory bandwidth doesn't care. On a Jetson Nano you load all 60M into VRAM at startup. The "active per token" framing is a paper trick that disappears the second a deployment engineer runs `nvidia-smi`. Your real footprint is 470M loaded; your "deployment story" defense in § 2 just lost half its leverage.

**(iii) You're proposing two architectures on a project that hasn't run a single experiment.** STRATOS is unimplemented. PROGRESS is unimplemented. The user owes the reviewer one architecture done well, not two architectures sketched. Scope explosion is a 2026 paper killer.

**(iv) MoE on cross-attention is a known-fragile recipe at this scale.** Switch Transformer worked at 1.6T parameters with thousands of experts. At 30M loaded across 4 experts, the routing decisions are noisier than the experts themselves. Cite literature where MoE works at <100M scale for vision-language. (You can't — it's mostly negative results.)

---

## § 5. Critic attacks PROGRESS-VLA

🧐 *More patient, but cuts deeper.*

**(i) Where's your evidence continuous τ generalizes better than discrete phases?** PROGRESS-VLA's central claim is *phases-are-too-coarse*. The proper baseline isn't STRATOS — it's **STRATOS with K=10 phases instead of K=5**, or **STRATOS with soft phases (continuous mixture)**. If those interpolations close the gap, your contribution collapses to "phases should be soft," which is a 2-page workshop paper, not a thesis.

**(ii) Wrong baseline triangle.** You frame yourself against STRATOS. But [Diffusion Policy](https://arxiv.org/abs/2303.04137) (Chi et al. 2023), [ACT](https://arxiv.org/abs/2304.13705) (Zhao et al. 2023), and [RDT-1B](https://arxiv.org/abs/2410.07864) (Liu et al. 2024) all do **phase-free chunked action prediction** without MoE and without τ. They are your real baselines. If RDT-1B at 1B params hits your MT-50 target with no phase machinery, why is your 470M complication interesting?

**(iii) τ supervised by "fraction of successful episode elapsed" is leaky.** At test time, T_episode is unknown — you don't know how long the episode will be when you start. The supervision uses *retrospective* T (post-hoc). The model at inference will have to estimate T from features it doesn't have access to during the training of τ. This is a train/test distribution mismatch dressed up as self-supervision.

**(iv) MoE on action-relevant FFN layers is principled, but you didn't justify K=2 or K=4.** Why two MoE layers and not one? Why four experts and not eight? Show the ablation budget. Otherwise this is hyperparameter aesthetics.

---

## § 6. Counter-Proposer rebuttal

🛠 *Concede where the critique lands, defend where it doesn't.*

**Concede Critic (i)**: PROGRESS-VLA's correct baseline is **STRATOS with K∈{5,10} and soft-vs-hard phase routing** as ablations *within the same paper*. The contribution then becomes: across phase granularities, continuous τ+MoE is no worse than the best phase setting and is **simpler to train** (no changepoint loss, no per-phase AE pretrain). This is a valid contribution even if numerical gains are modest.

**Concede Critic (iii)**: The τ supervision *is* leaky. Fix: train τ regression with a **causal masking scheme** — at training time, only show the model features available up to time t (no future leakage), and supervise τ_t against `min(t/T_train, 1.0)` as a soft target with a regression loss that's tolerant to the mismatch (Huber, not MSE). At inference, τ is bootstrapped from a small calibration window at episode start.

**Defend against Openwolf (i)**: Yes, τ approximates t/T in the trivial limit. The point is **what the model conditions on**, not whether τ is information-theoretically novel. The MoE router uses (τ, language_mean, layer_index) — τ is the *time-varying* signal that lets routing change as the task progresses. A clock counter lacks the language-conditioning composition. Show a head-to-head: τ-MoE vs. clock-counter-MoE.

**Push back on Openwolf (ii)**: Memory-bandwidth criticism cuts *both* architectures. STRATOS loads 5 phase-specific autoencoders and a hypernetwork; PROGRESS loads 4 experts. Both are 50–70M of "we hope sparsity helps." Whichever architecture wins should win on a deployment-fair benchmark (peak VRAM, latency on Jetson Orin), not on parameter count alone. Add a deployment column to the comparison tables.

**Reframe scope (Openwolf iii)**: PROGRESS-VLA is presented in this debate as a **lower-bound architecture**. The recommended path forward is: implement PROGRESS first (it's strictly simpler than STRATOS), use it as the null architecture, and only build STRATOS components if PROGRESS underperforms. This is one architecture done first, not two architectures sketched.

---

## § 7. Openwolf attacks STRATOS

🐺 *Equal-opportunity demolition.*

**(i) ATB's "action-uncertainty feedback loop" is vibes until you write the equation.** [[PRISM-VLA Brutal Critique & Redesign]] line 213 says *"if the model's action variance is low (confident) → use fewer tokens."* Variance of *what*? The flow-matching trajectory at integration step k? The marginal distribution at t=1? KL between consecutive timesteps? Calibration error against held-out validation? Each definition has different failure modes. Without a formal definition, ATB is a story about active inference that no reviewer will let you publish. Show me the equation in a table by next week or kill the component.

**(ii) Five nonlinear AEs trained per-phase = five places to overfit.** STRATOS's revised EAS (line 187–193) trains a separate 0.5M autoencoder per phase. Per-phase training data is **smaller than the full dataset by definition**. With ~2,000 LIBERO episodes split across 5 phases, each phase has ~400 episodes worth of action samples — easily memorizable for a 0.5M-parameter AE. You'll see beautiful per-phase reconstruction loss and catastrophic generalization. The PCA-on-SO(3) problem you fled doesn't go away just because you wrote `nn.Linear` instead of `np.linalg.svd`.

**(iii) TPIN's "hypernetwork in 5M params" is a single-layer projection in disguise.** Brutal Critique line 201 says TPIN uses *"phase-conditioned hypernetworks that generate the flow matching head's final projection weights (~3M params)."* A hypernetwork that outputs weights for a 65M flow head, parameterized in 3–5M, is at most a low-rank update factored across phases. Call it what it is: **per-phase LoRA on the action head**. That's a fine technique, but it's not "novel feedback loop"-grade.

**(iv) The PCA→AE pivot doesn't fix the SO(3) problem you flagged.** You cited Brutal Critique line 92: *"averaging rotation PCA bases is mathematically ill-defined."* Your fix: replace PCA with autoencoders in **axis-angle space**. Axis-angle is a 2-cover of SO(3) (two distinct axis-angle vectors map to the same rotation), and MSE loss in axis-angle has the same topology problem PCA has — discontinuities at antipodal points. You waved a wand and pretended the manifold became flat. **Use 6D-rotation (Zhou et al. 2019) or quaternions with double-cover correction**, or you're shipping the same bug under new branding.

**(v) "EAS preserved as your strongest contribution" is sunk-cost.** The Brutal Critique killed everything except EAS, then preserved EAS as the survivor. But the survivors of a triage aren't necessarily strong — they're just less-killed. Reapply the same standard you applied to DVE: *what's the closest published prior art, and how do you compare?* Latent action models (e.g., LAPA, OpenVLA-OFT-style action tokenization) and behavior primitives (SPiRL, OPAL — already listed in [[Eigenspace Action Synthesis (EAS)]] line 224) all do "structured action latent + flow/diffusion in latent space." Whether *phase-specific* latent spaces are sufficiently different from *task-conditioned* latent spaces is an empirical question, not a self-evident novelty.

---

## § 8. Synthesis & Verdict

### Where all three voices agree

1. **Sub-500M needs a deployment story, not a capability story.** Reframe the publication as *largest VLA deployable on $200 hardware*, with peak-VRAM and Jetson-Orin latency as headline numbers alongside success rates.
2. **Standard LIBERO must be demoted; LIBERO-PRO becomes primary.** Both the [[LIBERO Benchmark Strategy]] and [[Parameter Budget Analysis]] tables need revision before any public claim.
3. **SO(3) representation must be 6D-rotation (Zhou 2019) or quaternion with double-cover handling** — *regardless of which architecture wins*. Axis-angle MSE is broken in both PCA-EAS and AE-EAS.
4. **Run the SmolVLA MT-50 baseline before claiming any improvement number.** One day of compute resolves a category of attacks.
5. **Verify SmolVLA's parameter accounting methodology before publishing any comparison table.** One afternoon resolves Openwolf's attack (e).

### Where PROGRESS-VLA wins

- Simpler ablation story (one continuous variable vs. K phases × hypernetwork × per-phase AE)
- Fewer training stages (1 stage vs. STRATOS's 2 vs. original PRISM's 5)
- Directly tests the discrete-phase assumption that all of STRATOS depends on
- 6D-rotation flow head is naturally compatible with no eigenspace decomposition

### Where STRATOS-VLA wins

- More committed paper narrative if it works ("phase-aware everything" is a story; "continuous τ + MoE" is a technique)
- TPIN's learned changepoint detection is a genuinely novel piece if the phase boundaries it discovers are consistent across episodes
- ATB's perception-action feedback loop, **if formalized**, has no precedent in VLA literature
- The vault has 6 weeks of design work invested in STRATOS; pivoting again resets that

### Three open empirical questions that resolve the debate

1. **Does τ-regression carry information beyond t/T_episode?** Train both, condition MoE routing on each, compare LIBERO-Long success rates. ~1 day of compute.
2. **Do TPIN's learned phase boundaries agree across episodes for the same task?** Train TPIN, run on held-out same-task episodes, compute boundary-time variance. If σ > ~10% of episode length, phase-conditioning is conditioning on noise. ~2 days.
3. **What does the null architecture get?** SmolVLA + 6D-rotation flow-matching head + no phase / progress conditioning. Train on LIBERO-Long. If this hits ≥90%, **both STRATOS and PROGRESS are over-engineered** and the right paper is a 4-page note about action-rotation parameterization. ~1 day.

### Recommended decisive 1-day experiment

**Question 3 above is the highest-leverage bet.** It's a one-day experiment whose outcome forecloses or unlocks ~6 weeks of architecture work in either direction:

- Null hits ≥90% on LIBERO-Long → write the parameterization-and-deployment paper, skip phase research entirely.
- Null hits 80–89% → there's room for phase/progress mechanisms; PROGRESS-VLA is the next experiment.
- Null hits <80% → both PROGRESS and STRATOS are needed; build PROGRESS first because it's simpler.

---

## § 9. Verdict

**Recommendation**: **Do not commit to STRATOS yet.** Run the null-architecture experiment (§ 8 question 3) first. Pivot to PROGRESS-VLA as the *first* architecture beyond null, because PROGRESS is strictly simpler than STRATOS and tests the phase assumption that STRATOS *depends on*. Reserve STRATOS for the case where PROGRESS underperforms by ≥3 points on LIBERO-Long after a fair training budget — at which point STRATOS's added complexity has a measured price tag.

**Conditions that flip this recommendation**:

- Null architecture hits ≥90% on LIBERO-Long → both STRATOS and PROGRESS are over-engineered; write the deployment-and-parameterization paper instead.
- TPIN boundary-consistency variance σ < 5% of episode length on held-out same-task episodes → phases carve nature; STRATOS's phase machinery is justified, build STRATOS.
- SmolVLA-MT-50 baseline comes in below 50% → the field's hardest benchmark has more headroom than current numbers suggest; both architectures are scientifically interesting and the hybrid (τ-conditioned STRATOS components) becomes the strongest paper.

**Update protocol**: When any of the three open empirical questions resolves, append the result to this doc and update the verdict. The debate isn't over — it's paused on data.

---

## Cross-References

- Tactical autopsy that this debate builds on: [[PRISM-VLA Brutal Critique & Redesign]]
- Original strategic frame being challenged: [[The Core Scientific Insight]], [[Why VLAs Fail — Problem Space Analysis]]
- Architecture details cited in attacks: [[PRISM-VLA Architecture Overview]], [[Differential Visual Encoding (DVE)]], [[Phase-Aware Cross-Attention Engine (PACE)]], [[Eigenspace Action Synthesis (EAS)]]
- Parameter accounting under dispute: [[Parameter Budget Analysis]]
- Benchmark targets being reframed: [[LIBERO Benchmark Strategy]], [[MetaWorld MT-50 Strategy]]
- Baseline being compared against: [[SmolVLA Paper Notes]]
- MOC: [[VLA Research Hub]]
