---
description: "Bug fix workflow: root cause analysis → user review → regression test + fix via TDD"
argument-hint: '[bug-description] - Describe the defect observed'
tools:
- todo
- agent
---

# NW-BUGFIX: Defect Resolution Workflow

**Wave**: CROSS_WAVE
**Agents**: Rex (nw-troubleshooter) → selected crafter (OOP or FP per project paradigm)

## Overview

End-to-end bug fix pipeline: diagnose root cause, review findings with user, then deliver regression tests that fail with the bug and pass with the fix. Ensures every defect produces a test that prevents recurrence.

## Flow

```
INPUT: "{bug-description}"
  │
  ├─ Phase 1: Root Cause Analysis (@nw-troubleshooter)
  │   └─ /nw-root-why "{bug-description}"
  │   └─ Output: RCA document with root cause chain + fix proposal
  │
  ├─ Phase 2: User Review (INTERACTIVE — STOP here)
  │   └─ Present RCA findings to user
  │   └─ User confirms root cause + approves fix direction
  │   └─ If user rejects → refine RCA or stop
  │
  └─ Phase 3: Regression Test + Fix (via /nw-deliver)
      └─ /nw-deliver "fix-{bug-id}" with bug-fix scope
      └─ Paradigm detection determines crafter (OOP or FP)
      └─ Roadmap: regression test (RED) → fix (GREEN) → verify (COMMIT)
```

## Execution Steps

### Phase 1: Root Cause Analysis

**Skill loading**: The troubleshooter loads its skills from `.github/skills/nw-{skill}/SKILL.md`:
- `nw-five-whys-methodology` — core investigation methodology
- `nw-investigation-techniques` — systematic debugging patterns
- `nw-post-mortem-framework` — structured incident analysis

Invoke @nw-troubleshooter via #tool:agent:

```
Execute *investigate-root-cause for the following defect:

{bug-description}

Configuration:
- investigation_depth: 5
- multi_causal: true
- evidence_required: true

Produce:
1. Root cause chain (5 Whys with evidence at each level)
2. Contributing factors
3. Proposed fix with specific code changes
4. Files affected
5. Risk assessment of the fix
```

After the troubleshooter returns, present findings to the user. Include:
- Root cause summary (1-2 sentences)
- Evidence chain
- Proposed fix
- Files to modify
- Risk level

**STOP and wait for user confirmation before proceeding to Phase 3.**

### Phase 2: User Review

Present the RCA findings and ask:
1. "Does this root cause match your understanding?"
2. "Do you approve the proposed fix direction?"
3. "Any additional constraints or context?"

If user rejects:
- Refine the RCA with additional context
- Or stop the workflow entirely

If user approves → proceed to Phase 3.

### Phase 3: Regression Test + Fix (via /nw-deliver)

This phase delegates entirely to `/nw-deliver`, which handles:
- Paradigm detection (reads project .github/copilot-instructions.md for `## Development Paradigm`)
- Crafter selection (@nw-software-crafter for OOP, @nw-functional-software-crafter for FP)
- DES enforcement with proper markers
- Rigor profile from `.nwave/des-config.json`

**Preparation before invoking /nw-deliver:**

1. Derive feature-id: `fix-{kebab-case-bug-summary}` (max 5 words)
2. Create `docs/feature/{feature-id}/deliver/` directory
3. Prepare RCA context from Phase 1 output (root cause, files affected, proposed fix)

**Invoke /nw-deliver with bug-fix scope:**

```
/nw-deliver "fix-{bug-summary}"
```

The deliver orchestrator creates a minimal roadmap with 2 steps:

**Step 01-01: Regression test (RED)**
- Write a test that reproduces the exact defect
- Test MUST fail against current code (proves the bug exists)
- Test location: `tests/regression/{component}/` or `tests/bugs/`
- Test name: `test_bug_{description}.py`

**Step 01-02: Fix implementation (GREEN)**
- Implement the minimal fix identified in RCA
- Run ALL tests — regression test must now PASS
- Existing tests must not regress

The crafter handles the 5-phase TDD cycle (PREPARE → RED → GREEN → COMMIT) with DES monitoring.

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] Root cause identified with evidence at each causal level
- [ ] User reviewed and approved fix direction
- [ ] Regression test written that fails with the bug
- [ ] Fix implemented that makes the regression test pass
- [ ] All existing tests still pass (no regressions)
- [ ] Commit with conventional message: `fix(scope): description`
