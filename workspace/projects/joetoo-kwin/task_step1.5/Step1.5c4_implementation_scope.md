# Step 1.5c.4 — Graphical launch, remote display, and underlay: implementation scope and outline

**Status:** Maintainer approved the 1.5c.4 *scope direction* on 2026-10-31 at 09:56:37; the decisions below refine that direction for final maintainer review. **This document is not an authorization to edit implementation files, conduct native/remote operations, or publish changes.** Increment-specific authority resides in `HANDOFF.md`.

**Baseline:** Accepted and merged `joetoo-ai/main` following Step 1.5c.1–1.5c.3 (PR #25). Verify current `main`, exact commit, and clean state before creating a new task branch.

**Proposed branch:** `task/joetoo-kwin-step1.5c4-graphical-launch`; creation requires separate maintainer authorization in `HANDOFF.md`.

**Authorities:** `../ARCHITECTURE.md` (§§4–7, 9, and gate 1.5c.4); `HANDOFF.md`; applicable repository, workspace, and project `AGENTS.md`. `Step1.5c_implementation_scope.md` records completed work, not renewed permissions.

## 1. Objective and boundaries

Extend configuration-driven `joetoo-kwin -o` to positively identified graphical windows, beginning with **Dolphin local and Dolphin SFTP**, then **TigerVNC viewer over SSH**, while preserving shared desktop/slot policy, unique KWin UUID correlation, placement verification, conservative concurrency/duplicate guards, and usable graphical underlay. Validate supported paths on `gmki91` (KWin X11) and `q552u01` (KWin Wayland).

Keep distinct: **program** (local executable), **mode** (defined action/transport), **target** (mode-specific resource or endpoint), **intended desktop/slot** (configured logical identity), and **actual KWin UUID/desktop/geometry** (observed runtime identity/state). In particular, `dolphin|sftp|TARGET` starts **local Dolphin browsing remote files**; it does not execute remote Dolphin or forward its GUI. Broker ownership, layout calculations, and SSH/session health remain separate responsibilities.

## 2. Verified existing baseline and source dependencies

- The Bash planner currently accepts the *descriptive* mode names `ssh`, `swr`, `via-ssh`, `local`, and `direct`; it does **not** currently accept `sftp` or `tls`. Its non-Konsole `underlay-proposed` rectangle uses `graphical_*_percent`, without enforcing KWin stacking or focus. The planner numbers **all** entries per desktop for logical slots, while only Konsole entries consume terminal geometry positions.
- The current `-o` executor supports only `konsole:ssh` and `konsole:local`. For the latter, a nonempty executable target (e.g. `btop`) is currently required: empty-target `konsole|local|` is **not yet implemented**. Unsupported recipes cause whole-plan preflight rejection before confirmation or application launch; `-c` remains descriptive for accepted syntax.
- The broker requires positive registration and unambiguous PID/UUID correspondence; a program that delegates window creation to an existing process is not evidence of ownership. Step 1.3b native evidence found Dolphin `--new-window` could match on both backends; reconfirm using currently installed executable versions.
- The accepted `(intended desktop, slot)` association and duplicate guard persist through manual window movement; existing single-invocation `flock`, broker transaction safety, exact placement verification, best-effort isolated-failure continuation, and unresolved-state stopping remain intact.
- The existing `archive/tigervnc-poc/vnc-via-ssh-launch` was supplied as a maintainer reference, but its current content **was not retrievable from published `joetoo-ai/main` during this review**. The implementing agent must inspect the actual file when supplied; do not infer its command syntax, configuration, or security posture.

## 3. Proposed implementation increments (separately reviewable)

### 1.5c.4 prerequisite — KWin virtual-desktop capacity verification and provisioning

Before initiating configured application launches, `joetoo-kwin -o` shall inspect the actual virtual desktops available in the current KWin session and ensure that every desktop referenced by the validated launch plan exists. The minimum required desktop count is the **maximum intended desktop number** among all planned entries, not the number of launch entries or distinct desktop numbers referenced.<br>
1. After validating the full launch plan and completing non-mutating preflight, query the running KWin session for its current virtual-desktop inventory and available creation mechanism. Distinguish the configured `desktop_limit` validation ceiling from actual runtime desktop availability.<br>
2. Report the current and required desktop counts before requesting confirmation. When additional desktops are necessary, include their creation explicitly in the proposed launch operation.<br>
3. Do not create desktops during `-c`, during preflight, or when the user declines confirmation. Preserve `-c` as a non-mutating, usable dry run without requiring an active KWin session; it may show the required maximum desktop number.<br>
4. Following affirmative confirmation, recheck actual desktop availability and append only the additional desktops required. Do not reduce the desktop count, rename or reorder existing desktops, switch the active desktop unnecessarily, or change existing window assignments.<br>
5. Verify successful creation and availability of every required intended desktop before launching the first configured application. A D-Bus method returning successfully does not, by itself, establish that KWin has completed the requested change.<br>
6. If KWin cannot supply or create the necessary desktops, fail the configured launch before starting application windows. Report the required count, observed count, and reason. If partial desktop creation occurred, report that state without automatically deleting the created desktops.<br>
7. Preserve the launcher-wide lock throughout preflight, confirmation, provisioning, and application launch. Recheck required desktop availability before placement where necessary to handle external desktop changes conservatively.<br>
8. Inspect and use supported KWin desktop-management APIs on both X11 and Wayland. Do not modify `kwinrc` directly, assume X11-only desktop-management interfaces are valid on Wayland, or introduce new broker/resident methods unless inspection demonstrates they are necessary and the maintainer approves the interface extension.<br>
9. Fail gracefully with informative "-${err}" message if the required number of desktops exceeds system capacity.

**Acceptance:** On both supported backends, verify that sufficient existing desktops cause no modification; insufficient desktops are added and positively verified; cancellation causes no changes; and desktop provisioning failures prevent all application launches. Include headless tests for sparse desktop references, configured limits, partial provisioning failures, and launch-order preservation.

### 1.5c.4a — Dolphin local, then SFTP

**First approved graphical fixture:** Dolphin, using `--new-window` and an explicitly constructed argv array (no shell-evaluated command strings, implicit `eval`, or unsafe target interpolation). Verify installed `dolphin` and current behavior on both hosts before accepting native results.

Proposed executable configuration forms:

```bash
# Illustrative entries; desktop numbers are independent examples.
desktop_session_list=(
    "2|dolphin|local|"              # open $HOME
    "3|dolphin|local|/some/path"    # open an approved local path
    "4|dolphin|sftp|nuthuvia"       # remote host; optional path syntax TBD
)
```

- `dolphin|local|` means a new local Dolphin window at `$HOME`; `dolphin|local|PATH` means a new window at a validated local location. Define handling of relative paths, whitespace, missing paths, and trailing separators before implementing the parser; do not invoke a shell to interpret `PATH`.
- `dolphin|sftp|TARGET` means a new **local** Dolphin window opening a KIO SFTP URL. Define and test an unambiguous `TARGET` grammar (host, optional user, optional absolute path), URL encoding, IPv6 handling, and rejection of malformed/ambiguous endpoints. `hostname[:path]` is a requested convenience, **not yet a complete specification**; a colon is also used by IPv6 and port syntax. Do not insert passwords in configuration, command lines, logs, or URLs.
- KIO SFTP authentication and file-navigation outcomes are independent of registered-window identity and KWin placement; a failed or unreachable remote path must not be mislabeled as a placement failure. Do not promise that Dolphin presents a lasting placeholder in every connection-failure scenario without native evidence.
- Add narrowly scoped planner validation and executable dispatch only after the grammar is approved; mixed plans must continue to fail wholly *before launch* if any entry is unsupported. Preserve existing Konsole/SSH behavior.
- Confirm independently launched Dolphin windows register exactly once by unique KWin UUID, with correct intended desktop and verified geometry; existing Dolphin instances must not be silently adopted. If `--new-window` sometimes delegates, fail conservatively and report the evidence before changing the broker.

### 1.5c.4b — TigerVNC viewer over SSH

**Second selected implementation candidate:** `vncviewer|ssh|TARGET`, with the viewer running locally and its VNC connection protected by an authenticated SSH tunnel. No direct, unauthenticated, or exposed raw VNC connection is authorized.

Before coding, inspect the maintainer's `archive/tigervnc-poc/vnc-via-ssh-launch`, installed TigerVNC viewer version/options, and representative server configuration. Specify and obtain approval for:

- `TARGET` grammar, authenticated SSH endpoint, VNC display/port selection, and whether required fields belong in a separate trusted profile instead of overloaded `host[:path]` syntax;
- SSH tunnel creation and ownership (including evaluation of TigerVNC's documented `-via` support versus a managed explicit `ssh -L`), strictly loopback-bound VNC forwarding, existing host-key policy, authentication prompting, timeouts, and deterministic tunnel cleanup;
- handling the viewer's initial authentication dialog and subsequent viewer window: identify the *actual KWin-managed window*, not a guessed popup, class match, or process PID;
- viewer exit, connection failure and retry behavior: distinguish window registration/placement, viewer lifecycle, SSH-tunnel outcome, VNC authentication, and remote session availability; preserve a window only when the actual client supports it;
- clear, actionable failure messages, including an approved, relevant reference to trustworthy TigerVNC/SSH configuration documentation **without exposing credentials or dynamically trusting unverified URLs**.

The historical label `via-ssh` remains descriptive until its meaning is approved. It must not be silently equated with SSH X11 forwarding, a VNC gateway, or direct VNC. Do not replace `ssh_wrapper` with `swr`, or alter existing Konsole transport behavior. Native remote-session tests remain maintainer-run.

### 1.5c.4c — Graphical underlay, stacking, and focus

Use the established terminal and `graphical_*_percent` geometry as the initial layout policy. Introduce a clearly named configurable **`underlay_protrusion_percent`**, starting at **2**, validated as a bounded percentage and included in the normal `varlist`/effective-config display. Its exact geometry/visibility semantics must be defined before code changes: specify the measured reference dimension, how the exposed clickable region is calculated, and behavior at screen edges, rather than assuming 2% always produces a usable hit target.

- Preserve **configuration-file launch order exactly**. Do not silently sort graphical windows before or after terminals. If reliable focus/underlay becomes unduly complex with arbitrary order, stop, report the tradeoff, and request a maintainer decision.
- Inspect available KWin X11/Wayland resident capabilities for a **positively identified window** to lower/raise or adjust focus without changing unrelated windows. Provisional rectangle overlap is not proof of Z-order or clickable visibility. Do not invent a D-Bus method or use X11-only focus tools for Wayland.
- Validate combinations of graphical windows with one through four Konsoles, including launch-order permutations, focus after the last entry, user click-to-raise, and visibility of a deliberately exposed edge. Do not continuously re-enforce stacking after manual movement/resize/raise unless separately authorized.
- If broker or resident API changes are genuinely necessary, stop for specific interface, compatibility, and security authorization; no general window-management privilege expansion is implied.

## 4. Maintainer network/security policy

- **Direct VNC is prohibited**, even on a local subnet; the selected VNC implementation must use authenticated SSH tunneling. Do not disable host-key verification, weaken authentication, expose VNC listeners on non-loopback interfaces, store credentials in scripts, or put secrets in error messages.
- For **newly introduced remote connections** where client and server are in different subnets, the maintainer requires a **verified VPN pathway** in addition to any program-specific SSH/TLS protections. Preserve existing accepted Konsole/SSH behavior; do not extend new cross-subnet modes unless the requirement is enforceable and approved. Apply the same conservative review to new Dolphin SFTP and future file-browser/RDP candidates.
- `ip addr`, `getent`, and routing observations can inform endpoint/network assessment, but **subnet difference alone is not proof of WAN exposure**, and those commands alone are not proof of a protected VPN route. Define an approved trust/network policy and a reliable fail-closed verification method before implementing an automatic gate; report unsupported cases instead of assuming safety.
- Treat TLS as a security property, **not a complete RDP/VNC execution mode**. For every future `|tls|` candidate identify the underlying protocol, endpoint grammar, actual client capabilities and certificate-verification behavior before authorizing execution.

## 5. Candidate program/mode/target inventory and feasibility reports

The following is the maintainer's **approved inventory for investigation and interface planning**, **not** a statement that each form is currently executable or that every listed program will be implemented in 1.5c.4. Newly authorized executors must be individually named in `HANDOFF.md` after their grammar, dependencies, identity behavior, and security have been reviewed.

| Candidate recipe | Scope/disposition |
| --- | --- |
| `konsole|ssh|TARGET` | Existing supported SSH target recipe; regression-protected |
| `konsole|local|COMMAND` | Existing supported local executable recipe; **blank target not currently supported** |
| `qterminal|ssh|TARGET`, `qterminal|local|` | Investigate terminal-specific startup, SSH and PID/UUID behavior; not automatically Konsole-compatible |
| `vncviewer|ssh|TARGET` | **Selected second implementation candidate**, after endpoint/tunnel approval |
| `mc|sftp|TARGET`, `mc|local|` | Investigate TUI launch inside a managed terminal and actual remote-file protocol; `mc` itself does not create a KWin graphical window |
| `dolphin|sftp|TARGET`, `dolphin|local|[PATH]` | **Selected first implementation**, local followed by SFTP |
| `krusader|sftp|TARGET`, `krusader|local|` | Investigate KIO/remote path behavior and unique graphical window launch |
| `filezilla|sftp|TARGET`, `filezilla|local|` | Investigate application-specific URL/connection-site grammar and window delegation |
| `nautilus|sftp|TARGET`, `nautilus|local|` | Investigate GNOME/GVfs dependencies, URI launch and process delegation |
| `nemo|sftp|TARGET`, `nemo|local|` | Investigate URI launch, dependencies and process delegation |
| `krdc|tls|TARGET`, `remmina|tls|TARGET`, `xfreerdp|tls|TARGET`, `wlfreerdp|tls|TARGET` | **RDP feasibility investigation only**; client availability, RDP-specific grammar, certificates and X11/Wayland compatibility unverified |

For each investigation, report executable/package presence separately for `gmki91` and `q552u01`; actual launch syntax and protocols; whether the process reliably produces a uniquely correlated KWin window; local vs remote endpoint security; user-facing benefit; and a recommendation to implement, defer or reject. Do not infer installation from a package's general availability.

RDP feasibility belongs to 1.5c.4. Its **implementation** needs a subsequent express maintainer decision. If implemented and accepted before 1.5d, include it in the 1.5d integrated regression; otherwise document it as deferred rather than silently turning 1.5d into an RDP implementation milestone.

## 6. Acceptance and regression matrix

**Headless checks** (per separately authorized implementation increment):

- `-c` describes all grammar-accepted recipes without launching; `-o` rejects unsupported or malformed complete plans *before* confirmation and before application, tunnel or network side effects. Existing Konsole cases remain executable and unchanged.
- Argument/URL validation is deterministic, with no command interpolation; credentials, unsafe endpoints and invalid target syntax are rejected or handled without leakage. Missing local executables are reported clearly.
- Each supported graphical launch follows the existing lock, safe broker transaction, logical desktop/slot, positive UUID registration, exact placement, and partial-failure/uncertainty policies; no class-only adoption and no rollback of already created windows.
- Mixed plans use all-entry logical slots, terminal-only geometry counts, and actual configured launch order. Underlay width and protrusion percent are validated and shown in effective configuration.
- SSH tunnels, connection failure, cancellation, viewer exit and timeouts are mocked independently of registration/placement; no hanging or orphaned tunnel and no inherited launcher lock. No real GUI/network actions in agent-run tests.
- Run permitted Python/Node regression suites, installed-header coverage where available, Bash syntax, ShellCheck, and diff/whitespace checks.

**Maintainer-native checks on each backend:**

- Dolphin local `$HOME`, explicit path, and SFTP reachable/unreachable target; unique UUID and positive placement in each supported scenario; preexisting application window not falsely adopted.
- Selected VNC-over-SSH path only after server setup and security policy are approved: authentication-dialog lifecycle, target viewer registration/placement, reachable/unreachable server, tunnel teardown, and no cleartext/exposed listener.
- One-, two-, three-, and four-Konsole mixed layouts and selected launch-order permutations: correctly protruding/usable graphical window, verified KWin stacking/focus, preserved manual moves, and no changes to unrelated windows.
- Duplicate launch after manual window movement, competing `-o`, bounded Busy behavior, known isolated versus uncertain failures, exact desktop membership, and live-child lock release; reuse prior validated evidence where applicable.

Maintain a clear PASS/FAIL/NOT TESTED matrix by backend, with the implementation SHA and host/environment recorded. Do not claim SFTP/VNC transport success merely from KWin placement success.

## 7. Excluded and later work

Do not implement `-a`, `-d`, `-x` (Step 1.6); checkpoint/same-session recovery and durable restore (1.7/1.8); packaging/eselect integration (1.9); generic one-off launch; automatic restoration after manual movement; managed-slot release after closure; broker SSH-transport telemetry; speculative Wayland geometry tolerances; non-KWin desktop generalization; or Phase 2 performance optimization. Do not modify protected `joetoo` or `joetoo-upstream` repositories; consult their code/policies read-only where necessary.

**Step 1.5d remains a separate integrated X11/Wayland regression gate.** It covers accepted 1.5 workflows plus deferred focus races, specific-multiple-desktop membership, tiled/fullscreen refusal, Busy classification, complete/incomplete layouts, and new graphical focus/stacking. It does not automatically authorize additional program/transport implementations.

## 8. Authorization, evidence, and next actor

This is a **scope outline**, not operative implementation authorization. `HANDOFF.md` must separately designate the accepted increment(s), base SHA/new isolated branch, precise editable paths, headless validations, native/remote operations, stop/escalation conditions, and distinct commit/push/PR/merge permissions. In particular, broker/resident interface edits and any VPN enforcement need explicit narrow approval.

**Next actor:** local aagent, upon maintainer approval documented in task HANDOFF.md, begins bounded implementation
