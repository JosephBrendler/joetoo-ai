## Starting an AI engineering assignment

The root `AGENTS.md` is the governing entry point for AI contributors. An agent should inspect the current task's source repository and its own policies, discover `.agents/skills/*/SKILL.md` by metadata, and load only skills relevant to the task. The optional `joetoo-start` skill provides a repeatable orientation workflow when project context or skill selection is unclear.

Do not duplicate source code or establish a general `projects/` implementation tree here by default. Candidate implementations, test fixtures, and demonstrations can be developed in an explicitly authorized collaboration workspace, but official source and architecture belong in `joetoo-upstream`, and official Portage packaging belongs in `joetoo`, following human review and submission. An AI client needs actual repository access; a URL or standing instruction alone does not guarantee that current files have been retrieved.

## Norms for Collaboration cycle

This is the standing norm for development workflow for explicitly authorized collaboration projects under `workspace/`. It does not expand access to the official repositories.

1. **Maintainer supplies the baseline.** Push the candidate or returned integration result to joetoo-ai and identify its directory, branch or commit. Include relevant package metadata, manifests and other files changed during integration. Keep credentials, local authentication state, build trees, distfile caches and other unrelated machine files out of Git.
2. **Agent inspects baseline and task, prepares changes, and presents for review.** Fetch joetoo-ai, read applicable instructions, preserve local drafts, inspect the current baseline, and create a task branch. Research, implement and validate within the authorized workspace. Previously merged work is a baseline, not a reason to reuse its stale branch indefinitely. Show the complete diff including new files, summarize evidence and unresolved checks, and explicitly ask whether to commit, push and open/update a draft PR. State that this is the maintainer's review-before-publication boundary. Continue any useful authorized work while a response is pending; do not treat silence as permission.
3. **Maintainer authorizes; agent publishes.** Maintainer authorizes commit, push and potentially pull request generation, and agent responds as authorized.  Depending on maintainer decision, this may be one or two agent actions separated by discrete maintainer decisions.  When and as approved, commit the reviewed changes, push the task branch and create/update the draft PR in joetoo-ai. Return its URL. Reuse an open PR for the same iteration; use a new PR after the previous one has merged. Merging will normally be done by maintainer, otherwise by agent but with a separate approval.
4. **Maintainer integrates and tests.** Maintainer may merge and/or incorporate candidate material into joetoo or joetoo-upstream personally, following that repository's policy. Perform native checks and publication there. That work remains separate from the agent's actions in joetoo-ai.
5. **Maintainer returns integration feedback.** Following potential modification and publication in joetoo/joetoo-upstream, maintainer should push the actual incorporated candidate files back into the corresponding joetoo-ai project, along with a short note identifying what changed, native test results and remaining issues, to prevent divergence of the official and development baselines. Include the official source commit identifier when useful, without requiring the agent to access that repository. Feedback may be a direct maintainer commit to the collaboration baseline or a PR, according to preference.
6. **Agent starts the next iteration from subsequent maintainer tasking.** If so tasked, fetch and identify the feedback commit, reconcile pending proposals, and apply only the necessary follow-up changes. Do not replace human QA fixes or metadata with an earlier generated version. Repeat the review and explicit authorization step.

## Human-multi-agent task handoffs

- The turn-to-turn handoff document for any current task will be owned and reviewed by the maintainer and updated by agents in the workspace/projects/joetoo-kwin/task_<step_enum>/ directory (along with evidence, implementation guidance or other non-production documentation).
- Maintainer and agents are responsible for different parts of HANDOFF.md and are authorized to change only the sections they are responsible for.
- The stucture of HANDOFF.md will likely evolve, but its baseline minimal content will include --

|Section | Responsible party |
| --- | --- |
| Task ID, objective and accepted requirements | Maintainer, with cloud-agent drafting assistance |
| Base commit, branch and allowed paths | Maintainer-approved task setup |
| Authorized actions and stop conditions | Maintainer |
| Implementation progress and changed files | Acting implementation agent |
| Tests, outcomes and unresolved problems | Acting agent, supported by evidence |
| Review findings and recommendations | Reviewing agent |
| Acceptance and next authorized action | Maintainer |

The process description lives here; enforceable agent behavior lives in
[AGENTS.md](AGENTS.md). Project READMEs hold project-specific integration commands,
current baseline identifiers, and validation results rather than duplicating the
standing workflow.
