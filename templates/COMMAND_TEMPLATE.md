 # nWave Prompt File Template

 Version: 2.0 (2026-04-22)
 Extracted from analysis of 22 production prompt files.
 Replaces COMMAND_TEMPLATE.yaml (437 lines of comments) with actionable markdown.

 ## Frontmatter Schema

 ```yaml
 ---
 name: "nw-{name}"                                                       # OPTIONAL. Defaults to filename (without .prompt.md)
 description: "{What this prompt does. When to use it.}"                 # OPTIONAL. Shown in prompt picker
 argument-hint: "{usage pattern with parameters}"                        # OPTIONAL. Hint in chat input
 agent: "agent"                                                          # OPTIONAL. agent|ask|plan|{custom-agent-name}
 model: ""                                                               # OPTIONAL. Omit to use session default
 tools:                                                                  # OPTIONAL. List of tool aliases/refs
   - agent                                                               #   Subagent invocation
   - read                                                                #   File reading
   - search                                                              #   File/text search
   - edit                                                                #   File editing
   - execute                                                             #   Terminal commands
   - todo                                                                #   Task management
   - vscode/askQuestions                                                  #   User interaction
 ---
 ```

 ### Field Reference

 | Field | Type | Required | Notes |
 |-------|------|----------|-------|
 | name | string | no | Defaults to filename. Use `nw-{name}` convention |
 | description | string | no | Shown in prompt picker. Include "Use when..." |
 | argument-hint | string | no | Usage pattern: `[param] - Optional: --flag=[values]` |
 | agent | string | no | `agent` (default if tools specified), `ask`, `plan`, or custom agent name |
 | model | string | no | Qualified name like `Claude Sonnet 4 (copilot)`. Omit for session default |
 | tools | list | no | Tool aliases or specific tool refs. Only list tools the prompt actually uses |

 ---

 ## Prompt File Categories

 | Category | Size Target | Structure | Examples |
 |----------|-------------|-----------|----------|
 | Dispatcher | 40-80 lines | Agent invocation + success criteria | forge, research, review |
 | Orchestrator | 100-250 lines | Multi-phase coordination + agent invocations | deliver, discuss, design |

 ## Body Template: Dispatcher (40-80 lines)

 ```markdown
 ---
 description: "{Description. Use when...}"
 argument-hint: "[param] - Optional: --flag=[value]"
 tools:
   - agent
   - read
   - search
 ---

 # NW-{NAME}: {Title}

 **Wave**: {WAVE_NAME} | **Agent**: {PersonaName} (nw-{agent-id})

 ## Overview

 {One paragraph: what this prompt does and when to use it.}

 ## Context Files Required

 - {path} - {why this file is needed}
 - {path} - {why this file is needed}

 ## Agent Invocation

 @nw-{agent-id}

 Execute \*{command} for {parameters}.

 **Context Files:**
 - {files the orchestrator reads and passes}

 **Configuration:**
 - {key}: {value}

 ## Success Criteria

 - [ ] {measurable outcome}
 - [ ] {quality gate}
 - [ ] {deliverable exists}

 ## Examples

 ### Example 1: {Standard usage}
 ```
 /nw-{command} "{arguments}"
 ```
 {Brief description of what happens.}

 ## Next Wave

 **Handoff To**: {next-wave-agent or "Invoking workflow"}
 **Deliverables**: {what this prompt produces}

 ## Expected Outputs

 ```
 {file paths produced}
 ```
 ```

 ## Body Template: Orchestrator (100-250 lines)

 ```markdown
 ---
 description: "{Description. Use when...}"
 argument-hint: "[param] - Optional: --flag=[value]"
 tools:
   - agent
   - read
   - search
   - edit
   - execute
   - todo
   - vscode/askQuestions
 ---

 # NW-{NAME}: {Title}

 **Wave**: {WAVE_NAME} | **Agent**: Main Instance (orchestrator) | **Prompt**: `/nw-{name}`

 ## Overview

 {One paragraph: what this prompt orchestrates.}

 Sub-agents load their own skills by reading `.github/skills/nw-{agent-name}/SKILL.md`. You MUST:
 - Embed relevant context and instructions in the subagent prompt via `#tool:agent/runSubagent`
 - Include a SKILL_LOADING reminder so the agent reads its skills at `.github/skills/nw-{agent-name}/`

 ## Interactive Decision Points

 ### Decision 1: {Choice}
 **Question**: {What the orchestrator asks the user}
 **Options**:
 1. {Option} -- {description}
 2. {Option} -- {description}

 ## Context Files Required

 - {path} - {why needed}

 ## Rigor Profile Integration

 Before dispatching, read rigor config from `.nwave/des-config.json` (key: `rigor`). If absent, use standard defaults.

 - **`agent_model`**: Pass as `model` to `#tool:agent/runSubagent`. If `"inherit"`, omit.
 - **`reviewer_model`**: Pass to reviewer subagent. If `"skip"`, skip review phase.

 ## Orchestration Flow

 ```
 INPUT: "{parameters}"
   |
   1. {Phase 1 description}
   |
   2. {Phase 2 description} -- @nw-{agent} via #tool:agent/runSubagent
   |
   3. {Phase 3 description} -- @nw-{agent} via #tool:agent/runSubagent
   |
   N. Report completion
 ```

 ## Subagent Invocation Pattern

 Invoke subagents via `#tool:agent/runSubagent`. Include the agent name, context, and a SKILL_LOADING reminder in the prompt:

 ```
 Agent: @nw-{agent-name}
 Prompt: |
   TASK BOUNDARY: {description}

   SKILL_LOADING: Read your skill files at .github/skills/nw-{agent-name}/.
   At PREPARE phase, always load: {primary-skill}.
   Then follow your Skill Loading Strategy table for phase-specific skills.

   {task-specific context}
 ```

 ## Success Criteria

 - [ ] {Phase 1 outcome}
 - [ ] {Phase 2 outcome}
 - [ ] {Overall outcome}

 ## Examples

 ### Example 1: {Standard execution}
 `/nw-{name} "{arguments}"` -- {description of full flow}

 ### Example 2: {Resume after failure}
 Same prompt -- {description of resume behavior}

 ## Next Wave

 **Handoff To**: {next-wave or "completion"}
 **Deliverables**: {final artifacts}

 ## Expected Outputs

 ```
 {file paths produced}
 ```
 ```

 ---

 ## Section Reference

 ### Required Sections (all prompt files)

 | Section | Purpose |
 |---------|---------|
 | Title (`# NW-{NAME}`) | Prompt identity with wave and agent |
 | Overview | What the prompt does, one paragraph |
 | Agent Invocation | Which agent, what command, configuration |
 | Success Criteria | Measurable outcomes checklist |
 | Next Wave | Handoff target and deliverables |

 ### Optional Sections (by category)

 | Section | When to Include |
 |---------|----------------|
 | Interactive Decision Points | Orchestrators with user choices |
 | Context Files Required | Prompts needing file context |
 | Rigor Profile Integration | Prompts dispatching subagents |
 | Orchestration Flow | Orchestrators with multi-phase coordination |
 | Subagent Invocation Pattern | Orchestrators showing `#tool:agent/runSubagent` usage |
 | Error Handling | Prompts with validation/error states |
 | Examples | All prompts (1-4 examples) |
 | Expected Outputs | Prompts producing file artifacts |

 ---

 ## Design Principles

 ### Prompt Files Declare WHAT, Not HOW

 **Include in prompt file** (declarative):
 - Which agent to invoke
 - What context files to read and pass
 - Success criteria and quality gates
 - Next wave handoff

 **Delegate to agent** (belongs in agent definition or skill):
 - Methodology (TDD phases, review criteria, refactoring levels)
 - Domain-specific templates and schemas
 - Tool-specific configuration
 - Quality assessment rubrics

 Rule: if content describes HOW the agent does its work, it belongs in the agent
 definition or skill, not in the prompt file.

 ### SKILL_LOADING Reminder

 Every prompt file dispatching a sub-agent via `#tool:agent/runSubagent` MUST include a SKILL_LOADING reminder in the subagent prompt. Sub-agents load skills by reading them from `.github/skills/`.

 ```
 SKILL_LOADING: Read your skill files at .github/skills/nw-{agent-name}/.
 At PREPARE phase, always load: {primary-skill}.
 Then follow your Skill Loading Strategy table for phase-specific skills.
 ```

 ---

 ## Anti-Patterns

 | Anti-Pattern | Impact | Fix |
 |---|---|---|
 | Embedded workflow steps | Prompt file becomes 500+ lines | Move to agent definition |
 | Duplicated agent knowledge | Same content in prompt and agent | Remove from prompt |
 | Procedural overload | Step-by-step for capable agents | Declare goal + constraints |
 | Aggressive language | Overtriggering in advanced models | Direct statements |
 | Example overload | 50+ lines of examples | 2-4 canonical examples |
 | Missing SKILL_LOADING | Sub-agent operates without domain knowledge | Add reminder in subagent prompt |
 | JSON state examples | 200+ lines of format examples | Show actual format, 3 examples max |

 ---

 ## Observed Size Statistics

 | Category | Lines (min) | Lines (median) | Lines (max) |
 |----------|-------------|----------------|-------------|
 | Dispatcher | 40 | 65 | 90 |
 | Orchestrator | 100 | 170 | 250 |
 | All prompt files | 40 | 110 | 250 |
