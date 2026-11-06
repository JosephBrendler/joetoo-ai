# Remote desktop research — Step 1.5c.5c feasibility and subsequent evidence

**Status:** The maintainer accepted *affirmative feasibility* for adding managed
RDP to joetoo-kwin. This document preserves findings and open implementation
questions; it does not grant permission to run clients, alter transport policy,
register windows, or change production interfaces.

## Scope and source documents

This general research index consolidates the RDP client/server comparison,
GNOME session model, SDL window-identity work and security constraints.
The [existing GNOME Remote Desktop study](README_gnome_remote_desktop.md)
remains authoritative for its detailed Ubuntu/GRD configuration, credentials,
client trials, Remote Login/Desktop Sharing distinction, and certificate
observations. Its detailed content has **not been removed or overwritten** in
this review draft.

The [original long-form HANDOFF at migration baseline](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md)
retains exact diagnostic scripts, observations, event IDs, private archive
identifiers, uncertainties and agent interpretation. This document extracts
accepted technical conclusions without treating historical recommendations as
live instructions.

## 1. Server/session models evaluated

| Server | Session contract and relevant distinction |
| --- | --- |
| GNOME Remote Login | System-level GNOME Remote Desktop via GDM; login can start a remote desktop without an already unlocked physical GNOME session. GRD authentication and subsequent GNOME login are separate stages. |
| GNOME Desktop Sharing | User-level GRD sharing of an already-running, unlocked graphical session; its credentials and daemon scope differ from Remote Login. |
| xrdp + xorgxrdp | Alternative remote graphical login/session using an Xorg-compatible desktop; not proof of working native Wayland GNOME remote login. |
| KDE KRDP | Server for sharing an existing Plasma desktop; distinct from **KRDC**, the client. No presumption that it supplies unattended new-login semantics. |

On `raspiubuntu401` (Ubuntu 26.04.1 on Raspberry Pi 4), maintainer-operated
tests established independent GRD Remote Login (TCP 3389) and Desktop Sharing
(TCP 3390) workflows, with separately configured system/user credentials.
Those observations concern the tested server configuration and do not establish
a universal client/security/desktop contract. See the original GNOME study for
full provenance and limitations.

## 2. RDP client comparison and implementation decision

| Client | Findings relevant to joetoo-kwin integration |
| --- | --- |
| KRDC | KDE client with RDP/VNC capabilities. GUI/window handling and independent managed identity require client-specific verification. |
| Remmina | GUI client with profiles and delegation/tab behavior that can complicate process-to-UUID ownership. |
| `xfreerdp` | Useful CLI client/reference; native Wayland support is not implied by its process model. |
| SDL3 FreeRDP | Chosen for the **first managed RDP implementation**, supported by native-Wayland and X11 lifecycle evidence. Its prior auth dialogs and viewer-role behavior require positive correlation. |

**Architecture decision:** supported TigerVNC-over-authenticated-SSH and
supported RDP integrations are equal, independently selectable client options.
SDL was chosen *first in engineering sequence*, not as preferred/default.
Future clients require their own invocation, security, window identity and
lifecycle contracts. No automatic selection/fallback is implied.

## 3. Native SDL lifecycle evidence

**X11 (`gmki91`):** Successful runs revealed two successive marked normal
windows with the same SDL child PID and exact marker but distinct KWin UUIDs.
A marker/PID match alone does not identify the persistent desktop viewer on
X11; an explicit, evidence-supported viewer-role discriminator is needed.
Wrong-NLA, cancel and connection-failure runs did not justify registering
an authentication window. This role discriminator belongs to a later
implementation increment, not the initial native-Wayland registration core.

**Native Wayland (`q552u01`):** The effective SDL video backend was explicitly
reported as `wayland`. In the positive evidence, an unmarked credential window
preceded a distinct marked desktop viewer under the launched PID. The viewer
retained its exact marker and unique UUID. Cancellation, wrong password,
connection refusal and an already-open unrelated viewer were observed without
an additional eligible marked viewer.

The five follow-up archives were `GxoO58Q5` (cancel), `BRKiefxH` (failed NLA),
`txX5XzJf` (connection refusal), `kaZuBRs6` (unrelated-viewer coexistence)
and `4DytUoCv` (fresh-client connection), each under the private
`joetoo-rdp-stage-a.<suffix>.tbz2` naming scheme. These five runs retained
2,714 synchronized samples in all, no recorded observer errors and no managed
registration. They were observational feasibility proofs, **not tests of the
production managed RDP selector**. Do not publish raw private captures.

The fresh-client connection was a new process; faster apparent reconnect
cannot prove server-side GNOME session identity or in-process reconnect.
The local viewer's UUID/marker does not establish authentication success,
remote desktop usability, certificate trust or approved security negotiation.

## 4. Identity and registration implications

- Arm an owned transaction *before* starting SDL; capture synchronized source,
  event floor, and window baseline.
- Bind unique exact launch marker, actual spawned child PID and application
  identity to a new qualifying normal-window UUID with complete `added` history.
- Permit delayed marker arrival only on that same new positively observed UUID.
- Exclude unmarked NLA credentials, auxiliary windows, preexisting unrelated
  viewers and ambiguous same-PID windows.
- Fail closed on competing/new-and-disappeared eligible UUIDs, lost history,
  source or PID change, process/window exit, marker loss or timeout.
- Register the exact window only; **do not place, move, focus or stack** during
  Increment 1, and do not silently transfer ownership to a new UUID.
- Reuse existing broker/KWin observations without adding an input-event
  observer or a new observation daemon.

These findings inform the [approved implementation scope](Step1.5c5_implementation_scope.md).
The current [HANDOFF](HANDOFF.md) identifies who is allowed to perform the
next development step; this historical evidence does not.

## 5. Security and remaining acceptance gates

- Actual TLS certificate chain, endpoint/SAN identity, possible pinning,
  exception handling and NLA/security negotiation need a defined, reviewed
  production policy. Successful GUI connection or self-signed certificate
  acceptance in feasibility does **not** establish that policy.
- Passwords, secrets and private endpoint details must not leak into argv,
  configuration, source, logs or public evidence.
- A new public D-Bus registration-only launch interface needs explicit review
  of caller authentication, transaction ownership, PID/FD evidence provenance,
  bounds, cancellation and cross-transaction isolation.
- Native-Wayland implemented selector acceptance on `q552u01`, X11 identity on
  `gmki91`, post-registration placement readiness and configured workflow are
  separate gates. Later X11 success cannot be inferred from native Wayland.

## 6. Source and evidence navigation

- [Complete GNOME Remote Desktop technical study](README_gnome_remote_desktop.md)
- [Historical HANDOFF with original detailed RDP matrices and captures](https://github.com/JosephBrendler/joetoo-ai/blob/8f01b6859b3242333ffaa46c931629813921539b/workspace/projects/joetoo-kwin/task_step1.5/HANDOFF.md#15c5c-findings--research-2026-11-03-native-evidence-reviewed-2026-11-04)
- [PR #28 — accepted RDP feasibility](https://github.com/JosephBrendler/joetoo-ai/pull/28)
- [Task history](README.md) · [Active dispatch](HANDOFF.md) · [Implementation scope](Step1.5c5_implementation_scope.md)

**Editorial next step:** A full physical consolidation would embed the original
GNOME study and transfer the corresponding historical HANDOFF investigation
sections into this document, leaving the old filename as a compatibility link.
That is a separate byte-preserving migration to perform against the latest
available local originals; it has **not** been falsely claimed complete here.
