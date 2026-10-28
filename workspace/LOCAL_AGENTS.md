Caveat: This is a preliminary draft - not to be considered authoritative until maintainer finalizes and approves by removing this caveat

# Supplemental role-specification and required engineering behaviors

## Role specification for local AI agents including Codex CLI

- Participate in joetoo-ai workspace projects' software development workflow as a contributing developer within the scope of a task-specific branch in the repository

## Required engineering behaviors
- Prepare a per-task handoff file in .md format upon completion of each task, providing sufficient detail for maintainer to judge results and authorize either cloud agent or local agent to perform subsequent steps.  Also ensure content includes detail enabling cloud agent to understand local repository state of as-of-yet not committed untracked material.
- As a participating contributor in the workflow described in [workspace README.md](./README.md), local agent is expected to fulfill maintainer-requested actions to prepare draft code updates, patches, diffs, etc., and when authorized by maintainer, execute certain git workflow commands within the scope of the task-specific branch in the local repository.
1. Inspect and announce - Read current instructions and handoff; check branch, baseline and dirty files; report intended edits.
2. Act within scope - Implement focused source/test changes using existing joetoo conventions. Preserve unrelated and maintainer-owned changes.
3. Validate - Run approved checks; record actual outcomes, failures, skips and unperformed native tests.
4. Report and hand back - Summarize the complete diff, including untracked files, validation evidence, remaining risks and the proposed next actor.
 
| Activity | Default local agent policy |
| --- | --- |
| Inspect code and applicable instructions | Permitted |
| Edit source or tests | Only within the authorized task scope |
| Edit .md files including AGENTS.md, README.md, ARCHITECTURE.md | Prohibited unless separately authorized |
| Update the designated task handoff |Required and permitted |
| Modify protected joetoo or joetoo-upstream repositories | Prohibited under current policies |
| Commit, push, or open PR | Only with explicit publication authorization |
| Deploy, install packages, restart services | Separate operational authorization required |
| Report progress and validation after an iteration | Required |
- Local agents must not modify Markdown documentation, including AGENTS.md, README.md, ARCHITECTURE.md, policy or skill files, unless the maintainer explicitly authorizes those particular documentation changes. The designated task handoff is an exception, limited to sections assigned to the local agent. Maintainer-owned authorization and requirements sections must not be silently rewritten.
- Do not discard, reset, clean, stash, overwrite, rebase or otherwise conceal existing working-tree changes without explicit authorization. Inspect and preserve staged, unstaged and untracked material before changing branches or synchronizing source.
- Tools such as dev-util/joetoolkit's validate_scripts() and MCP servers are execution facilities, not authorization authorities.
