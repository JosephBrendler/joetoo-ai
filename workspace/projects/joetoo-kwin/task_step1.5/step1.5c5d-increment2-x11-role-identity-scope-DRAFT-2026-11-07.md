# Step 1.5c.5d — Increment 2 X11 SDL viewer-role identity: scope supplement (DRAFT)

**Prepared:** 2026-11-07 for maintainer/Codex design review.  
**Authority:** This is a requirements/planning draft subordinate to
`Step1.5c5_implementation_scope.md` §5A. It authorizes **no implementation,
no native/network tests, no service changes, no new input observer and no
contract/public-interface change**. Increment 1 is separately maintainer
ACCEPTED; see `step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md`.

## Objective and scope boundary

Extend the accepted exact launch-owned, no-placement SDL registration behavior
to **X11 on gmki91**, discriminating a persistent desktop viewer from a
preceding temporary normal window when both share the **same PID, application
class and exact generated title marker**, but have **different KWin UUIDs**.
No fixed-delay, last-created, last-survivor, largest-window, activation-only,
PID-only or class-only adoption. Preserve complete lifecycle and provenance.

Increment 2 is **registration only**. No GDM/remote readiness assertion,
desktop/geometry/stack/focus mutation, configured `-o`, client preference or
production security policy. No regression of accepted native-Wayland behavior,
generic launch, or TigerVNC behavior. Do not silently replace a registered
UUID with a successor.

## Historical evidence that must not be discarded

The maintainer's early-November X11 investigations found successive exact-marker
normal SDL windows with one child PID but two distinct UUIDs; the first
appeared then disappeared, and the second remained through GDM and the GNOME
desktop. Source: `README_remote_desktop_research.md` §3 and Appendix B,
and the original historical HANDOFF / private proof captures. In an
additional content-free `_NET_WM_USER_TIME` analysis, the **unmarked**
authentication window had activity, the **marked temporary** window did not,
and the **marked persistent** window showed activity. This is positive
candidate evidence for a *composite* predicate, NOT proof that a standalone
user timestamp denotes the application role on every run.

Two corrections to prior design discussion:

1. Activity in the credentials window cannot by itself defeat the proposed
   selector: that window lacks the exact broker-generated marker and is
   excluded before role evidence is assessed.
2. The prior X11 result gives a real alternative to FreeRDP source-instrumented
   XID/role export. **Evaluate the existing interaction-and-lifecycle candidate
   first**, rather than declaring native application-role attestation mandatory.

The *standalone KWin diagnostic* already records the specific UUIDs, lifecycle
and `windowActivated` events, but `tools/joetoo-rdp-window-diagnostic.js`
does **not currently capture** `_NET_WM_USER_TIME`. KWin activation alone
is explicitly recorded with `intent:unknown`; it cannot be relabelled as
physical user interaction. Establish where the historical activity evidence
came from and whether it can be obtained reliably, read-only, precisely per
window/UUID, without sensitive input data or a new input-event hook.

The EWMH `_NET_WM_USER_TIME` / `_NET_WM_USER_TIME_WINDOW` interface is intended
for client-reported last-user-activity time; it can initially contain the
action timestamp that launched the window. Therefore **nonzero alone is not
qualifying post-creation interaction**. X11 server timestamp ordering/wrap,
initial value, per-window association, later updates, and KWin's exact XID→UUID
mapping require source-grounded review.

## Candidate A — content-free, exact-window interaction gate (evaluate first)

This is a **proposal**, not yet an accepted/implemented contract. A candidate
may qualify only if all of these are established:

- Existing `Begin`/`Bind` safeguards: unique authenticated owner, direct
  launched SDL child, pidfd/start identity, verified actual `x11` backend,
  application class, exact unpredictable marker, synchronized observation
  source/revision, complete `added` lifecycle, and a prelaunch UUID baseline.
- The complete history retains every marked candidate, including the temporary
  predecessor; disappearance does not erase evidence of competing windows.
- The earlier marked temporary UUID is conclusively removed, and only one
  *live* eligible marked UUID remains. This is a prerequisite, **not the
  sole basis of selection**.
- Fresh positive, content-free **per-window user activity** on that surviving
  UUID is established **after** the window was created and after the temporary
  marked UUID disappeared. A baseline/nonzero startup timestamp,
  programmatic activation/focus, or a timestamp from another window must not
  qualify. Exactly how this is proved is the first design question.
- The broker revalidates the still-live UUID, PID, title, class, backend,
  source and complete candidate history **at commitment**. Ambiguous,
  missing, malformed, stale, reused or contradictory activity evidence fails
  closed, as do extra marked candidates, disappearance and source/owner loss.
