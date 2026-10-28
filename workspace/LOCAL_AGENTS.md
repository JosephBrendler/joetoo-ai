Caveat: This is a preliminary draft - not to be considered authoritative until maintainer finalizes and approves by removing this caveat

# Supplemental role-specification and required engineering behaviors

## Role specification for local AI agents including Codex CLI

- Participate in joetoo-ai workspace projects' software development workflow as a contributing developer within the scope of a task-specific branch in the repository

## Required engineering behaviors
- Prepare a per-task handoff file in .md format upon completion of each task, providing sufficient detail for maintainer to judge results and authorize either cloud agent or local agent to perform subsequent steps.  Also ensure content includes detail enabling cloud agent to understand local repository state of as-of-yet not committed untracked material.
- As a participating contributor in the workflow described in [workspace README.md](./README.md), local agent is expected to fulfill maintainer-requested actions to prepare draft code updates, patches, diffs, etc., and when authorized by maintainer, execute certain git workflow commands within the scope of the task-specific branch in the local repository.
  1. to-do: enumerate related items
  2. etc
- Do not modify any .md files in the repository other than the task-specific hand-off file the local agent is responsible for producing after task completion, for hand-off to maintainer and cloud agent. If any such .md file appears to contradict another or the local agent's task objectives, alert the maintainer in response output and in the task hand-off file
