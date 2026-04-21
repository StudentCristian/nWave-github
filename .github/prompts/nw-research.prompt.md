---
description: "Gathers knowledge from web and files, cross-references across multiple sources, and produces cited research documents. Use when investigating technologies, patterns, or decisions that need evidence backing."
argument-hint: '[topic] - Optional: --research_depth=[overview|detailed|comprehensive|deep-dive] --skill-for=[agent-name]'
tools:
- todo
- agent
- read/readFile
---

# NW-RESEARCH: Evidence-Driven Knowledge Research

**Wave**: CROSS_WAVE
**Agent**: Nova (nw-researcher)
**Command**: `*research`

## Overview

Systematic evidence-based research with source verification. Cross-wave support providing research-backed insights for any nWave phase using trusted academic|official|industry sources.

Optional `--skill-for={agent-name}` distills research into a practitioner-focused skill file for a specific agent.

## Orchestration: Trusted Source Config

At orchestration time, before invoking the researcher subagent:

1. **Read** `.nwave/trusted-source-domains.yaml` from the project root
2. **If file missing**, seed it from the defaults in the `## Default Trusted Sources` section below, then notify the user:
   "Seeded `.nwave/trusted-source-domains.yaml` with defaults (7 categories, 42 trusted domains, 5 excluded). Edit the YAML directly to customize."
3. **Embed** the YAML content inline in the researcher subagent Task prompt so the agent receives trusted source config via prompt context

## Agent Invocation

@nw-researcher

Execute \*research on {topic} [--skill-for={agent-name}].

**Configuration:**
- research_depth: detailed # overview/detailed/comprehensive/deep-dive
- source_preferences: ["academic", "official", "technical_docs"]
- output_directory: docs/research/
- skill_for: {agent-name} # Optional: distilled skill for specified agent
- skill_output_directory: .github/skills/nw-{agent-name}/

## Output Management

The researcher MUST create the output file in the FIRST 5 turns with a document skeleton (title, sections, placeholders). All subsequent findings are written DIRECTLY to this file as they are gathered -- never held only in context.

If the agent is interrupted or runs out of turns, the output file contains all work done so far. This is the researcher's equivalent of the crafter's "commit early, commit often."

Progressive write checkpoints:
- Turn ~5: Output file exists with skeleton
- Turn ~10: First findings written
- Turn ~25: All gathered findings written so far
- Turn ~35: Stop gathering, begin synthesizing
- Turn ~45+: Polish only

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

**Research:**
- [ ] All sources from trusted source domains from prompt context
- [ ] Cross-reference performed (3+ sources per major claim ideal, 2 acceptable, 1 authoritative minimum)
- [ ] Research file created in docs/research/
- [ ] Citation coverage > 95%
- [ ] Average source reputation >= 0.80

**Distillation (if --skill-for specified):**
- [ ] Skill file created in .github/skills/nw-{agent-name}/
- [ ] 100% essential concepts preserved
- [ ] Self-contained with no external references
- [ ] Token budget respected (<5000 tokens per skill)

## Next Wave

**Handoff To**: Invoking workflow
**Deliverables**: Research document + optional skill file

## Examples

### Example 1: Standalone research
```
/nw-research "event sourcing patterns" --research_depth=detailed
```
Nova researches event sourcing from trusted sources, cross-references 3+ sources per claim, produces comprehensive research document.

## Expected Outputs

```
docs/research/{category}/{topic}-comprehensive-research.md
.github/skills/{agent}/{topic}-methodology.md    (if --skill-for)
```
