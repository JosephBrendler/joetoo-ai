# Step 1.5c.5 — Remote resources and graphical remote desktops: implementation scope and outline

**Status:** Proposed scope for maintainer review. This document does **not** authorize implementation, repository edits, network connections, native GUI operations, deployment, publication, or a new task branch. Increment-specific authorization belongs in a subsequently approved `task_step1.5/HANDOFF.md`.

**Baseline:** The maintainer has accepted and merged the bounded Step 1.5c.4 implementation. The maintainer reports committing an updated `ARCHITECTURE.md` and `README.md` but **not yet merging those documentation changes** at the time this scope was drafted. Before opening a task branch, verify accepted `main`, its exact SHA, this scope's consistency with the merged architecture, and working-tree cleanliness. The historical native-tested 1.5c.4 implementation baseline is `a3c50fc`; do not mistake it for the future 1.5c.5 branch point.

**Proposed branch:** `task/joetoo-kwin-step1.5c5-remote-access` (name and base require maintainer approval).

**Authorities:** Current project `ARCHITECTURE.md` (particularly §§3–7, 10–11), project/root/workspace `AGENTS.md`, and the future active HANDOFF. `Step1.5c4_implementation_scope.md` is historical design evidence, not renewed authorization. The existing `task_step1.5/HANDOFF.md` closes 1.5c.4 and does not open 1.5c.5.

## 1. Objective and boundaries

Extend the accepted configured `joetoo-kwin -o` launch workflow to **remote file browsing** and **graphical remote desktops**, while reusing its existing KWin X11/Wayland positive managed-window identity, original intended desktop/slot, shared geometry, application-independent `under`/`panel`/`over` layers, initial stacking/focus, and conservative concurrency/partial-failure semantics.

The selected sequence is:

1. **1.5c.5a — Dolphin SFTP:** Implement local Dolphin browsing remote files using an approved endpoint/URI contract.
2. **1.5c.5b — TigerVNC over SSH:** Inspect the maintainer's *already working*, KDE application-launcher-integrated VNC-over-SSH proof of concept, verify compatibility and actual security properties, then adapt its command and lifecycle into managed `joetoo-kwin` launch.
3. **1.5c.5c — RDP feasibility and decision:** Evaluate each viable graphical RDP client and compare security, usability, native compatibility and managed-window integration; recommend the best candidate or defer. An RDP implementation is **not** authorized by this scope. If demonstrated reliable and secure, RDP is the maintainer's preferred future **primary graphical remote access**, with VNC retained as a legacy/compatibility alternative as appropriate.

Application startup, managed KWin window registration/placement, remote transport establishment, authentication, and session lifecycle are **different outcomes**. A successfully positioned window does not prove the remote connection is authenticated, secure or functional. Likewise, remote failure does not automatically make valid window placement a failure. Conversely, a transport that succeeds without a positively identified KWin window is not evidence of managed-window acceptance.

**Not included without later authorization:** broad launch plugin architecture; all alternative file managers/terminals; generic credentials store; network/VPN management; managed close (`-a/-d/-x`), checkpoint/recovery, durable restore, ebuild packaging; broad broker/resident API redesign; and Step 1.5d integrated regression as implementation work.

## 2. Accepted baseline and inspection prerequisites

The accepted Step 1.5c.4 infrastructure already supplies: config discovery (`-f`, XDG user-first and system fallback); `desktop_session_list` four-field recipes with optional fifth `layer`; derived per-desktop logical slots; virtual-desktop capacity provisioning after confirmation; Dolphin `local` new-window launching; positive UUID/PID correlation; placement readback; first-appearance desktop-group ordering; initial owned-window stacking and bounded one-time focus; duplicate managed `(desktop,slot)` rejection; invocation-wide lock; and original local Bash continuity for Konsole SSH. These are *reuse contracts*, not an invitation to replace the machinery.

At the start of each increment, inspect **current** planner, launcher, CLI, session-Bash startup, broker, KWin resident, tests, installed helpers, template and relevant architecture. Inspect relevant archived POCs before proposing a new launch route. Establish current program/mode support from source and tests rather than copying obsolete descriptive inventories in prior scope documents. Preserve established D-Bus signatures unless an explicitly approved, source-grounded extension is necessary.

