# Step 1.6 native managed-close adapter — candidate

This source candidate has not been installed, loaded or accepted natively.
It provides the small native boundary missing from KWin scripting. The broker
retains authority and transaction state; the effect does no placement, rendering,
recipe selection, application supervision or generic process-tree termination.

## Build and load boundary

The inspected SDK/release sources are KWin **6.7.6**, kwin-x11 **6.7.6**, Qt
**6.11.3** and libxcb **1.17.0**. Both effect variants compile locally. Build
against the actual host SDK: the KWin effect factory IID includes the exact
KWin version, and the normal loader rejects incompatible versions. The factory
also refuses a mismatched compositor executable before constructing native
window code; the Wayland/X11 namespaces must still be installed correctly. A compositor
upgrade requires rebuilding/reviewing the adapter. No KWin patch is involved.

For review builds only:

```bash
cmake -S native/managed-close -B /tmp/joetoo-close-wayland
cmake --build /tmp/joetoo-close-wayland -j2
cmake -S native/managed-close -B /tmp/joetoo-close-x11 -DJOETOO_KWIN_X11=ON
cmake --build /tmp/joetoo-close-x11 -j2
# End of commands

```

CMake prepares install rules for the appropriate Qt plugin directory:
`kwin/effects/plugins/` for KWin, **`kwin-x11/effects/plugins/` for kwin-x11**,
and the fixed helper in KDE's libexec directory. Do not mix variants/namespaces.
The effect is disabled by default. Installation and an explicit normal KWin
`org.kde.kwin.Effects.loadEffect("joetoo_managed_close")` are maintainer actions,
not steps executed by this candidate. Verify the installed compositor/SDK version,
plugin metadata/path, helper executable, and native service ownership first.
The POC user installer adds only the broker's new Python module; it does not
install or load native code. No package/HOME setup or service restart happens
as a side effect of compilation.

## Minimal interfaces and ownership

Public broker interface remains `org.joetoo.KWinBridge`, with three additions:

- `PrepareManagedClose(s JSON) -> s JSON` (asynchronous): exact keys
  `protocol:1`, `scope:"one"|"all"`, `managed_id:"win-NNN"|""`, `settings:{...}`;
  optional `terminal:{service,session,window}` contains Konsole hints only.
  Actual caller credentials must include same-user D-Bus `ProcessFD`, matching
  PID, start time and liveness. Broker Busy/source checks run before preparation.
  The response contains `request_id`, `state`, redacted fixed `targets`,
  `excluded`, retention flags and `self_terminal`. No application is closed.
- `CommitManagedClose(s request_id) -> s JSON`: only the original authenticated
  D-Bus owner can confirm a still-live prepared request. Replays/expired previews
  fail. After acceptance, caller/terminal loss does **not** cancel the broker job.
- `ManagedCloseStatus(s request_id) -> s JSON`: retained redacted per-target
  results, inspectable from another console. Unknown/evicted results are explicit;
  this is bounded in-memory history, not durable broker-restart recovery.

The private native service/path/interface is `org.joetoo.KWinCloseNative`,
`/org/joetoo/KWinCloseNative`, `org.joetoo.KWinCloseNative`. The broker requires
its unique owner to equal `org.kde.KWin` and authenticates that process with
D-Bus `ProcessFD`. Calls address that pinned unique name. The effect accepts
calls only from the watched unique owner of `org.joetoo.KWinBridge` on the
session bus; owner replacement invalidates pending work.

Private native methods are `Inspect(uuid)`, `Terminal(pid)` (optional warning
proof only), `Close(token,uuid,pid,class,grab_ms,absolute_monotonic_expiry_ms)`
and `Status(token)`, returning bounded application-authored JSON. The effect
re-resolves the original UUID, checks its live native object, normal-window
status, PID/class/backend and closeability. No caller-selected UUID is admitted
through the public close API. The native token identifies one target dispatch;
replies for another target/job cannot advance the broker transaction.

