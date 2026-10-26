## Start-of-assignment discovery

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
- When drafting code, make clear comments throughout; explain every step, call, and assignment clearly, as if written for someone who has little to no experience with the associated syntax. It will be easier to trim comments later than to interpret and try to apply comments to unreadable code later.
- Use an existing isolated checkout. Use a task branch from the current accepted
  baseline; start a fresh follow-up branch when the earlier PR has merged.
  Do not create a worktree unless the user requests one.
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