The configuration grammar remains `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]`; **slot is derived, not a sixth field**. A program/mode combination is executable only after explicit preflight support and target validation are implemented. `-c` must remain an application-free descriptive dry run. An executable `-o` plan containing unsupported/invalid entries must reject **as a whole before confirmation or any application, network, tunnel, or desktop-provisioning side effects**.

## 3. Increment 1.5c.5a — Dolphin SFTP

**Intended recipe:** `DESKTOP|dolphin|sftp|TARGET[|LAYER]` launches a **local Dolphin** instance displaying a remote location via KIO SFTP. It does not run Dolphin remotely, forward a remote GUI, or delegate SFTP session health to KWin.

### 3.1 Inspect and decide the endpoint contract before coding

Propose and obtain maintainer approval of a documented, unambiguous `TARGET` grammar with examples and rejection cases. Cover hostname/FQDN, optional user, optional remote path, optional port if required, IPv4, bracketed IPv6, absolute versus relative remote paths, percent-encoding of URL components, whitespace, reserved delimiters, and avoidance of ambiguous `host:path` constructions. Decide whether canonical SFTP URIs, a restricted shorthand, or both are supported. Do not presume that shell tilde expansion, embedded credentials, SSH aliases, KIO URL syntax, and scp-style addressing are interchangeable. Decide and document SSH key/agent and host-key interaction; never interpolate untrusted strings as shell commands or place passwords in argv/config/logs.

### 3.2 Implement the narrowly approved launch

Reuse the current Dolphin `--new-window`, argument-array, positive process/UUID correlation, managed-slot guard, desktop verification, and initial-layout transaction. Confirm the installed Dolphin/KIO version and behavior; when a launch delegates to an existing window or produces an ambiguous PID/UUID, fail conservatively rather than adopting it. Distinguish invalid recipe, missing executable/KIO support, window-launch failure, window-placement failure, KIO authentication prompt, inaccessible remote directory, connection timeout and remote listing success to the extent observable. **Do not invent transport telemetry** if existing interfaces cannot report it; state uncertainty truthfully.

### 3.3 Acceptance

Headless: valid/invalid endpoint table; URI construction and escaping; no command evaluation/secret leakage; complete-plan preflight; cancellation; launch-argv capture; ambiguous/delegated window rejection; propagation of independent placement versus remote-access results; preservation of existing local-Dolphin and Konsole tests.

Maintainer-native on `gmki91` X11 and `q552u01` Wayland: reachable SFTP location with visible file browsing, unavailable/invalid target, authentication behavior, positive new-window UUID, exact desktop/slot and placement, layer behavior, and no adoption of an already-running Dolphin. Report which outcomes are directly observable versus not instrumented.

**Gate:** Acceptance of 1.5c.5a and a separate explicit authorization precede work on 1.5c.5b.

## 4. Increment 1.5c.5b — TigerVNC over SSH

**Intended recipe:** `DESKTOP|vncviewer|ssh|TARGET[|LAYER]`, with the viewer running locally and a VNC stream protected by authenticated SSH. The exact target grammar and executable are subject to POC inspection and maintainer approval. **Direct or exposed raw VNC is prohibited**, including on a trusted LAN.

### 4.1 Start from the working workflow

Inspect `archive/tigervnc-poc/vnc-via-ssh-launch`, the *actual* KDE `.desktop` launcher/command maintained by the user, installed TigerVNC binary/version/options, SSH configuration, and representative server behavior. The maintainer reports that this workflow already functions via the KDE application launcher; treat that as a useful native POC, **not** proof of confidentiality, endpoint validation, tunnel cleanup, or managed-window identity. The objective is to translate the existing working invocation into the managed launcher with minimal behavioral change—not redesign working SSH unnecessarily.

Produce a concise POC-to-managed-launch mapping: original command and dependencies; target parsing; SSH authentication/host-key behavior; whether viewer `-via`/equivalent is appropriate or explicit `ssh -L` is necessary; listener binding; child/tunnel lifetime; viewer startup window/authentication dialog versus actual managed viewer; expected PID/UUID correlation; cleanup and retry.

### 4.2 Security and lifecycle contract to approve

