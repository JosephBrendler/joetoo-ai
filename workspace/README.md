## Starting an AI engineering assignment

The root `AGENTS.md` is the governing entry point for AI contributors. An agent should inspect the current task's source repository and its own policies, discover `.agents/skills/*/SKILL.md` by metadata, and load only skills relevant to the task. The optional `joetoo-start` skill provides a repeatable orientation workflow when project context or skill selection is unclear.

Do not duplicate source code or establish a general `projects/` implementation tree here by default. Candidate implementations, test fixtures, and demonstrations can be developed in an explicitly authorized collaboration workspace, but official source and architecture belong in `joetoo-upstream`, and official Portage packaging belongs in `joetoo`, following human review and submission. An AI client needs actual repository access; a URL or standing instruction alone does not guarantee that current files have been retrieved.
