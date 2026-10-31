# Deferred Step 1.5c.4 investigation (no executor changes)

## Evidence and availability

Inspected installed KWin headers/XML, existing planner/resident, historical
Step 1.3b report, archive/tigervnc-poc/vnc-via-ssh-launch, installed viewer manual,
and primary KDE/TigerVNC source below. No remote connectivity or viewer run.
The agent environment has executable paths for dolphin, qterminal, vncviewer,
krdc, xfreerdp and nautilus. command -v found none for mc, krusader, filezilla,
nemo, remmina or wlfreerdp. These are environment-local observations, not verified
package/version inventories on gmki91 or q552u01. Each host's current package,
executable options and identity behavior still needs maintainer verification.

Historical [Step 1.3b report](../archive/step1.3/step1.3b/joetoo-kwin-step1.3b-draft-pr.md)
records Dolphin --new-window exact-PID matches on both hosts. It is historical
feasibility evidence, not acceptance of the new executor/current versions.

## Dolphin SFTP

KDE [Dolphin source](https://github.com/KDE/dolphin/blob/master/src/main.cpp)
skips existing-instance attachment with --new-window and consumes QUrl targets.
[KIO SFTP worker](https://github.com/KDE/kio-extras/blob/master/sftp/kio_sftp.cpp)
uses SSH authentication and maps missing/denied paths to KIO errors. Authentication,
wallet/host-key dialogs and remote errors need native lifecycle observation;
registered Dolphin is not proof of successful authentication or navigation.

Propose approving canonical sftp://[user@]host[:port]/absolute/path first,
with bracketed IPv6, validated port 1..65535, UTF-8 path percent encoding, and
no passwords/query/fragment. Omitted path semantics (remote home vs root) must be
explicitly approved; do not silently map one to the other. Reject malformed brackets,
controls, userinfo passwords and ambiguous unbracketed IPv6/colon shorthand.
Use a URL builder with structured components, not text interpolation. Decide
whether already-percent-encoded input is accepted before defining normalization.
The requested host[:path] convenience needs a separate grammar: reject ambiguity
rather than guess between port, IPv6 and path. No SFTP parsing or execution added.

## TigerVNC over SSH

The archived launcher uses -via user@gateway with localhost:2. It is a historical
fixture, not a complete endpoint/cleanup/identity contract. The installed manual
and [upstream manual](https://tigervnc.org/doc/vncviewer.html) describe -via as SSH
local forwarding; a viewer profile can override command-line parameters. Do not
accept arbitrary profiles capable of bypassing approved tunneling policy.

Recommend a named trusted profile with separate SSH endpoint/user/port, remote
loopback VNC port and viewer options, rather than overloading hostname:path.
Evaluate -via against an owned foreground ssh -N -L tunnel with explicit local
127.0.0.1 binding, ExitOnForwardFailure, ordinary host-key verification and exact
child-PID cleanup. Do not use broad process kills, expose listeners or add VPN gates.
The manual's default -via forks SSH and uses a bounded remote sleep; reliable
long-session ownership/cleanup needs evaluation before selecting that mechanism.

Native observation must distinguish password/authentication dialogs from the actual
viewer window. A single PID producing multiple KWin windows may be ambiguous under
the existing contract; do not register a guessed class/title or weaken correlation.
If this occurs, propose a bounded broker/resident identity refinement with evidence.
Transport, SSH authentication, VNC authentication, viewer exit and placement need
independent mocked/native failure scenarios. No tunnel/viewer dispatch implemented.

## Underlay and exposed area

Proposed interpretation for separate approval: underlay_protrusion_percent=2 is a
minimum horizontal exposed strip measured against configured screen_width, rounded
up to pixels. Require graphical right edge >= terminal region right edge + strip,
within the configured screen. At 1920, strip is 39 pixels with ceiling rounding;
existing defaults place terminal right edge near 88% and graphical right edge near
99%, already exceeding that minimum. Decide whether minimum vs exact protrusion
is desired, and whether insufficient screen area rejects or adjusts geometry.
No new variable/formula was implemented in this first increment.

Rectangle exposure alone does not establish clickable Z-order or usable hit area.
Installed Window exposes keepBelow/keepAbove; internal C++ Workspace has lower/raise
and activation methods, but internal availability is not proof of JavaScript API
exposure. The current resident does not implement underlay policy. Permanent
keepBelow may conflict with click-to-raise, so do not equate it with one-time lowering.
Before coding, inspect supported scripting bindings and natively test lowering/focus
on both backends. A future broker/resident intent should be tied to an already
verified request UUID, apply once, preserve manual overrides and respect security
boundaries. It requires separate authorization. Preserve file launch order; report
unsupported focus/order combinations rather than reorder applications.

## Other recipes

| Candidate | Feasibility and recommendation |
| --- | --- |
| Konsole SSH/local | Accepted, regression-protected; blank local target still unsupported |
| QTerminal | Potential terminal startup adapter; inspect its actual argv, process delegation and rcfile behavior; defer |
| mc | TUI, needs a positively managed terminal; determine actual remote filesystem protocol; defer |
| Krusader | KIO candidate, but new-window/PID behavior unverified; defer |
| FileZilla | SFTP/site grammar and process/window delegation unverified; defer |
| Nautilus/Nemo | URI/desktop integration and single-instance delegation require exact-PID evidence; defer |
| KRDC/Remmina/FreeRDP variants | RDP endpoint grammar, certificate policy and backend/window identity need native evidence; TLS is not a standalone dispatch mode; defer |

No current source supports promising exact identity for these new recipes.
No broker/resident/architecture update is required for the implemented local-Dolphin
increment; the underlay or viewer identity proposals above need a later decision.
