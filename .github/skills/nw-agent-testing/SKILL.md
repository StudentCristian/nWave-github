---
name: nw-agent-testing
description: 5-layer testing approach for agent validation including adversarial testing, security validation, and prompt injection resistance
user-invocable: false
disable-model-invocation: true
---

# Agent Testing Framework

## 5-Layer Testing Approach

### Layer 1: Output Quality (Unit-Level)

Validate agent produces correct, well-structured outputs for typical inputs.

**Test**: Agent follows workflow phases | Outputs match expected format/structure | Domain-specific rules correctly applied | Token efficiency within bounds

**How**: Manual invocation with representative inputs. Check against acceptance criteria in agent description.

### Layer 2: Integration / Handoff Validation

Validate correct input/output between agents in workflows.

**Test**: Input parsing handles upstream format | Output format matches downstream expectations | Error signals propagate correctly | Subagent invocation works correctly (agent receives task, executes, returns result)

**How**: End-to-end workflow execution through full agent chain (e.g., DISCUSS -> DESIGN -> DELIVER).

### Layer 3: Adversarial Output Validation

Challenge validity of agent outputs rather than accepting at face value.

**Test**: Source verification (cited sources real and accurate?) | Bias detection (favors one approach without evidence?) | Edge case coverage | Completeness (required sections present?)

**How**: Peer review by `-reviewer` agent using structured critique dimensions.

### Layer 4: Adversarial Verification (Peer Review)

Independent review to catch biases and blind spots in agent design.

**Test**: Definition follows validation checklist? | Redundant platform default instructions? | Over/under-specified? | Could simpler agent achieve same results?

**How**: `@nw-agent-builder` validates via 11-point checklist or `@nw-agent-builder-reviewer` runs structured review.

### Layer 5: Security Validation

Test resilience against misuse and prompt injection.

**Test**: Tool restriction enforcement | Agent stays within declared scope | `user-invocable` and `disable-model-invocation` correctly configured

**How**: Frontmatter fields enforce at platform level. Verify configuration.

## Prompt Injection Resistance

GitHub Copilot provides injection resistance through: subagent isolation (own context via `agents` field) | Tool restriction via frontmatter `tools` array | Agent-scoped hooks (Preview, `PostToolUse` for validation)

Do NOT add prose-based injection defense. Configure platform features:

```yaml
---
tools:                                # Only tools this agent needs
- read/readFile
- search/fileSearch
- search/textSearch
user-invocable: false                 # Hidden from picker if subagent-only
disable-model-invocation: true        # Prevents auto-invocation if manual-only
---
```

## Security Validation Checklist

- [ ] `tools` restricted to minimum necessary (least privilege)
- [ ] `user-invocable` set appropriately (false for subagent-only agents)
- [ ] `disable-model-invocation` set appropriately (true for manual-only skills)
- [ ] No `execute/runInTerminal` unless agent requires command execution
- [ ] No `edit/createFile` or `edit/editFiles` unless agent creates/modifies files
- [ ] Description accurately describes scope
- [ ] `agents` field restricts subagent access (use `[]` to prevent subagent use)
- [ ] No sensitive data hardcoded in definition

## Testing Workflow for New Agents

1. **Create** with minimal definition
2. **Layer 1**: Invoke with 2-3 representative inputs, check outputs
3. **Layer 2**: Run in workflow chain if applicable
4. **Fix** failures observed
5. **Validate**: Run 11-point checklist
6. **Iterate**: Add instructions only for observed failure modes
