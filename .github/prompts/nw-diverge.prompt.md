---
description: "Generates 3-5 divergent design directions through JTBD analysis, competitive research, structured brainstorming, and taste evaluation before convergence."
argument-hint: '[feature-id] - Optional: --work-type=[new-product|brownfield|pivot]'
tools:
- todo
- agent
- read/readFile
---

# NW-DIVERGER: Structured Divergent Thinking Before Convergence

**Wave**: DIVERGE (between DISCOVER and DISCUSS, optional) | **Agent**: Flux (nw-diverger) | **Command**: `/nw-diverger`

## Overview

Execute DIVERGE wave through Flux's 4-phase workflow: JTBD analysis|competitive research|structured brainstorming|taste-filtered evaluation. Transforms a validated problem into 3-5 concrete, taste-scored design directions so DISCUSS can converge on one with confidence.

DIVERGE is optional. Brownfield features with a clear direction may skip it (see skip checklist in design spec). New products and pivot decisions benefit most from structured divergence.

## Interactive Decision Points

### Decision 1: Work Type
**Question**: What type of work is this?
**Options**:
1. New product -- no prior solution exists, full divergence needed
2. Brownfield feature -- existing product, exploring approach alternatives
3. Pivot / redesign -- existing feature being reconsidered from scratch
4. Other -- user provides custom context

### Decision 2: Research Depth
**Question**: How deep should competitive research go?
**Options**:
1. Lightweight -- 3 competitors, known market
2. Comprehensive -- 5+ competitors including non-obvious alternatives
3. Deep-dive -- cross-category research, adjacent markets, academic references

## Prior Wave Consultation

Before beginning DIVERGE work, read SSOT and prior wave artifacts:

1. **SSOT** (if `docs/product/` exists):
   - `docs/product/jobs.yaml` -- validated jobs and opportunity scores
   - `docs/product/vision.md` -- product vision and strategic context
2. **Project context**: `docs/project-brief.md` | `docs/stakeholders.yaml` (if available)
3. **DISCOVER artifacts**: Read `docs/feature/{feature-id}/discover/` (if present)
   - `wave-decisions.md` -- validated assumptions and key decisions
   - `problem-validation.md` -- customer evidence grounding the problem

If `docs/product/` does not exist, this is the first wave using the SSOT model. DIVERGE will create it (bootstrap `docs/product/jobs.yaml` with the validated job).

**READING ENFORCEMENT**: You MUST read every file listed in Prior Wave Consultation above using #tool:read/readFile before proceeding. After reading, output a confirmation checklist. Do NOT skip files that exist -- skipping causes options disconnected from evidence.

## Agent Invocation

@nw-diverger

Execute *diverge for {feature-id}.

**Context Files:** see Prior Wave Consultation above + project context files.

**Configuration:**
- work_type: {Decision 1}
- research_depth: {Decision 2}
- output_directory: docs/feature/{feature-id}/

**SKILL_LOADING**: Before starting work, load your skill files using the Read tool from `.github/skills/nw-{skill-name}/SKILL.md`. Skills encode your methodology -- without them you operate with generic knowledge only.

**Phase 1 -- JTBD Analysis:**
Flux loads `jtbd-analysis` skill. Extracts and elevates the job from the raw request or DISCOVER evidence. Produces job statements (functional + emotional + social) and ODI outcome statements. Gate G1 validates job level and ODI minimum.

**Phase 2 -- Competitive Research:**
Flux invokes `nw-researcher` sub-agent for evidence-grounded competitive research. Maps how existing products serve the validated job. Identifies non-obvious alternatives. Gate G2 validates real products named and evidence quality.

**Phase 3 -- Brainstorming:**
Flux loads `brainstorming` skill. Frames HMW question, applies SCAMPER lenses, generates structurally diverse options. Gate G3 validates diversity (mechanism|assumption|cost differ).

**Phase 4 -- Taste Evaluation:**
Flux loads `taste-evaluation` skill. Applies DVF filter, scores surviving options on 4 taste criteria with locked weights, produces weighted ranking and recommendation with dissenting case. Gate G4 validates completeness and traceability.

**Peer Review:**
After Phase 4 gates pass, Flux invokes `nw-diverger-reviewer` (Prism) to validate all 5 dimensions. Max 2 revision iterations before handoff.

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] Job extracted at strategic or physical level (not tactical, not a feature description)
- [ ] Minimum 3 ODI outcome statements produced
- [ ] 3+ real competitors researched, at least one non-obvious alternative
- [ ] 6 structurally diverse options generated (different mechanism, assumption, cost)
- [ ] All surviving options scored on all 4 taste criteria with locked weights
- [ ] Recommendation traceable to scoring matrix (no "feels right" overrides)
- [ ] Dissenting case documented for second-place option
- [ ] Peer review approved by nw-diverger-reviewer
- [ ] Handoff accepted by nw-product-owner (DISCUSS wave)

## Next Wave

**Handoff To**: nw-product-owner (DISCUSS wave)
**Deliverables**: `recommendation.md` with explicit decision statement + supporting DIVERGE artifacts