Konsole warning proof uses its read-only `Session.processId()` and
`Window.sessionList()` with authenticated Konsole process credentials and
invoker ancestry/start times, then an unambiguous native window for that PID.
Multiple native windows, unavailable APIs or inconsistent evidence yield
`unknown`, never a class/title/PID-only warning or a blanket assertion.
These hints do not grant close authority. No sensitive Konsole API is enabled.

## X11 lifetime fence and graceful-only dispatch

A UUID lookup alone does not protect a stale native XID. The helper uses a
separate authorized XCB connection and a **short server grab**, default 100 ms,
validated 10..500 ms. It sends a random 128-bit marker to an unmapped InputOnly
mailbox created by the effect on **KWin's own XCB connection**. The challenge
travels only over an inherited private Unix `SOCK_SEQPACKET` socketpair, never
argv/environment/logs or the stdout pipe. Per-message `SCM_CREDENTIALS` pins both
the actual helper PID and its original compositor parent; pre-fork socket creator
credentials are not mistaken for child identity. The helper is non-dumpable before
requesting the nonce. The supported Qt pre-exec hook duplicates only this socket to stdin; other
compositor descriptors are closed on exec. It runs no KWin/XCB code in the forked
child. Signal reset/unblocking makes the helper watchdog independent of inherited
compositor signal handling. It must not become available to an
X11 client before the grab, since a pre-grab forged marker could bypass the fence. This is not a
window observer. Wrong DISPLAY/server/authorization cannot yield the matching
marker on that connection, so it cannot produce GO.

KWin processes that marker through its ordinary `X11EventFilter`. On the
inspected native X11 path, Qt's normal FIFO event processing applies preceding
Destroy/Unmap notifications before the marker; those event types are not
compressed away. XWayland uses KWin's own XCB event loop. The effect re-resolves
and compares the **same original object, UUID, backend and XID**. It performs
no X-server round trip while the helper holds the server. Only then does it
write GO to the authenticated private socket. Other X clients cannot destroy/reuse the
resource while the helper owns the grab.

The helper checks bounded `WM_PROTOCOLS` with exact type ATOM, format 32 and
no trailing data, requiring `WM_DELETE_WINDOW`. It sends exactly that protocol
message, checks server processing, ungrabs and disconnects. Missing capability,
BadWindow, wrong type, incomplete data, expired lease or absent GO sends no close.
It never invokes KWin X11 `closeWindow()`, `killWindow()`, XKillClient,
DestroyWindow on an application, or a process signal against an application.

The helper has an absolute monotonic dispatch lease and an independent monotonic process watchdog
(grab budget plus 10 ms cleanup allowance), including blocking XCB setup/library calls. All normal
reply/GO waits share the shorter grab budget. Disconnection releases the grab
on every error. Parent death kills only this helper. KWin dispatch can itself
need an X round trip while processing a preceding destruction; then the helper
times out/releases the server and **does not close anything**. OS scheduling and
kernel uninterruptible states are not hard real-time guarantees.

A native Wayland target uses ordinary `EffectWindow::closeWindow()` only after
positive Wayland/X11 discrimination. Applications may refuse or show unsaved-work
UI. Existing KWin unresponsive-client UI is not automatic joetoo force-killing.

Source grounding: installed `effect/effect{,handler,window}.h`, `window.h`,
`x11eventfilter.h`, and retained release `src/effect/effectloader.cpp`,
`src/x11eventfilter.cpp`, `src/events.cpp`, `src/dbusinterface.cpp`; Qt's
`src/plugins/platforms/xcb/qxcbconnection.cpp`; kwin-x11's `KWIN_PLUGINDIR`
is `kwin-x11`. These sources establish the candidate mechanism; live compositor
ordering/load behavior still requires the native acceptance below.

## Transaction/result semantics

