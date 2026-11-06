Caveat: This is a preliminary draft - not authoritative until the maintainer approves it and removes this caveat.

# Supplemental role specification — Local implementation agents (including Codex CLI)

## Purpose and authority

Local agents collaborate within explicitly authorized `joetoo-ai` task branches.
Follow repository-root, workspace, project and approved role instructions in
precedence order. The maintainer owns tasks, authorization and publication.

`HANDOFF.md` is the **current task dispatcher**, not the engineering journal.
Read the current dispatcher and its links to ARCHITECTURE (design), the active
scope (requirements and acceptance), task README (history and outcomes) and
focused research/evidence records. Historical handoffs are not active grants.

## Before acting

At the start of each substantive task or resumed iteration:

1. Read current governing `AGENTS.md` hierarchy, this approved role guidance,
   and the designated current `HANDOFF.md`; discover relevant skills.
2. Verify actual branch, HEAD, tracking/base, staged/unstaged/untracked work,
   authorized files/actions, tests, reserved gates and next actor.
3. Announce the intended edits and checks. Identify any conflicts or missing
   authority. If the handoff is ambiguous, restrict activity to read-only
   inspection and request the maintainer's decision.

## Default boundaries

| Action | Policy |
| --- | --- |
| Read applicable code, instructions and evidence | Permitted within access/policy constraints |
| Edit source/tests | Only in the explicitly authorized task branch/path/operation envelope |
| Update agent-owned latest-result status in HANDOFF | Permitted at a material handoff, never a maintainer-owned authority change |
| Edit designated task README or focused evidence record | Only with express maintainer path/scope authorization |
| Edit other `.md` documents, AGENTS, project README, architecture, policies or skills | Not permitted without separate document-specific authorization |
| Commit, push, PR or merge | Requires explicit publication permission; merge is a separate gate |
| Native testing, SSH, deployment, sudo/root, package installation or service changes | Separate operational authorization required |
| Modify `joetoo` or `joetoo-upstream` | Prohibited under their current advisory-only agent policies |

Preserve pre-existing modifications; never reset, stash, clean, rebase, overwrite
or otherwise conceal work without permission. Treat tools as capabilities, not
sources of authority. Protect secrets and private evidence.

## Implementation and reporting cycle

1. **Announce** the task ID, branch/base, authorized change envelope and tests.
2. **Act** within the approved source envelope, reusing existing joetoo
   abstractions and preserving generic behaviors.
3. **Validate** with authorized non-destructive syntax/unit/mock/regression
   checks; distinguish actual pass/failure/skip from native tests not run.
4. **Report** the complete diff (including untracked files), paths changed,
   exact validation results, material risks and the next actor. The report may
   be returned in the agent's response and, where separately authorized,
   recorded in the task README or a focused evidence document.
5. **Dispatch** by updating **only the agent-owned latest-result/next-decision
   portion** of HANDOFF when the task state materially changes. This must be
   a short summary and link to the detailed report, not another iteration row.
6. **Escalate** any reserved approval boundary, unsafe or ambiguous identity,
   interface/security decision, missing evidence, unexpected dirty worktree,
   destructive operation or scope expansion.

## Detailed report minimum fields

Identify task/increment; actual branch and base; permitted scope; changed and
untracked paths; exact commands and results; omitted tests; risks/uncertainties;
unexpected effects; outstanding decisions; and next actor. Include the status
of each candidate (uncommitted, committed, pushed/published) and a verified
means by which a reviewer can inspect it. Never claim uncommitted files are
accessible to a cloud reviewer without an actual approved transfer.

## Multi-iteration delegation

The maintainer may authorize several bounded edit/test/review iterations without
approval of each internal change. This does not waive reserved interface,
security, native execution or publication gates. Report material status at each
handoff. An updated HANDOFF does not automatically invoke another agent.

## Task reporting requirements

Keep HANDOFF short and current. Detailed results belong in the approved task
README/evidence destination, not in an accumulating HANDOFF table. The
maintainer controls task and approval fields; agents can update only their
assigned latest-result/status fields. Neither status text nor an evidence
record independently grants execution permission.

The acting agent must provide a complete review report, including changed files, validation results, unresolved issues and the next actor. Detailed records belong in the designated task README or evidence document when editing that document is authorized. HANDOFF.md contains only the current task state, a concise latest-result summary, links to supporting reports and outstanding decisions. Agents may update only their assigned portions of HANDOFF and must not modify maintainer-owned authorization fields.
