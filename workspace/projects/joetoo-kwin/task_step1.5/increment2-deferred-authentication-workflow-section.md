## Deferred decision — interactive authentication, placement and multiwindow scheduling

**Decision status:** OPEN. This is a forward-looking dependency for §5A
**Increment 3 (controlled placement)** and **Increment 4 (configured `-o` workflow)**,
with security/time-limit verification in **Increment 5**. It does not broaden
Increment 2 or authorize new implementation/native tests. Consider a plan with,
for example, four RDP and two VNC connections spread among many desktops.

**Distinct stages and window identities:** An SDL FreeRDP client-side NLA/credential
dialog may precede creation of the persistent viewer; it must not be adopted as
a managed desktop viewer merely to allow placement. A GDM login greeter is
remote content *inside* the viewer after RDP transport/session negotiation, not
the same local window as the SDL credentials dialog. VNC and SSH authentication
must be analyzed under their actual, separate client process/window contracts.
A noninteractive X11 viewer-role selector (Increment 2 Candidate A) eliminates
only a *post-viewer-creation interaction requirement*; it does not eliminate
human authentication that occurs before that viewer exists.

**Future workflow choice requiring maintainer approval:**

- **Staged prompts at launch desktop:** Keep pending NLA/VNC authentication
  dialogs accessible near the launch console. Provide an explicit per-target,
  per-request status/identity mapping and discoverable prompt labeling without
  exposing passwords or conflating a temporary dialog with a registered viewer.
- **Temporary prompt placement:** Consider placing an independently identified
  *unregistered* authentication dialog at its intended desktop, with an explicit
  temporary lifecycle/ownership/cleanup contract. This is **not** placement of
  a registered SDL viewer and cannot rely on a fake managed UUID or class/title
  guess. A dialog need not exist before its launch request reaches authentication.
- **Mixed strategy:** Stage prompts near the operator during authentication,
  then release exact registered persistent viewer windows for later placement,
  subject to separately approved placement/readiness rules. No automatic
  movement or operator-focus stealing is implied.

**Uninterrupted plan execution:** Decide whether a pending interactive RDP/VNC
connection may coexist with continued launching of unrelated plan entries,
including later desktops. A sequential `-o` that waits for credentials or for
post-viewer user activity could suspend a 40-window plan. An asynchronous
or staged plan must still respect the current broker's single active
registration/correlation transaction, per-slot reservation, launcher lock
lifetime and bounded cleanup; concurrency cannot be assumed from the word
“asynchronous.” Define explicit pending, failed, expired and registered
outcomes and how a pending entry is resumed, skipped or cancelled without
blocking unrelated launches or falsely declaring success. This is an Increment
4 design concern, dependent on any necessary Increment 3 window-handling rules.

**Timeout/idle questions — must be measured or sourced; no timeout presumed:**

1. Local FreeRDP/SDL NLA credential-dialog idle behavior and any RDP server
   pre-authentication timeout (including failures/cancellation while unattended).
2. System GNOME Remote Desktop handover/authentication timeouts, *distinct* from
   any GDM greeter idle lifetime after the viewer reaches GDM.
3. Whether GDM/GRD closes, locks or retains the pre-login or logged-in session
   when left unattended across many virtual desktops; behavior on reconnect,
   disconnect and network failure, with server/version specificity.
4. TigerVNC/SSH or other selected VNC client's authentication prompt and
   connection idle behavior, independently of RDP.
5. How these limits interact with configurable per-registration, per-launch and
   whole-plan budgets without hiding stalled, vanished or expired prompts.

Any future native timeout characterization requires its own maintainer-approved
non-destructive procedure. Do not infer unlimited GDM idle life or a specific
NLA/GDM cutoff from earlier successful sessions, and do not use automatic
credential entry, password persistence or certificate exceptions as a workaround.

