---
description: "Guided wizard to start a new feature. Asks what you want to build, recommends the right starting wave, and launches it."
argument-hint: '[feature-description] - Example: "Add rate limiting to the API gateway"'
tools:
- todo
- agent
- read/readFile
- vscode/askQuestions
- edit/createDirectory
---

# NW-NEW: Start a New Feature

**Wave**: CROSS_WAVE (entry point)
**Agent**: Main Instance (self — wizard)
**Command**: `/nw-new`

## Overview

Conversational wizard that asks the user to describe their feature|classifies it|recommends a starting wave|launches it. Eliminates need to understand the 6-wave pipeline before using nWave.

You (the main instance) run this wizard directly. No subagent delegation.

## Behavior Flow

### Step 1: Feature Description Intake

Ask the user to describe what they want to build. If provided as argument, use that. Use #tool:vscode/askQuestions for interactive prompts.

Do NOT proceed until you have a clear, actionable description.

### Step 2: Feature ID Derivation

Derive feature ID per rules in `.github/skills/common/wizard-shared-rules.md` (section: Feature ID Derivation).

Show derived ID via #tool:vscode/askQuestions. Allow override with custom value.

### Step 3: Name Conflict Check

Check if `docs/feature/{feature-id}/` exists. If so, offer via #tool:vscode/askQuestions:
1. **Continue that project** — switch to `/nw-continue`
2. **Start fresh with different name** — ask for distinguishing name
3. **Archive and restart** — move to `docs/feature/{feature-id}-archived-{date}/`

### Step 4: Clarifying Questions

Use #tool:vscode/askQuestions for clarifying Q1/Q2 (new vs existing behavior, requirements readiness).

### Step 5: Feature Classification

Based on description and answers, classify and show classification for user confirmation.

### Step 6: Greenfield vs Brownfield Detection

Scan filesystem (search/textSearch) to detect `src/`, existing `docs/feature/`, and test directories.

### Step 7: Wave Recommendation

Decision tree maps description and artifacts to a recommended starting wave. Show recommendation with rationale via #tool:vscode/askQuestions.

### Step 8: Launch

After user confirms, create project directory using #tool:edit/createDirectory if needed and invoke the recommended wave by reading its task file and dispatching via #tool:agent, passing feature ID as argument.

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] User described feature in plain language
- [ ] Project ID derived and confirmed by user
- [ ] No name conflicts (or resolved)
- [ ] Feature classified by type
- [ ] Starting wave recommended with rationale
- [ ] User confirmed recommendation
- [ ] Wave command launched with correct feature ID
