---
description: "Designs CI/CD pipelines, infrastructure, observability, and deployment strategy. Use when preparing platform readiness for a feature."
argument-hint: '[deployment-target] - Optional: --environment=[staging|production] --validation=[full|smoke]'
tools:
- todo
- agent
- read/readFile
- edit/createFile
- edit/editFiles
---

# NW-DEVOPS: Platform Readiness and Infrastructure Design

**Wave**: DEVOPS (wave 4 of 6) | **Agent**: Apex (nw-platform-architect) | **Command**: `/nw-devops`

## Overview

Execute DEVOPS wave: platform readiness|CI/CD pipeline setup|observability design|infrastructure preparation. Positioned between DESIGN and DISTILL (DISCOVER > DISCUSS > SPIKE > DESIGN > DEVOPS > DISTILL > DELIVER), ensures infrastructure is ready before acceptance tests and code.

Apex translates DESIGN architecture decisions into operational infrastructure: CI/CD pipelines|logging|monitoring|alerting|observability.

## Interactive Decision Points

... (omitted here for brevity — original content preserved)

After selection, Apex asks permission to write to project .github/copilot-instructions.md under `## Mutation Testing Strategy` with the chosen strategy and description.

## Prior Wave Consultation

Before beginning DEVOPS work, read SSOT and prior wave artifacts:

1. **SSOT** (if `docs/product/` exists):
   - `docs/product/architecture/brief.md` — current architecture (driving ports, component topology)
   - `docs/product/kpi-contracts.yaml` — existing KPI contracts (if any — extend, don't duplicate)
2. **DISCUSS** (KPIs only): Read `docs/feature/{feature-id}/discuss/outcome-kpis.md` — drives observability and instrumentation design
3. **DESIGN** (primary input): Read `docs/feature/{feature-id}/design/wave-decisions.md` + SSOT architecture — architecture drives infrastructure decisions

SSOT architecture is the primary input for infrastructure design. Feature-level `outcome-kpis.md` defines what to instrument for this specific feature.

**READING ENFORCEMENT**: You MUST read every file listed in Prior Wave Consultation above using #tool:read/readFile before proceeding. After reading, output a confirmation checklist (`✓ {file}` for each read, `⊘ {file} (not found)` for missing). Do NOT skip files that exist — skipping causes infrastructure decisions disconnected from architecture.

## Document Update (Back-Propagation)

When DEVOPS decisions change assumptions from prior waves:
1. Document the change in a `## Changed Assumptions` section at the end of the affected DEVOPS artifact
2. Reference the original prior-wave document and quote the original assumption
3. State the new assumption and the rationale for the change
4. If infrastructure constraints require architecture changes, note them in `docs/feature/{feature-id}/devops/upstream-changes.md` for the architect to review

## Agent Invocation

@nw-platform-architect

Execute platform readiness and infrastructure design for {feature-id}.

Context files: see Prior Wave Consultation above.

**Configuration:**
- deployment_target: {Decision 1} | container_orchestration: {Decision 2}
- cicd_platform: {Decision 3} | existing_infrastructure: {Decision 4}
- observability_and_logging: {Decision 5} | deployment_strategy: {Decision 6}
- continuous_learning: {Decision 7} | git_branching_strategy: {Decision 8}
- mutation_testing_strategy: {Decision 9}

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] CI/CD pipeline design finalized and documented
- [ ] Logging infrastructure design complete (structured logging|aggregation)
- [ ] Monitoring and alerting design complete (metrics|dashboards|SLOs/SLIs)
- [ ] Observability design complete (distributed tracing|health checks)
- [ ] Infrastructure integration assessed (if existing infra)
- [ ] Continuous learning capabilities designed (if applicable)
- [ ] Git branching strategy selected and CI/CD triggers aligned
- [ ] Mutation testing strategy selected and persisted to project .github/copilot-instructions.md
- [ ] Outcome KPIs instrumentation designed (if outcome-kpis.md exists)
- [ ] Data collection pipeline documented for each KPI
- [ ] Dashboard mockup or spec includes all outcome KPIs
- [ ] Handoff accepted by nw-acceptance-designer (DISTILL wave)
