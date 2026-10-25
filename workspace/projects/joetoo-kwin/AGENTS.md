# AI collaborator instructions — joetoo-kwin project

Applies within `workspace/projects/joetoo-kwin/` in `joetoo-ai`.

## Read the architecture first

**Before design, candidate edits, tests, review, or PR preparation**, read
[`ARCHITECTURE.md`](ARCHITECTURE.md) and identify the current milestone
and acceptance gate. Treat it as the **project's accepted design record**,
not proof that planned features are implemented. Preserve the document's
explicit distinctions among accepted requirements, tested POC behavior,
proposed mechanisms, and unresolved verification tasks.

Read the current repository root `AGENTS.md`, `workspace/AGENTS.md`, and
`workspace/README.md`. Follow their scope, authorization and branch-and-review
workflow. If any governing document is unavailable, state the limitation
rather than silently substituting remembered content. Project instructions
cannot override higher-priority policy or the protected repositories' own
AI policies.

## Inspect the current baseline and reuse established work

- Fetch the current `joetoo-ai` accepted baseline and inspect relevant files
  in `step1-candidate/` and the six preserved POC reference directories under
  `archive/` **as relevant**, along with any subsequent maintainer feedback.
  Do not treat an older POC as the authoritative latest implementation.
- Consult applicable installed skills under `.agents/skills/`, especially
  `script_header_joetoo`, `script_header_joetoo-CLI`,
  `script_header_joetoo_ssh`, and `pseudo-boolean_framework`. Discover the
  actual skill names/paths instead of presuming they remain unchanged.
- For related joetoo source or packaging, inspect `joetoo-upstream` and
  `joetoo` **read-only**, including their specific AI policies; do not modify
  or execute their development workflows. Official integration is reserved
  for the human maintainer.
- Prefer existing `script_header_joetoo` functions, SSH wrappers, KWin bridge,
  joetoo colors/messages and configuration conventions. Do not introduce
  undefined helpers, undocumented assumptions, or a replacement framework
  without first checking what already exists.

## Project invariants and deliberate safety boundaries

- Preserve X11 and Wayland support; do not regress proven Step 0 SSH lifecycle
  and window-placement behavior. Use the tested single interactive Bash
  `--rcfile` design, `ssh_wrapper`, and ordinary non-root SSH. No always-enabled
  security-sensitive Konsole D-Bus API and no mandatory `tmux`.
- Preserve the 87%-by-default **total** terminal-width budget, adjustable
  gutters, and right-hand visibility for desktop widgets and selecting windows
  behind Konsole. `mw l/r` and planned multiwindow placement must share one
  calculation, not diverging duplicate formulas.
- Distinguish logical desktop/slot and readable titles such as
  `joetoo_konsole_3.1` from per-run request IDs, managed IDs and KWin UUIDs.
  No class-only or title-only adoption/closing of unrelated windows.
- An unreachable SSH destination can still yield a **successful managed
  placeholder terminal**. Window/placement status and SSH transport status
  must not be conflated.
- `joetoo-kwind` OpenRC stop/restart must not close running Konsole, SSH, or
  other managed application windows. Keep daemon supervision independent of
  application process ownership; test this critical-path requirement early.
- Runtime registry/checkpoint (current session) and restorable `.conf`
  snapshot (reboot) have different purposes. `-r` launches **new** windows;
  `-x` must not erase the last-good snapshot. Persist only appropriate data,
  privately and atomically, with explicit reconciliation when needed.
- Unknown or mismatched UUIDs are **not** grounds for destructive fallback.
  Keep `-d` and `-x` scoped to positively registered, verified windows.

## Milestone workflow and review handoff

Use the numbered gates from `ARCHITECTURE.md` (e.g. 1.1, 1.2a, 1.3b)
and corresponding named task branches such as
`task/joetoo-kwin-step1.2a-openrc`. Start each branch from the latest
accepted baseline after maintainer feedback. Preserve POCs and human
integration changes. Work incrementally with non-destructive tests/mocks
before proposed native runs. Distinguish test evidence from estimates.

When a milestone is ready, provide a **complete diff**, validation results,
risks and remaining native tests. Then **explicitly request** the next required
authorization to commit, push and create/update the draft PR; do not merely
say nothing was committed and wait. No merge, deployment, protected-repository
write, or host administration is authorized by drafting in this workspace.

If a discovered fact changes the architecture, propose a focused update to
`ARCHITECTURE.md`, mark the decision as proposed until the maintainer agrees,
and include its effect on tests and later milestones in the review.
