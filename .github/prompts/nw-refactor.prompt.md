---
description: "Applies the Refactoring Priority Premise (RPP) levels L1-L6 for systematic code refactoring. Use when improving code quality through structured refactoring passes."
argument-hint: '[target-class-or-module] - Optional: --level=[1-6] --method=[extract|inline|rename|move] --scope=[method|class|module]'
tools:
- todo
- agent
---

# NW-REFACTOR: Systematic Code Refactoring

**Wave**: CROSS_WAVE
**Agent**: Crafty (nw-software-crafter)
**Command**: `*refactor`

## Overview

Applies the Refactoring Priority Premise (RPP) — cascading 6-level hierarchy where lower levels complete before higher. Levels: L1 Readability|L2 Complexity|L3 Responsibilities|L4 Abstractions|L5 Design Patterns|L6 SOLID++. Each builds on previous. For complex multi-class refactorings, agent applies Mikado Method internally.

## Context Files Required

- src/* - Production codebase
- tests/* - Test codebase

## Agent Invocation

@nw-software-crafter

Execute *refactor for {target-class-or-module}.

**Context Files:**
- src/*
- tests/*

**Configuration:**
- level: 3 # Shorthand: --from=1 --to=3 (RPP range)
- from: 1 # Start RPP level (default: 1)
- to: 3 # End RPP level (default: same as level)
- scope: module # file/module/project
- method: extract # extract/inline/rename/move
- mikado_planning: false # Use Mikado Method for complex refactorings

## Progress Tracking

The invoked agent MUST create a task list from its workflow phases at the start of execution using #tool:todo. Each phase becomes a task with the gate condition as completion criterion. Mark tasks in_progress when starting each phase and completed when the gate passes. This gives the user real-time visibility into progress.

## Success Criteria

- [ ] Code quality metrics improved (measured before/after)
- [ ] All tests passing after refactoring
- [ ] Refactoring levels applied in sequence (L1 before L2, etc.)
- [ ] Technical debt reduced measurably

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Refactored codebase with quality improvements

## Examples

### Example 1: Module-level readability refactor
```
/nw-refactor src/auth/token_manager.py --level=2 --scope=module
```
Crafty applies RPP L1-L2: rename ambiguous variables|extract magic numbers into constants|remove dead code (L1), then simplify conditionals|extract long methods (L2).
