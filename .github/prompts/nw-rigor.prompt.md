---
description: "Selects a quality-vs-token-consumption profile (lean, standard, thorough, exhaustive, custom, inherit) and persists it globally (~/.nwave/global-config.json) or per-project (.nwave/des-config.json). Use when tuning how much rigor wave commands apply."
argument-hint: '[profile] - Optional: lean, standard, thorough, exhaustive, custom, inherit. Omit for interactive selection.'
tools:
- todo
- vscode/askQuestions
- read/readFile
- edit/createFile
- edit/createDirectory
---

# NW-RIGOR: Quality Profile Selection

**Wave**: CROSS_WAVE | **Agent**: Main Instance (self) | **Command**: `/nw-rigor [profile]`

## Overview

Interactive command to select a quality-vs-token-consumption profile. Persists choice to either `~/.nwave/global-config.json` (global scope) or `.nwave/des-config.json` (project scope) under the `rigor` key. All wave commands read this config to adjust agent models, review policy, TDD phases, and mutation testing.

You (the main instance) run this directly. No subagent delegation.

## Behavior Flow

### Mode Detection

- No argument -> Mode 1 (Interactive Selection)
- Argument is a preset name (lean, standard, thorough, exhaustive, inherit) -> Mode 2 (Quick Switch)
- Argument is `custom` -> Mode 3 (Custom Builder)

### Mode 1: Interactive Selection (no argument)

#### Step 1: Welcome

Read `.nwave/des-config.json`. If missing or `.nwave/` directory absent -> error: "No nWave config directory found. Run nwave install first."

If JSON is invalid -> backup as `.nwave/des-config.json.bak`, reset config to `{}`, note: "Config was corrupted. Backed up and reset."

Display current profile (from `config.rigor.profile`) or "none set" if absent.

Brief explanation of profiles and costs.

#### Step 1.5: Scope Selection

Ask via #tool:vscode/askQuestions:
```
Where do you want to save this configuration?
```
Options:
1. Globally (~/.nwave/global-config.json)
2. This project only (.nwave/des-config.json)

Store the user's choice as `{scope}` and the corresponding file path as `{target_file}`.

#### Step 2: Comparison Table

Display profiles table and allow 'custom' or 'inherit' options.

#### Step 3: User Selection

Ask user to select via #tool:vscode/askQuestions. If user selects 'custom' -> go to Mode 3. If 'inherit' -> proceed.

#### Step 4: Detail View

Show detail view for the selected profile and ask to confirm via #tool:vscode/askQuestions.

#### Step 6: Save to Config

1. If `{scope}` is global AND the directory `~/.nwave/` does not exist, create it using #tool:edit/createDirectory (parents=True)
2. Read `{target_file}` (handle missing file or corrupt JSON: start with `{}`)
3. Parse JSON
4. Set `config["rigor"]` to the full profile object and write back to `{target_file}` using #tool:edit/createFile or edit operations, preserving other keys

#### Step 7: Summary

Display resolved settings and the target file path.

### Mode 2: Quick Switch (with argument)

Validate argument, ask scope via #tool:vscode/askQuestions, show diff, confirm, then save as in Mode 1 using #tool:edit/createFile.

### Mode 3: Custom Builder

Ask a sequence of configuration questions via #tool:vscode/askQuestions (agent model, reviewer model, double review, TDD phases, refactor pass, mutation testing). After building the profile, confirm and save to `{target_file}`.

## Error Handling

| Error | Response |
|-------|----------|
| Missing `.nwave/` directory | "No nWave config directory found. Run nwave install first." |
| Invalid JSON in des-config.json | Backup as `.bak`, reset to `{}`, proceed with notice |
| Unknown profile name | "Unknown profile '{name}'. Available: lean, standard, thorough, exhaustive, custom, inherit" |
| inherit with undetectable session model | Fallback to sonnet with notice: "Could not detect session model. Defaulting agent_model to sonnet." |

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] Current profile displayed (or "none set")
- [ ] Scope question asked (global vs project) in all 3 modes
- [ ] Comparison table shown with all 5 profiles
- [ ] User selected and confirmed a profile
- [ ] Config written to `{target_file}` (read-modify-write, other keys preserved)
- [ ] `~/.nwave/` directory auto-created with `parents=True` on first global save
- [ ] Summary of all resolved settings displayed (including scope and target file path)