Specify and review: SSH destination and VNC server/display/port grammar; credentials and known-hosts policy; allowed forwarding endpoint; **loopback-only** VNC listener; prevention of exposing secrets in logs/process lists; how a local forwarded port is allocated and conflict-checked; tunnel readiness; timeout/cancellation; shell/child process and file-descriptor ownership; deterministic teardown when the viewer closes or launch fails; and distinction between failure to launch a viewer and failure to connect/authenticate remotely. Never disable host-key verification or automatically accept unverified host keys. Do not presume `ssh_wrapper` or `swr` is appropriate for a background tunnel; inspect their actual contract first. If POC safety or correlation cannot be established, stop and propose specific remediation before implementation.

### 4.3 Implement and accept

Implement only the approved command, target grammar and minimal lifecycle support. Reuse the positive UUID-owned broker placement and initial layer/focus infrastructure; do not enroll authentication popups, unrelated viewers or class-only matches. A viewer that exits or changes window identity during authentication must be handled truthfully. Preserve whole-plan preflight and invocation-lock discipline; do not leak file descriptors or leave orphaned tunnel processes.

Headless: argv and tunnel-command construction; quoting/validation; explicit security options; cancellation, unreachable host, authentication failure, port collision, viewer exit and cleanup; PID/UUID ambiguity; initial-layout and existing Konsole/Dolphin regression.

Maintainer-native on both backends: the working SSH-protected desktop connection, authentication-dialog lifecycle, registration and placement of the **actual viewer window**, manual rearrangement persistence, failure/retry and tunnel teardown. Where native tunnel inspection is possible, verify the VNC forwarding endpoint is loopback-only and no direct VNC connection escaped the SSH tunnel. Do not infer cryptographic assurances from successful display alone.

**Gate:** Document accepted implementation and residual security limitations, if any, before 1.5c.5c evaluation. Do not block RDP comparison on optional TigerVNC enhancements once the bounded POC translation is accepted or explicitly deferred.

## 5. Increment 1.5c.5c — Comparative RDP feasibility and decision

**Primary goal:** Determine whether a reliable and demonstrably secure RDP workflow should become joetoo-kwin's **preferred graphical remote-access method**, superseding legacy TigerVNC-over-SSH as the usual choice. This increment is a **feasibility/design study and recommendation**; no RDP executor is authorized until the maintainer chooses a candidate, approves program/mode/target semantics, and grants a separate implementation scope.

### 5.1 Examine every viable graphical RDP candidate

At minimum inspect **KRDC, Remmina and available FreeRDP graphical clients** (including `xfreerdp` and `wlfreerdp` or version-appropriate equivalents). Add another concrete candidate if installed and relevant; do not assert installation or support without verifying current binaries/packages. Include KRDC's VNC support where useful to compare whether one graphical client can replace separate viewer workflows. Check availability and installed feature flags separately on **both** `gmki91` and `q552u01`.

For **each candidate**, provide an evidence-backed comparison of:

1. Installed package/version, USE/build features, executable names, native X11/Wayland functionality and dependency weight.
2. Launch syntax and complete proposed endpoint grammar (server, port, user/domain, screen dimensions, path/profile, relevant options), and whether it can be launched without unsafe shell evaluation or exposed secrets.
3. Protocol/security: TLS/NLA or other applicable authentication, certificate identity and verification policy, downgrade/exception behavior, credential handling, encrypted transport and any unsupported assumptions. **`tls` alone is not an RDP mode contract.** Avoid claiming protocol security merely from a product name or GUI setting.
4. Unique local window creation and KWin PID/UUID ownership; whether an existing client process delegates or reuses tabs/windows; authentication/preconnection dialog versus steady-state remote desktop window.
5. Session lifecycle: connection error, authentication failure, timeout, exit, reconnection, orphan processes, and whether a usable managed window persists for retry.
6. KWin geometry, layer, focus and virtual-desktop compatibility with accepted `joetoo-kwin` behavior on both native backends.
7. Usability and tradeoffs: clipboard, resizing, multiple monitors, scaling, keyboard shortcuts, network resilience, session persistence, server interoperability, maintenance and package complexity, and suitability for routine joetoo remote administration.
8. Relative engineering effort and expected operational value compared with the working TigerVNC-over-SSH option.

Produce a **side-by-side comparison**, including a capability/confidence rating supported by specific documentation, installed-client inspection or maintainer-run native evidence; label unsupported and untested claims. Identify a preferred candidate **or** explain why no candidate is currently acceptable. Recommend whether to implement RDP during a newly authorized follow-up increment of 1.5c.5 or defer it. State which existing VNC functionality should remain for compatibility.

