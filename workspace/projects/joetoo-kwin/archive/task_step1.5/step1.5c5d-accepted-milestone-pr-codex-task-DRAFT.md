# DRAFT Codex task — Step 1.5c.5d accepted milestone PR readiness and next handoff

**Status:** Maintainer-review draft, not an instruction to act until issued. **Step 1.5c.5d is already ACCEPTED AND CLOSED (2026-11-11)**; this is publication/next-task preparation, not another implementation increment or acceptance gate.

## Objective

Prepare the accepted `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation` branch for a **single milestone PR targeting `main`**. Inspect the current local worktree, pushed branch and latest main; respect the maintainer's explicit publication decisions and repository AGENTS instructions. Do not change accepted behavior or rerun full native checks. Do not merge or create PR automatically without separately explicit maintainer authorization.

Read `task_step1.5/HANDOFF.md`, `task_step1.5/README.md`, `task_step1.5/step1.5c5d-increment5-final-native-acceptance-2026-11-11.md`, the prior Increment 5 native record, Increment 4 acceptance, the project architecture and scope, root/workspace/project AGENTS. Preserve historical evidence and any uncommitted maintainer edits.

## Work to perform when authorized

1. Confirm `git status`, current branch HEAD, remote tracking, `git log` and `git diff --check`. Compare against latest `main` and identify actual unrelated changes, conflicts, secrets, unsupported claims or other concrete PR blockers. Do not describe accepted limitations as new defects; no speculative redesign.
2. Ensure acceptance evidence, HANDOFF and README correctly state **Increment 5 accepted; Step 1.5c.5d closed**, with exact pointers and distinction between earlier pre-policy and final strict-policy native tests. Correct broken relative links if any. Make only necessary documentation fixes; never rewrite dated test transcripts to imply tests were rerun.
3. Produce a concise **PR title and complete PR description**, including scope (RDP exact UUID registration/placement, production configured `-o`, serial known-clean failure, configuration layering and security enum policies), acceptance evidence (X11 and Wayland, strict positive/negative native outcomes), Codex-reported 919 Python/161 JS and focused 185 tests, documented limitations and explicit exclusions. Include test provenance; avoid implying the PR closes Step 1.5d or packaging.
4. Recommend **one PR**, not artificially split accepted history; determine actual diff and CI state before advising merge. If requested and authorized to create PR, create it as a PR (prefer draft until reviewed). **Merge requires a separate explicit maintainer instruction.** Do not change `joetoo`/`joetoo-upstream` or deploy to systems.
5. Outline the shortest defensible next Step 1.5d integration objective from actual scope/architecture. **Do not begin Step 1.5d implementation** in this task. Explicitly carry forward later ebuild to-do: install `/etc/joetoo-kwin/BUILD` with `BUILD="${PVR}"` and source it in CLI instead of unrelated joetoolkit BUILD; source-tree fallback. Record as separate packaging backlog, not a 1.5c.5d defect.

## Deliverables and stop conditions

Report current HEAD and diff against `main`, an audit-ready PR title/body, exact blockers if any, and a compact proposed Step 1.5d next-assignment outline. Do not make a new stage/gate, broaden testing, update protected repositories, push, create a PR or merge without express authorization. The accepted RDP security policy is `rdp_security_protocol=nla` -> `/sec:nla`, `negotiate` -> omit `/sec:`, `rdp_certificate_policy=strict` -> `/cert:deny`, `prompt` -> omit `/cert:`. Do not reopen these decisions absent an actual observed defect.
