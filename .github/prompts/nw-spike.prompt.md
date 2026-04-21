---
description: "Runs a timeboxed spike to validate one core assumption before DESIGN. Use after DISCUSS when the feature involves a new mechanism, performance requirement, or external integration."
argument-hint: '[feature-description] - Example: "wave-matrix -- derive feature status from pytest + filesystem"'
tools:
- todo
- agent
- read/readFile
- execute/runInTerminal
---

# NW-SPIKE: Timeboxed Assumption Validation

**Wave**: SPIKE (between DISCUSS and DESIGN) | **Agent**: Attila (nw-software-crafter) | **Command**: `/nw-spike`

## Overview

Execute a timeboxed spike (max 1 hour) to validate a single core assumption before investing in architecture design. Produces throwaway code and permanent findings. The spike answers: does the mechanism work, does it meet the performance budget, and what did we assume wrong?

## Skip Check

Before running, verify the spike is needed. If ALL answers are "no", skip and proceed to DESIGN:

1. Is there a new mechanism never tried before in this codebase?
2. Is there a performance requirement that cannot be validated by reasoning alone?
3. Is there an external integration with unknown behavior?

If skipping: tell the user and recommend `/nw-design` directly.

## Prior Wave Consultation

1. **DISCUSS artifacts**: Read `docs/feature/{feature-id}/discuss/` (required)
   - `user-stories.md` -- scope and acceptance criteria
   - `wave-decisions.md` -- constraints and assumptions to test
2. **DIVERGE artifacts**: Read `docs/feature/{feature-id}/diverge/recommendation.md` (if present)

## Interactive Decision Points

### Decision 1: Spike Scope
**Question**: What is the ONE assumption you need to validate?
**Examples**:
1. "Can we parse pytest output reliably in <5 seconds?"
2. "Can the CEL library evaluate 100 expressions in <1 second?"
3. "Can we write to .git/hooks/ from a subprocess without corruption?"

### Decision 2: Performance Budget
**Question**: What is the timing constraint? (Enter "none" if mechanism validation only)
**Examples**:
1. "<5 seconds end-to-end"
2. "<100ms per operation"
3. "Handle 10K items without OOM"

## Agent Invocation

@nw-software-crafter

**SKILL_LOADING**: Before starting, load your spike methodology skill at `.github/skills/nw-spike-methodology/SKILL.md` using #tool:read/readFile.

Execute spike for "{feature-description}".

**Spike question**: {Decision 1 answer}
**Performance budget**: {Decision 2 answer}

**Rules**:
- Code goes in `/tmp/spike_{feature_id}/`. Never in `src/`.
- Max 1 hour. No tests, no types, no error handling, no abstractions.
- One file preferred. Two files maximum.
- Use `time.perf_counter()` for timing.
- Print results to stdout.

**After spike completes**:
1. Write findings to `docs/feature/{feature-id}/spike/findings.md`
2. Delete the spike code from `/tmp/`
3. Report the binary verdict: WORKS or DOESN'T WORK

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes.

## Success Criteria

- [ ] Exactly one assumption tested (not two, not zero)
- [ ] Spike code lives in `/tmp/`, never in `src/`
- [ ] Completed within 1 hour (or escalated with "BIGGER THAN EXPECTED")
- [ ] `findings.md` written with binary verdict, timing, and edge cases
- [ ] Spike code deleted after findings written
- [ ] Design implications documented (what was assumed wrong)

## Next Wave

**Handoff To**: nw-solution-architect (DESIGN wave)
**Deliverables**: `docs/feature/{feature-id}/spike/findings.md`
**Design reads findings before starting** -- spike results override any prior assumptions.