### 5.2 Evidence and decision gate

Agent-side work is read-only capability inspection and non-network feasibility analysis unless the maintainer specifically authorizes mock tests. Actual remote desktop sessions, credential/certificate interactions and native GUI trials are maintainer-operated. Provide a compact, reproducible native evaluation plan rather than attempting unauthorized connections. If a candidate cannot establish secure server identity or trustworthy managed-window identity, report the blocker and alternative; do not weaken TLS verification to make a demonstration pass.

**Stop before RDP implementation.** A separate maintainer decision must identify client, recipe grammar, certificate/authentication policy, expected window lifecycle, branch/file permissions and native tests.

## 6. Other newly available application candidates — deliberate evaluation, not wholesale implementation

The maintainer reports the following installed on `gmki91` as of November 1, 2026: **QTerminal 2.4.0; Krusader 2.9.0; FileZilla 3.70.6; Nautilus 49.6-r1; Nemo 6.6.4; KRDC 26.04.3; Midnight Commander 4.8.33.** This is maintainer-reported package evidence, **not** proof of executable/window behavior or installation on `q552u01`. KRDC was built with `rdp ssh vnc wayland` USE flags; `mc` was built with `-sftp`.

During the corresponding investigation, evaluate each additional candidate's feasibility and possible utility **without treating it as approved implementation**:

| Candidate | Specific questions / prospective benefit |
| --- | --- |
| QTerminal | Could its terminal/SSH/local workflows retain an original usable shell and provide reliable independent KWin window/PID identity? What differs from established Konsole? |
| Krusader | Can it supply useful dual-pane local and remote-file browsing via KIO/SFTP with reliable new-window identity? |
| FileZilla | Can its SFTP capabilities be configured and launched safely as a distinct managed GUI without leaking credentials or reusing ambiguous windows? |
| Nautilus | What GVfs/GNOME dependencies and URI/instance-delegation behavior affect managed KWin X11/Wayland launches? |
| Nemo | How do its remote filesystem and new-window behavior compare with Dolphin, and what are its Wayland dependencies/limitations? |
| KRDC | Compare RDP/VNC/SSH capabilities and window identity; include fully in the RDP study. |
| Midnight Commander (`mc`) | It is a **terminal UI**, not a standalone graphical KWin window. Assess whether launching `mc` **inside** a managed Konsole or QTerminal provides value as an optional local/remote file-manager workflow. With installed `-sftp`, do **not** assume current SFTP functionality; report whether rebuilding with `sftp` or using a different supported backend would justify any integration. |

Report for each: executable presence on each host, launch grammar, window ownership/delegation, remote protocol support, security/user experience, extra dependencies, and a concrete **implement / investigate later / defer / reject** recommendation with rationale. Avoid a sprawling survey if it would delay the three selected increments: this is a bounded comparative appendix to feasibility work, not a requirement to implement every candidate. The maintainer may promote an individual candidate in a later explicit scope decision.

## 7. Shared acceptance, failure policy and test matrix

### 7.1 Invariants for every approved implementation

- Keep `-c` non-launching; full `-o` syntax/program/mode/target verification must occur **before** confirmation, application, tunnel or network side effects. Trust boundary: sourcing a trusted Bash config may itself have side effects, so `-c` is not a sandbox for arbitrary config code.
- Preserve `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]`, planner-derived slot, grouped launch order, four-panel and explicit-layer budget behavior, graphical exposure warnings, and one-time stacking/focus, without re-enforcing manual user changes.
- Preserve all existing public D-Bus signatures unless a narrowly approved additive interface is justified. Broker must never guess geometry, transport connectivity or ownership. No PID/title/class-only adoption.
- Reuse launch serialization, positive correlation, bounded transactions, consistent AAR reports, successful/partial/incomplete distinction, and the policy that known isolated failures may continue while unresolved Busy/ownership uncertainty stops further submission. No automatic rollback of already registered windows.
- Maintain separate statuses for launch process, real window identity, placement, stacking/focus, remote connection, authentication and process/tunnel lifetime, *only* where actually observable. Do not fabricate a transport telemetry API or conflate window presence with connection success.
- Ensure new timing/resource limits are configurable, validated, bounded and represented in the template; avoid assuming Bash global variables appear automatically in broker/resident state.
- Do not embed credentials in config, argv, diagnostic dumps or error messages. Respect server certificate and SSH host-key verification; never use insecure fallbacks simply to get a native PASS.
- Do not create a generic secret manager, broad firewall/VPN detector, arbitrary remote-command executor or shared transport framework without a separately justified need.

