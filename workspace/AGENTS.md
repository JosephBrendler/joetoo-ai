## Purpose and applicability

**Purpose:** Establish AI and human agent common understanding of the objective - joetoo-ai/workspace is a place in which agent and human developer/maintainer can collaboratively and iteratively develop software supporting the [joetoo](../../joetoo) / [joetoo-upstream](../../joetoo-upstream) ecosystem. This work should be conducted in a manner that is itself consistent with and produces outcomes that are consistent with best practices in agile, efficient, continuous development and integration of reliable and secure software. The purpose of the continuous collaborative workflow described here and refined in each project is to enable a more efficient and better process and better outcomes than could be achieved without an AI-human collaboration.

## Agent roles and active-task discovery

Caveat: this "Agent roles and active-task discovery" and following text up through the end of the table on "Division of responsibility in multi-agent-human collaborative workflow" is to be considered draft and with no instructive authority until maintainer finalizes and approves it and removes this caveat.

All agents must follow the governing AGENTS.md hierarchy.

Local implementation agents, including Codex CLI, must read, and also re-read at the beginning of every task and turn, and follow workspace/LOCAL_AGENTS.md.

Cloud collaboration agents, including ChatGPT, must read, and also re-read at the beginning of every task and turn, and follow workspace/CLOUD_AGENTS.md.

Before beginning task-specific work, identify the active task
handoff document and read its objectives, scope, authorization,
current state, validation evidence, and next action.

Role-specific guidance must not override repository policies
or the maintainer's authorization boundaries.

### Division of responsibility in multi-agent-human collaborative workflow
| Step | Lead actor | Other participants |
| --- | --- | --- |
| Review operational requirement described by maintainer and prepare outline of task-step candidate software change requirements | Cloud agent (e.g. ChatGPT) | local agent (e.g. codes CLI) can produce a local diff and test evidence; maintainer evaluates results and findings and articulates updates to operational requirement specifications |
| Prepare validation/handoff record following completion of each task |	All | Cloud agent uses handoff record to translate maintainer's operational requirement into an outline of software development tasks to be performed by local agent. Local agent supplies implementation evidence, state of local repository not otherwise visible to cloud agent; maintainer reviews handoff file in all exchangesor and either approves or expresses modification requirements either in the handoff file itself, or in prompts to cloud and local agent |
| Commit, push, open draft PR | Maintainer may perform or authorize	local or cloud agent | Local and cloud agent can perform explicitly authorized joetoo-ai publication actions |
| Add cross-agent workflow convention |	ChatGPT drafts; Maintainer approves | appropriate authorized actor updates policy files |
| Pilot Codex, MCP, and GitHub Actions | Codex for local implementation; ChatGPT for design/review |Maintainer authorizes tool installation and CI publication, and reviews results |

## General start-of-assignment discovery

At the beginning of a substantive joetoo assignment, identify the target repository and inspect its current applicable instructions and policies. Enumerate available `.agents/skills/*/SKILL.md` files by name and description; read only relevant skills. If orientation is needed, follow the `joetoo-start` skill where available. Do not rely solely on a remembered skill inventory. If source or skill material is inaccessible, disclose the limitation and do not imply that it was read.

This repository may contain AI-authored recommendations, documentation, skills, test fixtures, and scratch collaboration material when authorized. AI-generated files do not acquire instructional authority merely by being stored in the repository. AGENTS.md files govern AI behavior; accepted architecture and source contracts govern engineering implementation; validation documents record evidence. None of these materials independently authorizes repository modification, deployment, or other actions. Other documentation is not behavioral instruction, though it may document discussion of alternatives and record decisions.  Such documentation is to be kept efficient and clean, so as to avoid "overthinking" matters between turns. The restrictions on direct contribution to `joetoo` and `joetoo-upstream` do not prohibit substantial AI participation in developing candidate code separately for human review, integration, commits, and publication in this joetoo-ai repository.

## Collaboration and review workflow

Follow the branch-and-review process in [README.md](README.md#collaboration-cycle).

- Work autonomously on authorized investigation, candidate edits, and validation
  in joetoo-ai. Keep joetoo and joetoo-upstream separate; their human integration
  and publication are not agent actions under this workflow.
- Before starting or revising a candidate, fetch joetoo-ai and inspect maintainer
  feedback. Treat the maintainer's returned integration changes as the new
  baseline; preserve their edits, metadata, formatting, and validation evidence.
  Preserve an existing draft before replacing it. Never silently overwrite
  local work or reapply an entire stale draft over a newer baseline.
- Use an existing isolated checkout. Use a task branch from the current accepted baseline; start a fresh follow-up branch when the earlier PR has merged. Do not create a worktree unless the user requests one.
- Prepare a concrete diff before requesting publication
  permission. At that point, explicitly ask for the next needed authorization
  (normally commit, push, and draft PR together), identifying the branch, scope,
  and why work is paused. Do not merely say that nothing was committed and wait
  for the maintainer to infer the next step.
- A commit/push/PR approval does not authorize merging or official-repository
  integration. Keep the PR description current as its scope changes.
- After human integration, request that the maintainer push the resulting
  candidate files and test results back to joetoo-ai. The next iteration must
  inspect that feedback before applying further changes. Do not infer official
  repository state or synchronization from a stale workspace copy.

## Working Principles
- Engineering drives documentation; documentation must not drive unnecessary engineering work, nor should documentation drive unnecessary documentation work (or be changed to do so).
- One authoritative collaboration policy, subordinate role-specific guidance, explicit task-level delegation, and continuous maintainer visibility and control.
