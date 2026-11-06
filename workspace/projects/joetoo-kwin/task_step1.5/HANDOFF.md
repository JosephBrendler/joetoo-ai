# Step 1.5 — Active task dispatch

> **REVIEW DRAFT — not an operative authorization.** Reconcile with the active
> Codex checkout and maintainer decisions before publishing or using for tasking.

**Active task:** Step **1.5c.5d, Increment 1**, managed RDP on native
Wayland: positive registration of the exact KWin viewer UUID **without placement**.

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`.
**Baseline:** verify actual branch point and current `HEAD`; the original
feasibility merge is `be8eb276`, not necessarily this branch's baseline.
**Current phase:** private registration core reported implemented/headless-tested;
review of a separately gated additive development interface is pending.

## Dispatch references

- **Rules:** repository-root, workspace and project `AGENTS.md` hierarchy;
  [workspace collaboration process](../../../README.md); approved role supplements.
- **Product and roadmap:** [ARCHITECTURE.md](../ARCHITECTURE.md).
- **Detailed current scope, tests and reserved gates:**
  [Step 1.5c.5 implementation scope](Step1.5c5_implementation_scope.md), §5A.
- **Historical outcomes and iteration index:** [task README](README.md).
- **RDP research and diagnostic findings:**
  [remote-desktop research](README_remote_desktop_research.md).

## Current authority / limits

**Previously authorized:** bounded, private, registration-only implementation
and non-destructive headless testing inside the maintainer-approved file envelope.
The source code, tests and complete diff remain in the active Codex checkout;
they are **not verified by this draft** or implicitly present on remote `main`.

**Requires a fresh maintainer decision:** exact public D-Bus development methods
(begin, child/evidence binding, poll, cancel), signatures, caller ownership,
child-PID/file-descriptor provenance and validation, isolation and failure
semantics. Production TLS/NLA trust policy is a separate approval boundary.

**Not authorized by this dispatch:** public-interface wiring before approval;
native graphical/network testing by agents; X11 SDL registration; placement;
configured `-o` RDP; new RDP clients; changes to TigerVNC/generic semantics;
install/deployment; changes to protected repositories; staging/commits/pushes/PR
or merge without an explicit publication approval.

**Stop on:** unsafe/ambiguous UUID correlation; source/history loss; insufficient
caller/process ownership verification; new interface or security decisions;
changes to accepted VNC or generic behavior; expanded paths or operational scope.

## Latest result and next decision

**Codex reported:** the private registration-only selector and headless tests
are complete. It stopped at the public-interface boundary; the candidate is not
yet operable as a native SDL managed registration. The exact uncommitted diff,
test outputs, D-Bus signatures and operation status need maintainer inspection.

**Next actor:** maintainer (optionally cloud reviewer). Review the precise
additive interface contract and source diff; approve, revise or defer it.
Codex resumes only once that bounded approval is granted. Native acceptance
and publication have later, separate gates.

**Maintenance rule:** replace this latest-result/next-decision block at a
material transition. Keep full reports and evidence in the approved task
README/research/acceptance records or review response; do not append an
iteration diary or historical authorization to HANDOFF.