### 7.2 Test expectations

| Category | Headless agent-permitted evidence (subject to HANDOFF authorization) | Maintainer-native X11 and Wayland evidence |
| --- | --- | --- |
| Preflight | grammar/escaping/unsupported-plan rejection, cancellation, missing executable | invalid/unsupported plan changes nothing; user confirms valid plan |
| Identity | exact request/PID/UUID correlation, class-only ambiguity rejection, managed slot conflict | actual new window, desktop/slot, UUID and registry presence |
| Layout | grouped geometry/stack/focus and no continuous enforcement | initial layers and preferred focus; manual movement survives switching desktops |
| Remote resource | SFTP URL/argv, failure classification, mock timeout | remote listing/authentication and unreachable targets |
| VNC tunnel | command/options, only-loopback intent, cancellation/exit cleanup under mock processes | protected actual session, tunnel endpoint, auth dialog and teardown |
| RDP study | documented inspection and comparison; no implementation by default | maintainer-run pilot to establish secure and usable candidate behavior if approved |
| Compatibility | existing Python/JS cases, Bash syntax, ShellCheck, link/diff checks | no regression to Konsole SSH placeholders and original local Bash continuity |

Reuse previously accepted 1.5c.4 native evidence for unchanged contracts rather than rerunning the full graphical-layer battery in every subincrement. New network/GUI work needs actual maintainer-native acceptance on both backends. Record PASS/FAIL/NOT TESTED **by host/backend and exact implementation SHA**; separate application/placement success from remote transport/authentication success. Document missing native evidence honestly.

## 8. Authorization, stop conditions and subsequent milestone

**This scope is a proposal, not operative agent authorization.** The maintainer and cloud AI will prepare a new 1.5c.5 `HANDOFF.md` only after reviewing this scope and the actual merged architecture. That document must specify: accepted baseline SHA and branch, next actor, precise editable files and narrow increment, permitted headless tools, explicit native/network authority, owner of tests, escalation criteria, and separate commit/push/PR/merge approvals. Protected `joetoo` and `joetoo-upstream` remain advisory/read-only under their current policies.

**Proposed authorization sequence:**

1. Approve the **Dolphin SFTP grammar/increment** and allow only bounded 1.5c.5a implementation/test paths once prerequisites are resolved. If the grammar needs material decisions, authorize a short read-only design gate first, then approve the interface explicitly.
2. Following maintainer review/native acceptance or explicit deferral of 1.5c.5a, authorize **TigerVNC-over-SSH POC inspection and adaptation** as 1.5c.5b. Its existing working KDE launcher is the starting point; its actual host-key, port exposure, lifetime and security contract must be verified before implementation.
3. After 1.5c.5b acceptance or documented deferral, authorize **1.5c.5c RDP feasibility/comparative review**, including inspection of the newly installed candidates. **RDP implementation requires a further explicit authorization** selecting the client, endpoint grammar, certificate policy, and tests.
4. When the selected integrations are accepted or explicitly deferred, define and authorize **1.5d integrated X11/Wayland regression** separately. Do not automatically make 1.5d a feature-implementation milestone.

**Stop/escalate** on: conflicting task scope or repository policy; uncertain source baseline; unsupported/ambiguous endpoint semantics; inability to preserve positive window identity; unresolved cross-process Busy or ownership uncertainty; unsafe credential/certificate/host-key behavior; VNC traffic outside the approved SSH protection; orphaned tunnel risk; unapproved broker/resident API edits; need for deployment, native connections or protected repository writes; or a proposed departure from accepted layer, shell or configuration contracts. Document concrete findings and obtain the maintainer's decision before extending scope.

**Next actor:** maintainer reviews this proposed scope with cloud AI, records accepted decisions, merges approved planning documents as appropriate, and only then prepares a new, specifically authorized 1.5c.5 HANDOFF for the first bounded increment.