Flow: CLI fields/config → original Python frontend bus connection → authenticated
broker PREPARING/PREPARED preview → confirmation → broker RUNNING → native
exact-target dispatch → authenticated native disappearance → retained result.
Targets serialize; later registrations never enter the fixed set. Prepared work
expires without dispatch. Already missing/uncertain targets are excluded and keep
reservations. Per-target refusal/no disappearance times out without a resend or
force escalation; known-reaped attempts can proceed to the next fixed target.

Legacy `ObserveWindow`/`SyncInventory` messages do not authenticate destruction.
Only the native effect's original-window closed signal proves completion.
Successful closure updates presence to missing and leaves identity, slot and
placement history intact. Forged/mismatched responses, owner/source loss or
unknown dispatch/helper reaping produce unresolved/cleanup-uncertain state and
block conflicting work. A terminal result cannot conceal owned resources.

The effect never blocks unload indefinitely waiting for a helper: an unreaped
Qt process object is detached for Qt-only reaping after the bounded wait; service
loss makes the broker result uncertain. A conservative uncertain transaction
stays blocked for maintainer investigation; no automatic ownership reset is
provided. Broker restart has no recovery/continuation promise.

An already-issued application close cannot be recalled. A delayed application
response can remove the window after timeout; that does not turn the old request
successful or authorize another close. No claim of atomic bulk close/rollback is
made. Window disappearance, local SSH termination and remote tmux persistence
remain independent outcomes. RDP/VNC workers keep their existing cleanup roles.

## Maintainer-only acceptance, after separate install/native approval

First q552u01 Wayland, then slim2 X11; gmki91 is additional X11 coverage.
Use disposable application windows/unsaved work, never irreplaceable sessions.

1. Verify matching SDK/compositor, native effect namespace/version and service
   owner equality with org.kde.KWin. An unloaded/mismatched adapter must fail
   before any close. Start with `-l`; retain managed IDs, UUIDs, desktops/slots
   and placement. An observed but unmanaged window is never eligible.
2. Confirm `-d` on a disposable managed Konsole/Dolphin. Decline once first:
   nothing closes. Then confirm: only the original UUID disappears; `-l` retains
   the missing record, same slot and placement. A second close does not adopt
   another window. Existing unmanaged windows remain untouched.
3. Exercise native Wayland and XWayland separately, then native X11. On X11,
   a client without WM_DELETE must not be killed. Exercise teardown/replacement
   around the fence; stale/reused XIDs must fail without closing a replacement.
   Confirm the normal event-loop fence ordering on each actual compositor.
4. Exercise a normal refusal/unsaved-work dialog: dispatch is not success; timeout
   neither kills the application nor dismisses its dialog. Refusal in a bulk set
   permits only the remaining previously confirmed, still eligible targets.
5. Run `-x` with multiple registered clients and an unrelated unmanaged window.
   Verify one snapshot, one confirmation, serialized outcomes, retained slots,
   partial results and no unrelated close. Close the invoking terminal only in a
   disposable managed-member test: warning only with positive proof; broker work
   and `ManagedCloseStatus(REQUEST_ID)` remain available from another console.
6. Verify an ordinary managed Konsole/SSH close terminates its local foreground
   SSH process while a deliberately persistent remote tmux session remains.
   Verify RDP/VNC ordinary close lets their existing workers clean owned resources.
7. Recheck `-L`, `-l`, a representative mixed `-o`, strict RDP NLA/certificate
   defaults and service/application separation. Do not change certificates or
   restart services merely to bypass Busy/uncertainty.

Headless tests cover real broker/registry/CallerIdentity and CLI code with fake
D-Bus/native callbacks, and the compiled helper/libxcb wire ABI over socketpairs. Where the sandbox denies
`SO_PASSCRED`, wire tests explicitly interpose a synthetic credential seam and a
separate availability test skips real kernel credentials. An unconfined run uses
the real credential transport automatically; production builds contain no shim.
They cannot establish native loading, Qt/KWin ordering, actual application close,
SSH/tmux or client-worker cleanup. No native operations were run by Codex.
