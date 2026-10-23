# joetoo-ai
joetoo repository for ai-relevant instructions and skills available to tools like ChatGPT, Codex, Gemini, Copilot, etc. through their respective mechanisms

**Shared, version-controlled instructions and resources for AI-assisted work in the joetoo ecosystem.**

`joetoo-ai` is the authoritative home for reusable AI-facing guidance intended for use with ChatGPT, Codex, Gemini, Copilot, and other AI assistants **through each tool's supported integration and discovery mechanisms**.

Its purpose is to improve continuity, focus, accuracy, and consistency in AI contributions to joetoo engineering work, without transferring development authority from human maintainers to autonomous agents.

## Goals

- Preserve project conventions, constraints, and established design decisions across tools, conversations, and computers.
- Make AI assistance evidence-based, appropriately scoped, reproducible, and reviewable.
- Reduce repeated explanation of the joetoo environment, conventions, idioms, styles, and correction of unsupported assumptions.
- Develop reusable skills for investigation, architecture review, documentation, code review, and related advisory workflows.
- Maintain clear boundaries among project policy, reference material, skills, tool access, and agent orchestration.
- Evaluate whether AI assistance actually improves engineering outcomes.

## Relationship to other joetoo repositories

| Repository | Responsibility |
| --- | --- |
| [`joetoo`](https://github.com/JosephBrendler/joetoo) | Gentoo Portage overlay: ebuilds, eclasses, profiles, metadata, and packaging of joetoo software. |
| [`joetoo-upstream`](https://github.com/JosephBrendler/joetoo-upstream) | Upstream source for joetoo utilities, development tools, platform support, and system-building automation; authoritative architecture documentation is maintained here. |
| `joetoo-ai` | Cross-project AI instructions, reusable advisory skills, workflow guidance, and evaluations. |

`joetoo` and `joetoo-upstream` deliberately use corresponding category/package organization. AI guidance must preserve this separation: software and its architecture live with the applicable source project, Portage packaging lives in the overlay, and reusable AI-specific procedures live here.

`joetoo-ai` **does not replace** either source repository's README, architecture documentation, licensing information, or AI policy. Repository-specific documentation and policy remain authoritative for work concerning that repository.

## AI participation and human control

The published AI policies for both [`joetoo`](https://github.com/JosephBrendler/joetoo/blob/master/doc/AI_Policy.md) and [`joetoo-upstream`](https://github.com/JosephBrendler/joetoo-upstream/blob/master/doc/AI_Policy.md) currently permit **advisory AI use only**. AI can assist with research, diagnosis, design discussion, review, and suggested changes, but agents must not modify those repositories, execute their development workflows, or commit changes. Human developers perform and verify repository modifications and remain responsible for design, correctness, provenance, and licensing. AI and human developers may use shared resources and file system structures (in the abstract - development environment) other than the joetoo and joetoo-upstream repositories in which to collaborate on material  underdevelopment, understanding that when mature, human action will make the official submission/commit/push to the official repositories.

An AI skill, MCP server, connector, or harness does not confer permission to bypass those policies. Any future change to the permitted role of AI must be made explicitly in the affected repository's own policy.

## How the pieces fit together

- **Project policies and architecture documents** define facts, requirements, constraints, and recorded decisions.
- **`AGENTS.md`** defines standing instructions for AI contributors working with this repository.
- **Skills** package task-specific instructions, examples, and references for repeatable workflows.
- **MCP and other integrations** can expose approved resources and tools, but access and authorization remain separate questions.
- **Harnesses** can coordinate context, workflow steps, evaluation, and handoffs while remaining within project policies.

A skill describes *how* to approach a task; it is not necessarily enabled merely because its files are present in Git. Every client needs a supported way to discover or import the relevant material.

## Proposed repository layout

The directories below describe an **incremental target structure**, not features already implemented:

```text
joetoo-ai/
├── README.md
├── AGENTS.md
├── policy/                 # Shared guidance, not overrides of source-repository policies
├── .agents/
│   └── skills/             # Reusable task-specific SKILL.md packages
├── workflows/              # Advisory work patterns and human handoff templates
├── evaluations/            # Representative cases and quality criteria
└── integrations/           # Future client-specific setup and MCP documentation
```

Initial skill candidates include Bash source review, Portage/ebuild analysis, platform architecture review, and build-failure classification. Their detailed rules should be written only after examining representative joetoo sources and existing conventions.

## Using this repository across computers and AI clients

GitHub is the version-controlled **source of truth**. Local clones may be used on any development machine; `git fetch`/`git pull` synchronize them when run.

Availability to an AI client is a separate concern:

- A local coding assistant must load applicable instructions or install/link skills in locations it recognizes.
- A cloud-hosted agent must have access to an authorized repository checkout or configured integration.
- ChatGPT Project instructions and uploaded sources can provide shared conversational context, but a Project Source is not automatically an installed executable skill.
- Other AI tools may need their own adapter files, configuration, or import procedures.

Distribution and client setup should be documented under `integrations/` when implemented. Do not assume that a GitHub push automatically updates every agent session or ChatGPT Project.

## Working principles

1. **Evidence before conclusions.** Inspect the relevant source, documentation, logs, and configuration; distinguish observations from hypotheses.
2. **Respect scope.** Prefer targeted recommendations and preserve established behavior and interfaces unless a change is explicitly under discussion.
3. **Keep decisions explicit.** Distinguish settled architecture, proposed alternatives, open questions, and deprecated assumptions.
4. **Honor platform policy.** Gentoo, Portage, OpenRC, multiple architectures, board/platform abstraction, and stable-keyword practices are important context; verify the actual policy and state for each task.
5. **Report uncertainty and verification honestly.** Never present unperformed tests, uninspected files, or inferred runtime behavior as verified facts.
6. **Human ownership.** AI assists analysis and preparation; authorized human developers make changes to the protected code repositories under their respective policies.

See [`AGENTS.md`](AGENTS.md) for the standing instructions applicable to AI work in this repository.

## Initial milestones

1. Establish and review `README.md` and `AGENTS.md`.
2. Identify shared policies and links to authoritative source-repository documentation.
3. Draft one narrow advisory skill and test it against a real, read-only review case.
4. Record concrete evaluations: accuracy, scope adherence, unsupported assumptions, and value of the result.
5. Add client-specific installation instructions only after validating them on a real client.
6. Consider read-only MCP integrations and more elaborate harness design only where they solve a demonstrated problem and comply with project policy.

## Status

**Bootstrap stage.** The repository establishes shared guidance; proposed skills, integrations, and harness capabilities are not implied to be installed or operational.