- User input contents (keys, mouse coordinates, clipboard, screenshots,
  credentials) are **not captured**. The evidence is at most that qualifying
  activity occurred, attributable to the exact candidate window and its
  bounded observation time/sequence.
- Interaction is a **positive user-selection gate**, not a cryptographic
  assertion of application internals or proof of remote-desktop readiness.
  This policy may intentionally delay registration until the operator interacts;
  no-interaction or unsupported property then yields no enrollment, not a
  timeout-based guess.

Review whether `_NET_WM_USER_TIME` actually supplies this stronger
per-window/post-birth signal in the installed SDL3/KWin versions, or whether
it can be set/inherited/updated without the requisite user action. Review
any read-only KWin/X11 property observation path as part of the design;
**do not assume the current resident already emits this field**. Avoid
reimplementing an event-capture daemon or adding raw keyboard/mouse observers
without explicit new maintainer authorization.

## Candidate B — source-supported application desktop-role evidence (fallback)

If candidate A cannot meet the acceptance criterion, propose the *smallest*
alternative: a FreeRDP/SDL source-supported desktop-viewer role assertion
associated with the **native X11 XID** and read-only, exact KWin XID→UUID
resolution. Distinguish SDL window IDs from native XIDs; establish whether an
unmodified client already exposes the evidence. No caller-supplied UUID,
boolean `is_viewer`, guessed role property, or source modification is
accepted by this draft. Present client instrumentation as an **explicit
alternative requiring separate approval**, not a prerequisite by fiat.

A hybrid predicate may be proposed if neither candidate alone is sufficient.
Document evidence provenance, correctness/failure cases, complexity and
configuration impact of each candidate before recommending one.

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

## Interface-contract compatibility review

The accepted v1 `step1.5c5d-sdl-interface-contract.md` is **Wayland-only**;
`development_environment()`, backend reader and broker currently enforce
`wayland`. Preserve the v1 document. Propose a **focused Increment 2 X11
addendum** explaining whether the existing four methods and JSON `protocol:1`
can safely be extended, with explicit backend/profile selection and unambiguous
owner-scoped evidence transport. Do not change signatures/schema or add an
observer as an automatic assumption. Shared safeguards (Begin owner/baseline,
Bind process/FD, Poll stable terminal results, Cancel cleanup) remain.

## Design-review deliverables (Codex read-only)

1. Trace the historical activity evidence to the exact proof output and
   differentiate it from KWin `windowActivated` / focus and the standalone
   observer's current fields. Identify gaps without inventing capture results.
2. Trace source (versions used on gmki91) for `_NET_WM_USER_TIME`, the optional
   `_NET_WM_USER_TIME_WINDOW`, activity update semantics, XID→UUID linkage,
   startup timestamp and X server timestamp wrap/reuse.
3. Assess candidate A **first**, including potential false positives/negatives
   and an explicit no-user-interaction timeout outcome. Compare candidate B
   as a bounded alternative, not the default.
4. Draft a narrow **X11 contract addendum proposal**, not an edit to v1, with
   needed evidence, transport, invariants, stop conditions, test matrix and
   any proposed interface-change decision points.
5. Propose headless test cases: temporary-only window, marked predecessor
   removed with no user activity, genuine fresh activity on surviving UUID,
   baseline/startup timestamps, unmarked credentials with activity, competing
   live marked UUIDs, stale/reused XIDs or timestamps, source/owner loss,
   early activity on temporary, wrong backend and no placement.
6. Propose a separately maintainer-authorized `gmki91` native gate that
   verifies the persistent exact UUID and absence of premature enrollment;
   never perform it as part of the read-only review.

## Stop conditions / undecided questions

Stop for maintainer review if no source-grounded way to distinguish post-birth
user activity from startup/activation, or if the only available path requires
new input-event capture, client patching, new D-Bus methods, weaker trust,
new daemon, or native actions. Do not declare X11 accepted from historical
feasibility evidence alone. The maintainer and ChatGPT will review Codex's
comparison and **then decide** the predicate and approve or reject a contract
addendum before any implementation.

## References

- `Step1.5c5_implementation_scope.md` §5A, Increment 2.
- `step1.5c5d-sdl-interface-contract.md` v1 (Wayland-only).
- `README_remote_desktop_research.md` §3, Appendix B, and its linked
  original HANDOFF / private X11 proof captures.
- `tools/joetoo-rdp-window-diagnostic.js` (read-only window lifecycle and
  activation; NOT user-time capture).
- Official EWMH: https://specifications.freedesktop.org/wm/latest-single/
- SDL X11 implementation: https://github.com/libsdl-org/SDL/blob/main/src/video/x11/SDL_x11events.c
