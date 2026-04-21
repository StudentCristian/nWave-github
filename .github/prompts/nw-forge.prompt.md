---
description: "Creates new specialized agents using the 5-phase workflow (ANALYZE > DESIGN > CREATE > VALIDATE > REFINE). Use when building a new AI agent or validating an existing agent specification."
argument-hint: '[agent-name] - Optional: --type=[specialist|reviewer|orchestrator] --pattern=[react|reflection|router]'
tools:
- todo
- agent
- edit/createFile
- edit/createDirectory
- read/readFile
---

# NW-FORGE: Create Agent (V2)

**Wave**: CROSS_WAVE
**Agent**: Zeus (nw-agent-builder)

## Overview

Create a new agent using research-validated v2 approach: focused core (200-400 lines) with Skills for domain knowledge. 5-phase workflow: ANALYZE > DESIGN > CREATE > VALIDATE > REFINE.

## Agent Invocation

Invoke the builder via #tool:agent (nw-agent-builder) to execute `*forge` and create the {agent-name} agent.

**Configuration:**
- agent_type: specialist | reviewer | orchestrator
- design_pattern: react | reflection | router | planning | sequential | parallel | hierarchical

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] Agent definition under 400 lines (`wc -l`)
- [ ] Official YAML frontmatter format (name, description, tools)
- [ ] 11-point validation checklist passes
- [ ] Only divergent behaviors specified (no Claude defaults)
- [ ] 3-5 canonical examples included
- [ ] Domain knowledge extracted to Skills if >50 lines
- [ ] No aggressive language (no CRITICAL/MANDATORY/ABSOLUTE)
- [ ] Safety via platform features (frontmatter/hooks), not prose

## Next Wave

**Handoff To**: Agent installation and deployment
**Deliverables**: Agent specification file + Skill files (if any)

## Expected Outputs

```
.github/agents/nw/nw-{agent-name}.md
.github/skills/nw-{agent-name}/*.md    (if Skills needed)
```
