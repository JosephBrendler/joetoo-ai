# Step 1.5c.5 — Remote resources and graphical remote desktops: implementation scope and outline

**Milestone status:** Steps 1.5c.5a (Dolphin SFTP) and 1.5c.5b
(TigerVNC-over-SSH) are accepted. Step 1.5c.5c (RDP feasibility) is closed
with an affirmative maintainer decision, recorded in PR #28. Step 1.5c.5d
(managed RDP) is in incremental development, beginning with SDL3 FreeRDP
native-Wayland **registration without placement**. Later increments require
separate approval. This scope specifies requirements and acceptance gates;
it does not grant source-edit, public-interface, native-test or publication
authority. Refer to the [active HANDOFF dispatcher](HANDOFF.md) and explicit
maintainer tasking for current actor, branch, permissions and next decision.

**Historical baseline:** Feasibility PR #28 merged at `be8eb276`. The
maintainer-selected task branch is
`task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. Verify its actual
HEAD and branch base in the current checkout; historical or originally proposed
branch names are not operative instructions.

**Authorities:** Current project `ARCHITECTURE.md` (especially §§3–7, 10–11), project/root/workspace `AGENTS.md`, and the active [HANDOFF](HANDOFF.md). `Step1.5c4_implementation_scope.md` is historical design evidence, not renewed authorization.

## 1. Objective and boundaries

Extend the accepted configured `joetoo-kwin -o` launch workflow to **remote file browsing** and **graphical remote desktops**, while reusing its existing KWin X11/Wayland positive managed-window identity, original intended desktop/slot, shared geometry, application-independent `under`/`panel`/`over` layers, initial stacking/focus, and conservative concurrency/partial-failure semantics.

The established milestone sequence is:

1. **1.5c.5a — Dolphin SFTP:** Accepted and closed.
2. **1.5c.5b — TigerVNC over SSH:** Accepted and retained as a managed peer option.
3. **1.5c.5c — RDP feasibility and decision:** Closed; affirmative feasibility accepted.
4. **1.5c.5d — Managed RDP implementation:** Planned as separately authorized
   increments, beginning with SDL3 FreeRDP registration-only on native Wayland.

**Peer-capability decision:** The established TigerVNC-over-SSH implementation,
SDL FreeRDP and any later approved RDP clients are independent user-selectable
options. Implementation sequence does not assign a primary/secondary, default
or fallback role. Other clients need their own launch/security/identity
contracts without inheriting SDL-specific window behavior; no speculative
generic plugin framework or automatic client fallback is approved.

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

### 3.2a Post-confirmation name-resolution and TCP-connectivity advisories

A maintainer-directed follow-up correction adds **two separately reported checks**
for SFTP targets: local DNS/NSS name resolution (not needed for a literal IP)
and bounded TCP connectivity to the intended SSH endpoint/port, where the
effective destination is safely ascertainable. Each check has its own
`success`, `failure`, or `not attempted/inconclusive` result. If resolution
fails and there is no usable address for a TCP attempt, report the second
check as **not attempted**, not as a TCP failure. A failed direct lookup or
connection check is not proof that KIO/libssh cannot reach an SSH alias or
proxy-mediated destination. Neither check is authentication or SFTP success.

These checks occur **only after the maintainer confirms `-o`**, immediately
before the relevant SFTP launch. Preserve the offline `-c`, full-plan URI
validation and local KIO capability preflight. Use configurable bounded
timeouts and a documented disable mechanism; do not require new packages or
embed secrets or unvalidated URIs into resolver/connection command lines.
Unavailable tools, unsupported aliases/proxies, timeouts and indeterminate
results must be differentiated from a verified failure. The checks are
**advisory only**: negative results must not abort an otherwise valid plan,
change UUID/slot/geometry handling, or claim a remote-authentication outcome.
Always launch Dolphin with the original validated URL so KIO can show its own
error and allow manual retry; do not silently substitute a local directory.

### 3.2b KIO/OpenRC process-launch warning

The maintainer observed
`kf.kio.gui: Failed to determine systemd version, falling back to extremely legacy forking mode.`
on an OpenRC/KWin native test host. KDE KIO's process runner attempts to query
the session's systemd-manager version and uses a conventional forking fallback
when that query does not return a usable version. This is a **nonfatal,
application-launch compatibility warning**, separate from SFTP hostname,
TCP-connectivity, authentication or listing errors. The tested managed launch
and remote browsing still succeeded. Do not introduce systemd as a dependency,
suppress the warning or redesign KDE/joetoo process launching in this tranche.

### 3.3 Acceptance

Headless: valid/invalid endpoint table; URI construction and escaping; no command evaluation/secret leakage; complete-plan preflight; cancellation; launch-argv capture; ambiguous/delegated window rejection; propagation of independent placement versus remote-access results; preservation of existing local-Dolphin and Konsole tests.

Maintainer-native on `gmki91` X11 and `q552u01` Wayland: reachable SFTP location with visible file browsing, unavailable/invalid target, authentication behavior, positive new-window UUID, exact desktop/slot and placement, layer behavior, and no adoption of an already-running Dolphin. Report which outcomes are directly observable versus not instrumented.

**Observed evidence (2026-11-01):** The maintainer ran the SFTP+local Dolphin
fixture on both X11 (`gmki91`) and Wayland (`q552u01`): 301 Python and 50
JavaScript tests passed on each host; both new windows registered with distinct
UUIDs, reached desktop 2 with verified geometry and verified panel-over-under
stacking; the maintainer independently browsed `nuthuvia.brendler` via KIO
and opened its `/etc/hostname`. Both runs initialized desktop 2 while desktop
1 was active, so automatic focus acquisition on the displayed target desktop
was **not tested**. Host-key/authentication prompts and all URI variants were
not exercised. A separate X11 negative test using nonexistent
`raspi23204.brendler` successfully placed both windows, while Dolphin reported
name-resolution failure. That verifies independent placement/error display;
it does **not** establish completed acceptance of the new DNS/TCP advisories,
which require their own tests after implementation. Preserve these distinctions
in the task's native acceptance record.

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

**Completed gate:** The maintainer accepted an affirmative RDP feasibility
determination. SDL3 FreeRDP was chosen as the **first client to implement**,
not the preferred or default client. TigerVNC-over-SSH remains a fully
supported peer. The comparison criteria below document the original
investigation scope, not a new instruction to repeat completed tests.

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

The accepted comparison and native observations are recorded in
[remote-desktop research](README_remote_desktop_research.md), including original
installed-client evidence, native diagnostics and clearly labeled inference. Neither choosing SDL first nor
establishing feasible window identity grants production RDP acceptance.

### 5.2 Evidence and decision gate

**Closure evidence:** Native-Wayland observations cover correct credentials
window exclusion, positive marked-viewer UUID, NLA cancellation/failure,
connection refusal and an unrelated viewer remaining present. X11 results
include successive marker-bearing temporary and persistent windows and require
an additional viewer-role discriminator. The proof scripts do **not** exercise
production registration or placement, server-side session continuity, or
validated production certificate trust. In-process reconnect was not tested;
initial implementation must reject silent UUID replacement. The maintainer's
existing Python/JavaScript test passes remain historical evidence, not tests
of the production RDP selector.

## 5A. Increment 1.5c.5d — Managed RDP implementation

**Objective and boundary.** Add SDL3 FreeRDP as an independently selectable
peer of accepted managed TigerVNC-over-SSH, reusing existing launcher, broker,
registry, KWin resident, desktop/slot, geometry and layering invariants.
Potential future clients, including KRDC and Remmina, require independently
approved launch, identity, security and lifecycle contracts. Implementation
chronology confers no default, preference or fallback. Do not introduce a
general-purpose client-plugin framework.

The recipe grammar remains `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]`; this
increment does **not** approve concrete SDL recipe values. Process launch,
viewer registration, placement, authentication, transport security and remote
desktop readiness are separate outcomes.

### Increment 0 — Preconditions and design gates

Inspect the real installed SDL executable and existing broker/registry/public
interfaces. Establish a single ordinary desktop-window profile, safe argv,
no secrets in config/argv/logs, bounded transaction/resource policy and
strict registration-versus-placement separation. Production endpoint parsing,
TLS certificate/server identity, NLA and allowable security negotiation remain
separate maintainer-controlled policy gates. Feasibility-only certificate
exceptions are not accepted production defaults.

Existing generic and TigerVNC completion paths may couple registration to
placement; do not reuse that behavior for registration-only SDL. An additive
D-Bus development interface requires a reviewed contract, especially caller
identity, transaction ownership, child provenance and evidence-FD validation.
The separate `step1.5c5d-sdl-interface-contract.md`, when present in the
authorized working tree, is detailed design evidence rather than permission
by itself.

### Increment 1 — Native-Wayland SDL registration only

**Viewer identity.** Arm a broker-owned transaction before child launch;
capture synchronized observation source/revision, event floor and existing
window baseline; generate an exact unique title marker. Bind the actual SDL
child PID and expected application identity. Require a new, live, normal KWin
window UUID with complete qualifying `added` lifecycle and matching source,
PID, application and exact marker. A late marker may qualify **only the same
positively observed UUID**, with complete lifecycle history.

Exclude unmarked credentials dialogs, auxiliary windows, previously present
unrelated viewers and replacement UUIDs. Fail closed on missing/mutated/lost
marker, simultaneous or disappeared competing candidates, incomplete/evicted
event history, observation-source replacement, PID/class mismatch, process
exit, window disappearance, cancellation, timeout and duplicate ownership.
No PID-only, class-only, title-only, most-recent-window or fixed-delay selector;
no new user-interaction observer or observation daemon.

**Registration only.** Register the exact verified UUID and return stable
bounded terminal results. Do **not** request placement, desktop movement,
geometry, focus or stacking, or silently retarget a replacement window.
Existing generic/VNC interfaces and semantics remain unchanged.

**Additive development interface under separately controlled approval.**
Codex proposed four D-Bus methods:

| Method | Input → output | Registration-only role |
| --- | --- | --- |
| `BeginSdlRegistration` | `s → s` | Establish owner-bound transaction before launch |
| `BindSdlRegistration` | `sih → s` | Bind launched child and bounded evidence descriptor |
| `PollSdlRegistration` | `s → s` | Owner-only pending/terminal result |
| `CancelSdlRegistration` | `s → s` | Owner-only cancellation and cleanup |

The maintainer has separately issued bounded conditional development tasking
for this interface; **the exact public contract and native/production security
acceptance are not implied by this scope**. Review the actual current
interface-contract draft and explicit maintainer direction before exposing
methods. Authenticate the unique D-Bus sender for every call and bind its
single persistent bus connection to the transaction. Reject cross-caller
poll/bind/cancel, process reuse and substituted or contradictory evidence.
Clean up on name-owner loss, cancellation, timeout and terminal result.

Require reliable child PID provenance, immutable or otherwise defensible
process-lifetime identity, parent relationship, and FD identity, ownership,
type and bounds. A bare numeric PID or an attacker-substitutable writable
log is not independent proof. D-Bus `ProcessFD` is **optional**; verify its
availability on the actual target bus. If absent, do not silently weaken
caller/process verification: propose a source-grounded alternative for approval
or stop at that boundary. An owning same-user development launcher and its
writable log are within an explicitly trusted launcher model; do not claim
cryptographic SDL-log authorship or malicious-same-UID isolation.

**Expected narrow source/test envelope:**

| Path or component | Bounded purpose |
| --- | --- |
| `libexec/joetoo-kwind` | SDL-specific transaction, observation and D-Bus handling, without changing generic/VNC behavior |
| Proposed `libexec/joetoo_kwin_rdp_launch.py` | Minimal local SDL launch adapter, only if source inspection justifies it |
| `tests/test_rdp_broker.py`, `tests/test_rdp_launch.py` and relevant fixtures | Positive/negative headless checks and no-placement regression |
| `libexec/joetoo_kwin_registry.py`, `joetoo-kwin-resident.js` | Read-only by default; any required edit separately approved |
| Existing configuration template | Approved configurable bounds only; do not introduce premature `-o` recipes or change VNC defaults |

**Headless acceptance:** Positive exact UUID registration and late-marker
qualification on the same UUID; no placement in any path; credentials-only
cancellation, failed NLA, refused connection, lost/mismatched marker,
simultaneous or disappeared competitors, preexisting unrelated viewer,
wrong PID/class/source, incomplete event history, PID reuse, forged or
substituted evidence FD, unauthorized D-Bus sender, name-owner loss,
cross-transaction interference, process exit, bounded expiry, duplicate
ownership, stable terminal results and inert late callbacks. Exercise actual
broker/registry behavior through mocks, preserve generic/TigerVNC regressions,
and do not mistake mocked transport results for remote authentication.

**Maintainer-native gate (separately authorized):** On `q552u01`,
verify actual SDL backend `wayland`, exact child PID/UUID, correct viewer
registration without any placement/movement, credentials exclusion, and
bounded failure/coexistence checks. Record actual security/certificate
conditions. Feasibility archives do not establish production acceptance.
Codex must not run native/network sessions without that authority.

### Increment 2 — SDL X11 viewer-role identity (stock-client legacy profile)

**Maintainer direction, 2026-11-08:** Candidate A2 client-side XID/nonce/READY
instrumentation is **ABORTED** as an implementation path because it requires a
downstream FreeRDP patch for the retiring native Plasma X11 session. Its accepted
Stage 0 synthetic tests remain historical research evidence, not Increment 2
acceptance. Preserve the accepted native-Wayland Increment 1 unchanged.

Evaluate **A1** first as a short experiment in *documented, supported settings
of unmodified stock FreeRDP/SDL* that might suppress transient native-window
replacement. Do not infer a proven role from a renderer option or absence of a
replacement in a small sample. If A1 is unsupported or inconclusive, consider
**Candidate C**: an explicitly opted-in, best-effort X11-only persistence selector,
subject to the [A1/C draft](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md).
No FreeRDP/SDL patch is allowed by this revised scope.

**Explicit, narrow exception to the Increment 1 fixed-delay prohibition:** For
this **legacy native-KWin-X11 SDL profile only**, the maintainer permits a
**bounded, centrally configurable, monotonic persistence interval** as *one
component* of a pragmatic viewer-role heuristic. The proposed parameter is
`rdp_x11_identity_settle_ms` (initial **500 ms for evaluation**, adjustable from
the established configuration template after validation). Start the one timer
when a particular newly observed UUID **first fully qualifies** by launched
PID, application, exact marker, normal-window and source/lifecycle checks; a
late marker cannot backdate qualification. Evaluate concurrently with normal
broker observation and provenance checks; **never** chain it to a second 500 ms
`PollCorrelation()` diagnostic wait. Do not use a blocking sleep or extend the
registration deadline. The existing diagnostic `PollCorrelation()` wait is **not**
a registration prerequisite and need not be modified by this exception.

At the eligibility decision, require the **same unique live UUID** and fresh
child/PID/class/marker/source/owner checks with complete, non-evicted birth and
removal history. On X11 only, retain an observed temporary marked predecessor as
a removed tombstone, instead of rejecting *solely* because it disappeared; do
not discard ambiguity, changed identity, source gaps or an unresolved live
competitor. No adoption of preexisting windows, silent UUID replacement,
placement, focus or stack changes; existing caller/FD and resource safeguards
remain in force. **Persistence is not positive proof of FreeRDP renderer
completion.** A temporary viewer lasting longer than the threshold may still
be misregistered. Evaluate real archived lifetimes, A1 effects and this residual
risk before authorizing an X11 broker implementation or native acceptance.

This permission is **Increment 2 only**: it does **not** weaken the accepted
native-Wayland Increment 1 or generic/VNC contracts. The next A1/C read-only
feasibility gate does not authorize source edits, builds, native sessions or
publication. A later broker implementation and `gmki91` native test each require
a separate, narrowly scoped maintainer approval. Increment 2 remains OPEN.

### Increment 3 — Controlled placement release

Registration does not establish successful GDM login, authenticated GNOME
desktop readiness or allowed placement. Propose explicit operator-confirmed
release first; automatic release requires separately reliable readiness
evidence. Revalidate exact registered UUID, owner/source and transaction
before existing desktop/geometry/layer/focus operations. Address Busy, slot
reservation, cancellation, expiry and initial layout completeness without
holding the ordinary launcher lock throughout interactive authentication.

### Increment 4 — Configured SDL RDP workflow

With separate authorization, implement exact safe SDL recipe grammar and
offline whole-plan `-c` validation plus confirmed `-o` execution. Reject
unsupported/invalid plans before side effects. Preserve security policy,
independent registration/placement/remote outcome reporting, slot ownership,
layer/focus guarantees and Konsole/Dolphin/TigerVNC behavior. No automatic
reconnect, UUID reassignment, multimonitor, RemoteApp or client fallback is
implied.

### Increment 5 — Security, regression and milestone closure

Validate production server certificate/endpoint identity and permitted TLS/NLA
negotiation; complete relevant full headless and maintainer-native regressions;
record tested and unsupported cases. Close the milestone only following
maintainer review and integration. **Step 1.5d** remains a separate broader
integrated regression and `-L`/`-l` milestone.

**Increment 1 exclusions:** X11 enrollment, any placement, configured `-o`,
other clients, speculative plugin infrastructure, changed VNC/generic
semantics, unapproved certificate exceptions, new interaction observers,
installer/deployment, protected-repository edits or publication without
separate authority. Stop on unreliable identity or any missing required
interface/security/file permission.

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
| RDP feasibility (closed) | comparative documentation, mock identity and security observations | maintainer-run X11/native-Wayland diagnostic captures; no production registration |
| Managed RDP (1.5c.5d; individually gated) | Private selector and owner/process/FD-interface tests, fail-closed identity and no placement; then X11 role, placement, configured and security tests by approved increment | `q552u01` native-Wayland and `gmki91` X11 registration/placement at separate gates; server identity/security before final acceptance |
| Compatibility | existing Python/JS cases, Bash syntax, ShellCheck, link/diff checks | no regression to Konsole SSH placeholders and original local Bash continuity |

Reuse previously accepted 1.5c.4 native evidence for unchanged contracts rather than rerunning the full graphical-layer battery in every subincrement. New network/GUI work needs actual maintainer-native acceptance on both backends. Record PASS/FAIL/NOT TESTED **by host/backend and exact implementation SHA**; separate application/placement success from remote transport/authentication success. Document missing native evidence honestly.

## 8. Authorization, stop conditions and subsequent milestone

**Source of authority.** This scope documents accepted requirements and
proposed future gates; it **does not grant execution permission**. The
maintainer-selected task branch is
`task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`.
Verify the actual current revision, actor, permissible paths, active
authorization and next decision against the [current HANDOFF](HANDOFF.md),
explicit maintainer tasking and the local checkout. Historical instructions
and an agent-authored contract are not independent authority.

**Increment 1 progress and reserved gate.** Codex reported a private
registration-only core and headless tests, not independently reviewed/native
accepted or necessarily committed/published. The proposed four-operation
additive interface is subject to explicit maintainer review. Subsequent
conditional development authorization may permit implementation and headless
tests without constituting final public API, ProcessFD security, transport
policy or native acceptance. Consult the current maintainer prompt and
HANDOFF for the exact boundary; retain detailed interface/evidence records
outside HANDOFF.

**Stop/escalate** on missing or contradictory current authorization,
uncertain branch/baseline, unexpected dirty worktree, unsafe process/FD
provenance, missing or ambiguous complete KWin lifecycle, unavailable bus
credentials without an approved alternative, unauthorized interface or
security changes, generic/VNC regressions, expanded edit paths, native host
operations/deployment or protected-repository writes. Do not weaken identity,
authentication or trust merely to obtain a passing result.

**Next actor and review.** The maintainer reviews the concrete interface
implementation and headless evidence, grants or revises any remaining narrow
security/interface authority, and separately decides native acceptance,
publication and subsequent increments. Detailed progress belongs in task
status/evidence records; HANDOFF remains the concise current dispatcher.
