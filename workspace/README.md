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

- The turn-to-turn handoff document (HANDOFF.md) for any current task will be owned and reviewed by the maintainer and updated by agents with access to it, in the workspace/projects/joetoo-kwin/task_<step_enum>/ directory.
- HANDOFF.md is the canonical active-task dispatch and authorization record. It contains the minimum information necessary to identify the current task, accepted baseline, permissions, stop conditions, recent status and next actor. Detailed implementation progress, validation evidence and historical decisions belong in task status and evidence documents referenced by HANDOFF. Agents update HANDOFF only when the current execution state, authority or next action changes materially.
- The stucture of HANDOFF.md will likely evolve, but its baseline minimal content will include --

|Section | Content description |
| --- | --- |
| Task ID and approval| (maintainer only) text string naming and enumerating the task, along with reference to agent-authored file(s) requesting or recommending this |
| Objective, scope, requirements | Summary and reference to documents detailing this |
| Base commit, branch and allowed paths | as stated |
| Authorized actions and stop conditions | as stated |
| Implementation progress | Summary and reference to file detailing this |
| Review findings and recommendations | Summary and reference to file detailing this |
| Latest result / recommendation | Summary of what is pending maintainer review / approval, including which actor produced it and a reference to agent-authored document(s) detailing the work, on which branch, revision, status, whether changes are committed, uncommitted or published, where the complete diff and test evidence can be obtained, and what decision or action is required. (i.e. these details are in the referenced document, only a summary is in HANDOFF.md) |
| Acceptance / approval decisions | (maintainer only) Summary and reference to agent-authored file detailing and requesting this |

The process description lives here; enforceable agent behavior lives in
[AGENTS.md](AGENTS.md). Project READMEs hold project-specific integration commands,
current baseline identifiers, and validation results rather than duplicating the
standing workflow.
