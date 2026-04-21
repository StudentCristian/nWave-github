---
description: "Creates E2E acceptance tests in Given-When-Then format from requirements and architecture. Use when preparing executable specifications before implementation."
argument-hint: "[story-id] - Optional: --test-framework=[cucumber|specflow|pytest-bdd] --integration=[real-services|mocks]"
tools:
- todo
- agent
- read/readFile
- execute/runInTerminal
- edit/createFile
---

# NW-DISTILL: Acceptance Test Creation and Business Validation

**Wave**: DISTILL (wave 5 of 6) | **Agent**: Quinn (nw-acceptance-designer)

## Overview

Orchestrate acceptance test creation from prior wave artifacts, then gate the result through parallel reviews before handoff to DELIVER. You (main instance) are the orchestrator. You dispatch agents and enforce gates.

## REVIEW GATE SUMMARY (read this first)

After the acceptance designer produces scenarios, you MUST dispatch 3 parallel reviewers if scenario count exceeds 3. This is the single most important orchestration step in DISTILL. The procedure is: dispatch designer -> count scenarios -> dispatch 3 reviewers in parallel -> AND-gate results -> handoff. Details in Phase 3 below.

## Phase 1: Decisions and Context

### Interactive Decision Points

... (Decision 1-4 content retained)

### Prior Wave Consultation

DISTILL is the conjunction point — it reads all three SSOT dimensions plus the feature delta.

**SSOT (all three dimensions):**
1. **Journeys** (behavior): Read `docs/product/journeys/{name}.yaml` — extract embedded Gherkin as starting scenarios, identify integration checkpoints and failure_modes
2. **Architecture** (structure): Read `docs/product/architecture/brief.md` — identify driving ports (from `## For Acceptance Designer` section) for port-entry test scenarios
3. **KPI contracts** (observability): Read `docs/product/kpi-contracts.yaml` — identify which behaviors need `@kpi` tagged scenarios (soft gate — warn if missing, proceed)

**Feature delta:**
4. **DISCUSS**: Read from `docs/feature/{feature-id}/discuss/`:
   - `user-stories.md` (scope boundary — generate tests for THIS feature's stories only) | `story-map.md` | `wave-decisions.md`
5. **DEVOPS** (test environment): Read from `docs/feature/{feature-id}/devops/`:
   - `platform-architecture.md` | `ci-cd-pipeline.md` | `wave-decisions.md`

**Scope rule**: DISTILL generates tests for the behaviors described in `user-stories.md`, not for the entire SSOT. The SSOT provides context (which port to enter through, which KPI to verify) but the scope is bounded by the feature delta.

**READING ENFORCEMENT**: Read every file above using #tool:read/readFile. Output confirmation checklist (`+ {file}` for each read, `- {file} (not found)` for missing). Do NOT skip files that exist.

## Phase 2: Dispatch Acceptance Designer

Invoke the acceptance designer via #tool:agent (nw-acceptance-designer) and include all prior wave context and configuration.

**Prompt must include:**
- All prior wave context read in Phase 1
- Decisions 1-4 configuration
- Instruction to load skills at `.github/skills/nw-{skill-name}/SKILL.md`

**Configuration:**
- model: rigor.agent_model (omit if "inherit")
- test_type: {Decision 1} | test_framework: {Decision 2}
- integration_approach: {Decision 3} | infrastructure_testing: {Decision 4}
- interactive: moderate | output_format: gherkin

**After the agent returns**: Count the total scenarios produced. Store this number. You need it for Phase 3.

## Phase 3: TRIPLE REVIEW GATE (mandatory orchestrator action)

This phase determines whether the acceptance tests are ready for DELIVER handoff. You MUST execute this phase. There is no path to Phase 5 (Handoff) that bypasses this gate.

### Step 3.1: Count scenarios

Count total scenarios across all `.feature` files produced by the acceptance designer. Store the count.

### Step 3.2: Fast-path (3 or fewer scenarios)

If total scenarios <= 3:
1. Skip the triple review. Run ONE acceptance-designer review pass only:
   - Dispatch `@nw-acceptance-designer-reviewer` with the feature files using #tool:agent
2. Run behavioral smoke test via #tool:execute/runInTerminal:
   ```bash
   pipenv run pytest tests/acceptance/{feature-id}/ -v --tb=short -x
   ```
   First scenario MUST fail for a business logic reason (not import error, not missing fixture).
3. Proceed to Phase 4.

### Step 3.3: Triple review (more than 3 scenarios)

If total scenarios > 3, DISPATCH ALL THREE REVIEWERS IN PARALLEL using #tool:agent three times in the same orchestration response. Do not wait for one to finish before dispatching the next.

**Reviewer 1 — Product Owner (@nw-product-owner-reviewer)**

Invoke via #tool:agent with a prompt that asks for story-to-scenario traceability. Load skills from `.github/skills/nw-{skill-name}/SKILL.md` before starting.

**Reviewer 2 — Solution Architect (@nw-solution-architect-reviewer)**

Invoke via #tool:agent with a prompt that asks for hexagonal boundary compliance. Load skills from `.github/skills/nw-{skill-name}/SKILL.md` before starting.

**Reviewer 3 — Platform Architect (@nw-platform-architect-reviewer)**

Invoke via #tool:agent with a prompt that asks for environment coverage. Load skills from `.github/skills/nw-{skill-name}/SKILL.md` before starting.

### Step 3.4: AND-Gate (all three must approve)

After all three reviewers return:
1. Check each reviewer's `approval_status`
2. ANY `rejected_pending_revisions` BLOCKS the DISTILL handoff
3. On rejection:
   - Collect specific findings from rejecting reviewer(s)
   - Re-dispatch `@nw-acceptance-designer` with reviewer findings attached via #tool:agent
   - After revision, re-submit ONLY to the rejecting reviewer(s) — do not re-run approving reviewers
4. On ALL APPROVE: proceed to Phase 4

Max 2 revision cycles. If still rejected after 2 cycles, STOP and escalate to user.

## Phase 4: Produce Wave Decisions

Before completing DISTILL, produce `docs/feature/{feature-id}/distill/wave-decisions.md` (template omitted here).

## Phase 5: Handoff to DELIVER

Deliver artifacts to the next wave (feature files, step definitions, test-scenarios.md, walking-skeleton.md).

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] All user stories have corresponding acceptance tests
- [ ] Step methods call real production services (no mocks at acceptance level)
- [ ] One-at-a-time implementation strategy established (@skip/@pending tags)
- [ ] Tests exercise driving ports, not internal components (hexagonal boundary)
- [ ] Walking skeleton created first with user-centric scenarios (features only; optional for bugs)
- [ ] Infrastructure test scenarios included (if Decision 4 = Yes)
- [ ] Triple Review Gate passed (or fast-path for <=3 scenarios)
- [ ] Handoff package ready for nw-software-crafter (DELIVER wave)
