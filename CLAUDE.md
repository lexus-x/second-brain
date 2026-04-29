# CLAUDE.md — Second-Brain Vault for VLA Research

## What this vault is for

This Obsidian vault is a research second-brain whose **single objective** is to identify and develop a **sub-500M-parameter Vision-Language-Action (VLA) architecture** with a **genuinely novel, Q1-defensible contribution**, then carry it through to publication.

Target venues: **IEEE T-RO** (primary), **IJRR** (secondary). RAL is a fallback only.

The user is the sole/primary author and is in **active idea-search mode** — not committed to any specific architecture. Several candidates have been proposed and most have been killed:

- **PRISM-VLA** (DVE/PACE/EAS) — dead. DVE scooped by VLA-Cache (NeurIPS 2025), ADP (ICLR 2026), VLA-Pruner. PACE underpowered. EAS used PCA-on-SO(3) which is mathematically broken.
- **STRATOS-VLA** (TPIN + nonlinear AE + ATB) — dead. Autoencoder on axis-angle has the same SO(3) double-cover problem PCA had. ATB had no formal definition.
- **PROGRESS-VLA** (continuous τ + token-MoE) — alive only as a *decision-tool null architecture*, not a Q1 thesis.
- **GAUSS-VLA** (Riemannian flow matching on SE(3) + 3-head ensemble calibration + uncertainty-driven adaptive replanning) — current strongest candidate as of 2026-04-27, but **not locked in**. May be sharpened, replaced, or merged with a better idea.

Treat all of the above as **prior art the user has already considered**, not as a committed direction. New candidates are welcome and expected.

## Operating principles (non-negotiable)

These come from explicit user direction. Apply on every research-recommendation turn.

1. **Lead with novelty, not process.** Every research-direction recommendation must open with the *unsolved problem in the field*, the *single-line novel thesis*, the *theorem to prove* or *metric to introduce*, and **head-to-head expected numbers** vs named baselines (SmolVLA, OpenVLA, π0, ACT, Diffusion Policy, RDT-1B). Decision tools and control experiments belong in a "what would force us to reconsider" section, never as the pitch.

2. **Q1-defensibility test.** Before recommending a direction, ask: *what would make a T-RO/IJRR reviewer write a positive review?* If the answer is "incremental empirical gain over a 7B baseline," it's not a Q1 thesis. Need theoretical contribution + experiment match (T-RO) or a problem-opening contribution (IJRR).

3. **Mathematical rigor.** No PCA-on-SO(3). No autoencoder-on-axis-angle. Any claim about Lie groups (SE(3), SO(3), 𝔰𝔬(3)) must be checked against double-cover, identification of charts, and metric structure. Explain group/Riemannian concepts pedagogically — user is strong on VLAs and flow matching, less explicitly demonstrated on Lie geometry.

4. **Sub-500M parameter budget.** Hard ceiling. SigLIP-400M (or whatever vision encoder) is counted *fairly* — don't hide it. State the loaded parameter count explicitly when proposing an architecture.

5. **A100 compute reality.** ~13–14 A100-days is the working ballpark for a full architecture-paper experiment plan. Flag any proposal that exceeds this. Smaller is better; if a 6-week plan needs 50 A100-days, the experimental scope is wrong.

6. **Scoop check before recommending.** Before pitching any "novel" direction, search arXiv (2024–2026), recent NeurIPS/ICLR/CoRL/RSS/ICRA/IROS, and Semantic Scholar citation graphs around named baselines. If something within 12 months looks within 1 hop of the proposed contribution, surface it explicitly — don't soft-pedal.

7. **Honest expected numbers.** Break results down by task subset where the contribution is causally attributable. Don't hide weak gains behind benchmark averages. Don't promise unrealistic dominance over 7B-parameter baselines on every task.

## How to help find the next direction

When the user asks for ideas, candidates, or critiques:

- Use the arXiv and Semantic Scholar MCPs aggressively (`claude mcp list` to confirm). For a direction to count as "novel," verify nothing within 12 months on arXiv/recent-conferences is within 1 hop.
- For library/method-implementation questions, prefer `mcp__plugin_context7_context7__*` over WebSearch (faster, more authoritative).
- For mathematical claims (theorems, metrics, convergence arguments), invoke `math-olympiad:math-olympiad` to adversarially verify the proof sketch before presenting it as a contribution.
- For figure generation in the paper draft phase, prefer the Canva MCP. For paper PDFs (final), the `anthropic-skills:pdf` and `pptx`/`docx` skills are available.
- Default to the `Explore` subagent at "quick" thoroughness for vault searches; reserve "very thorough" only when prior assumption seems wrong.
- The `mcp-registry` is available — search it if a workflow needs an MCP not yet installed (e.g., a Zotero connector).

## Vault conventions (do not break)

- **Preserve `[[wikilinks]]`** in every edit. Obsidian relies on them for the graph.
- **Daily-log pattern**: `08 - Daily Log/YYYY-MM-DD.md`. Never deviate.
- **Never edit `.obsidian/` or `.obsidian-skills/`** (config + plugin internals). The pre-tool hook also blocks this.
- **Never create `Untitled*.md` or `Untitled*.canvas`** files. The pre-tool hook blocks this. If you need a scratch file, name it properly first.
- **Vault backup commits** look like `vault backup: YYYY-MM-DD HH:MM:SS` — those are auto. Do not imitate; use real commit messages for code/doc work.
- The vault root is the working directory you're in. Folders are numbered (`01 - Research Foundations`, `02 - Novel Architecture`, `04 - Literature Review`, `05 - Experiments`, `06 - Real World Deployment`, `07 - Paper Draft`, `08 - Daily Log`, `09 - Resources`, `10 - Code & Implementation`).

## Token-efficiency defaults

- Don't write planning, summary, or "what I just did" docs unless the user asks. Conversation context + git diff is enough.
- Don't re-explain GAUSS/PRISM/STRATOS history every turn — it's encoded here and in memory; reference, don't re-derive.
- Use parallel tool calls for independent reads.
- Prefer Read/Glob/Grep over Bash for file ops.
- Memory is canonical for cross-session facts (`~/.claude/projects/.../memory/`). Update it when the project state changes (new candidate alive, candidate killed, target venue shifts), prune it when entries go stale.

## When in doubt

Ask. The user prefers a direct clarifying question over a confidently-wrong recommendation. Two acceptable closers when uncertain: "should I scan arXiv for X first?" and "is the budget closer to 200M or 500M for this candidate?" — both are cheap and sharpen the next turn.
