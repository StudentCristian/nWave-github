---
description: "Fast-forwards through remaining waves end-to-end without stopping for review between waves."
argument-hint: '[feature-description] - Optional: --from=[discuss|design|devops|distill|deliver]'
tools:
- todo
- agent
- read/readFile
- vscode/askQuestions
- search/textSearch
---

# NW-FAST-FORWARD: Fast-Forward

**Wave**: CROSS_WAVE (entry point) | **Agent**: Main Instance (self — orchestrator) | **Command**: `/nw-fast-forward`

## Overview

Chains remaining waves end-to-end after single user confirmation. Detects current progress (like `/nw-continue`), shows planned sequence, runs each wave automatically — DISCUSS > DESIGN > DEVOPS > DISTILL > DELIVER — without stopping between waves.

You (main instance) run this orchestration directly. Each wave invoked by reading its task file.

**DISCOVER skipped by default** — requires interactive customer interview data that cannot be auto-generated. Use `--from=discover` to include.

## Behavior Flow

### Step 1: Input Parsing

Accept: feature description (new project)|`--from` flag with optional feature ID|no arguments (auto-detect from `docs/feature/`)

### Step 2: Project Resolution

**New project (description provided):** Derive feature ID per `.github/skills/common/wizard-shared-rules.md` (Feature ID Derivation). Show derived ID, allow override via #tool:vscode/askQuestions. Create `docs/feature/{feature-id}/`.

**Existing project (no description):** Scan `docs/feature/` (same as `/nw-continue` Step 1-2). If multiple, ask user to select via #tool:vscode/askQuestions.

### Step 3: Detect Current Progress

Check wave artifacts using Wave Detection Rules in `.github/skills/common/wizard-shared-rules.md`.

### Step 4: Determine Wave Sequence

Default order (DISCOVER skipped): DISCUSS > DESIGN > DEVOPS > DISTILL > DELIVER

**With `--from` flag:** Validate prerequisite artifacts exist. If missing: "Cannot start from {wave} — {missing} artifacts missing. Run `/nw-continue` to fill the gap." Start from specified wave.

**Without `--from`:** Find first incomplete wave, start from there.

### Step 5: Show Plan and Confirm

One-time confirmation via #tool:vscode/askQuestions.

### Step 6: Sequential Execution

For each wave:
1. Read task file (`.github/prompts/{wave}.md`)
2. Follow instructions — invoke appropriate agent via #tool:agent
3. Wait for completion
4. Verify output artifacts exist (wave detection rules)
5. Missing artifacts after wave = failure
6. Proceed to next wave

Between waves show brief status and continue.

### Step 7: Failure Handling

If any wave fails:
1. **Stop immediately** — do not proceed
2. Show error and suggest `/nw-continue` for manual resume
3. Do NOT retry automatically

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] Project resolved (new or existing)
- [ ] Current progress detected accurately
- [ ] Planned wave sequence shown to user
- [ ] User confirmed one-time before execution
- [ ] Each wave executed in sequence
- [ ] Output artifacts verified between waves
- [ ] Failure stops pipeline with clear error and `/nw-continue` suggestion
- [ ] Completion summary shown
