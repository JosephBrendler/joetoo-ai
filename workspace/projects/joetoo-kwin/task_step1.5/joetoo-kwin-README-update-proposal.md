# Proposed *focused* edits to project `README.md`

**Source reviewed:** `workspace/projects/joetoo-kwin/README.md` on `joetoo-ai/main` (blob `98af27e9210d7186bf767a0e4a60381d3f4100fc`), October 28, 2026.  
**Status:** proposed, not applied. The current README correctly names Step 1.4d complete, but contains obsolete text below it, including a statement that the four-window fixture does not register windows. This proposal replaces only that obsolete material and a couple of references.  
**Prerequisite:** add and review the proposed `task_step1.4/HANDOFF.md` and `task_step1.5/HANDOFF.md` before publishing links to them.

## Edit 1: Replace the entire current `## Current status` section through (but not including) `## Development and validation platforms`

```markdown
## Current status

**Completed through Step 1.4d** (October 2026). Step 1.4 established
broker-private managed-window registration, independent presence and placement
states, UUID-based observation reconciliation, read-only registry queries, and
bounded asynchronous placement confirmation. The four-window managed-launch
fixture passed native X11 and Wayland validation. These are collaboration
candidates in `joetoo-ai`, not yet the complete version 1 application.

| Increment | Status and scope | Evidence |
| --- | --- | --- |
| 1.4a | Complete: registry identity, state, and headless contracts | [PR #19](https://github.com/JosephBrendler/joetoo-ai/pull/19) |
| 1.4b | Complete: broker-private correlation and multiwindow UUID reconciliation | [PR #20](https://github.com/JosephBrendler/joetoo-ai/pull/20) |
| 1.4c | Complete: read-only `ListManaged`, `GetManaged`, `RegistryStatus` | [PR #21](https://github.com/JosephBrendler/joetoo-ai/pull/21) |
| 1.4d | Complete: managed multiwindow launches, asynchronous placement confirmation and native validation | [PR #22](https://github.com/JosephBrendler/joetoo-ai/pull/22) |

For Step 1.4d, the maintainer reported **144 Python and 8 JavaScript tests
passing on each development machine**. Native tests on `gmki91` (Plasma X11)
and `q552u01` (Plasma Wayland) each registered four separate Konsole windows,
confirmed all four placements, verified exact desktop/geometry and no adoption
of preexisting KWin UUIDs, and preserved placement history when a window was
closed (presence became `missing`). These results do not establish completion
of the general `-o` SSH/configuration workflow, destructive managed close,
checkpointing or reboot restoration.

For the completed milestone, its validation boundaries and deferred issues, see
[Step 1.4 closure handoff](task_step1.4/HANDOFF.md). The proposed next milestone,
including its authorization and validation plan, is in the
[Step 1.5 task handoff](task_step1.5/HANDOFF.md).

Step 1.5 addresses the shared geometry policy, `mw l/r`, colorized `-c`,
configuration-driven `-o` with SSH placeholders and `-v/-q`. Steps 1.6–1.9
remain planned according to [ARCHITECTURE.md](ARCHITECTURE.md). Phase 2
reserves measured optimization/refinement work after the core prototype.
```

## Edit 2: In `## Active development files and checks`, update stale descriptions

Replace the `joetoo-kwin` CLI bullet with:

```markdown
- `joetoo-kwin` — current Bash CLI for active-window placement and the
  Step 1.4d managed test-launch fixture; generalized configuration-driven
  layouts and SSH placeholders are Step 1.5 work.
```

Update the tests bullet to mention handoff directories:

```markdown
- `tests/` — headless regressions; `archive/` — historical POCs;
  `task_step1.4/` and `task_step1.5/` — milestone evidence and current-task
  handoffs, not runtime source.
```

Replace the JavaScript test command in the existing code fence:

```bash
node --test tests/*.js

# End of commands

```

The remainder of the existing checks (Python, Bash syntax and installer `--check`) can be retained subject to checking they still represent desired developer checks. `--check` inspects an installed POC rather than performing a universally portable headless test.

## Edit 3: Add a succinct reference under `## Design and development references`

```markdown
- [Step 1.4 closure](task_step1.4/HANDOFF.md) and
  [Step 1.5 active-task proposal](task_step1.5/HANDOFF.md) — milestone
  completion evidence and maintained task state, respectively.
```

Avoid copying full test transcripts or interim patch histories into the README. Keep it a current-status landing page; leave precise acceptance evidence and task authorization in the designated handoffs, and retain the actual code history in PRs and commits.
