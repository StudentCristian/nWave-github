---
description: "Creates a phased roadmap.json for a feature goal with acceptance criteria and TDD steps. Use when planning implementation steps before execution."
argument-hint: '[agent] [goal-description] - Example: @solution-architect "Migrate to microservices"'
tools:
- todo
- agent
- execute/runInTerminal
- read/readFile
---

# NW-ROADMAP: Goal Planning

**Wave**: CROSS_WAVE
**Agent**: Architect (nw-solution-architect) or domain-appropriate agent

## Overview

Dispatches expert agent to fill a pre-scaffolded YAML roadmap skeleton. CLI tools handle structure; agent handles content.

Output: `docs/feature/{feature-id}/deliver/roadmap.json`

## Usage

```bash
/nw-roadmap @nw-solution-architect "Migrate monolith to microservices"
/nw-roadmap @nw-software-crafter "Replace legacy authentication system"
/nw-roadmap @nw-product-owner "Implement multi-tenant support"
```

## Execution Steps

You MUST execute these steps in order. Do NOT skip any.

**Step 1 — Parse parameters:**
1. Agent name (after @, validated against agent registry)
2. Goal description (quoted string)
3. Derive feature-id from goal (kebab-case, e.g., "Migrate to OAuth2" -> "migrate-to-oauth2")

**Step 2 — Scaffold skeleton via CLI (mandatory, BEFORE invoking agent):**

```bash
PYTHONPATH=$HOME/.github/lib/python $(command -v python3 || command -v python) -m des.cli.roadmap init \
  --project-id {feature-id} \
  --goal "{goal-description}" \
  --output docs/feature/{feature-id}/deliver/roadmap.json
```
For complex projects add: `--phases 3 --steps "01:3,02:2,03:1"`

If exit code non-zero, stop and report error. Do NOT write file manually.

**Step 3 — Invoke agent to fill skeleton:**

Invoke the filling agent via #tool:agent. Skeleton exists with TODO placeholders. Provide the agent the skeleton path and goal description and ask it to replace TODOs without changing YAML structure.

Context to pass (if available): measurement baseline|mikado-graph.md|existing docs.

**Step 4 — Validate via CLI (hard gate, mandatory):**

```bash
PYTHONPATH=$HOME/.github/lib/python $(command -v python3 || command -v python) -m des.cli.roadmap validate docs/feature/{feature-id}/deliver/roadmap.json
```
- Exit 0 -> success, roadmap ready
- Exit 1 -> print errors, STOP, do NOT proceed
- Exit 2 -> usage error, STOP

## Invocation Principles

Keep agent prompt minimal. Agent knows roadmap structure and planning methodology.

Pass: skeleton file path + goal description + measurement context (if available).
Do not pass: YAML templates|phase guidance|step decomposition rules.

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

### Dispatcher (you) — all 4 must be checked
- [ ] Parameters parsed (agent name, goal, feature-id)
- [ ] `des.cli.roadmap init` executed via CLI (exit 0)
- [ ] Agent invoked via #tool:agent to fill TODO placeholders
- [ ] `des.cli.roadmap validate` executed via CLI (exit 0)

### Agent output (reference)
- [ ] All TODO placeholders replaced with real content
- [ ] Steps are self-contained and atomic
- [ ] Acceptance criteria are behavioral and measurable
- [ ] Step decomposition ratio <= 2.5 (steps / production files)
- [ ] Dependencies mapped, time estimates provided

## Error Handling

- Invalid agent: report valid agents and stop
- Missing goal: show usage syntax and stop
- Scaffold failure (exit 2): report CLI error and stop
- Validation failure (exit 1): print errors, do not proceed
