# SDL X11 A2 registration contract addendum — DRAFT

**Status:** Proposed wire/source contract for maintainer review, 2026-11-07.
The maintainer accepted **A2 hidden initialization with positive exact-native-XID
completion evidence** in principle as the intended Increment 2 baseline, including
the Section 5 resolver/verification design. Final contract approval remains subject
to the ordering, property and cleanup gates below; no implementation is authorized.
Increment 1 is formally ACCEPTED and COMPLETE. Nothing here authorizes code, builds, packaging, installation,
native execution, publication or Increment 2 acceptance.

This addendum references and does not replace the accepted
[Wayland v1 contract](step1.5c5d-sdl-interface-contract.md). It is subordinate to
[scope §5A](Step1.5c5_implementation_scope.md#5a-increment-15c5d--managed-rdp-implementation)
and the [Increment 2 scope draft](step1.5c5d-increment2-x11-role-identity-scope-DRAFT-2026-11-07.md).
Source baseline: `f53390078e7e86e2f9f9ae2fe564e04c66f70a7f`, branch
`task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. Tracked worktree
clean on inspection; this addendum is the sole untracked candidate.
All new field names, atoms, environment selectors, helper methods and policies
below are **exact proposals requiring approval**, not existing functionality.

## 1. Profile, scope and compatibility

Proposed profile name: **`sdl-x11-a2-v1`**. Support only the reviewed FreeRDP
3.32.1 / SDL 3.4.18 / KWin X11 6.7.5 combination with the approved client patch.
Record actual package/build revisions at acceptance; a different build is not
implicitly validated. Require compiled native-X11 support (the existing SDL3
CMake X11 detection/`WITH_SDL_X11_NATIVE` path), headers/libraries needed for checked
property publication, and the approved proof emitter. A stub/no-X11 build cannot
emit READY. The ordinary desktop profile is one monitor, one desktop
viewer, decorated, floating, non-fullscreen, non-RemoteApp/non-RAIL. Reject
unsupported settings before creating its desktop window. Reconnect, secondary
desktop publication and registered-UUID transfer are unsupported.

The existing four launcher methods retain their names and signatures:
Begin `s→s`, Bind `sih→s`, Poll `s→s`, Cancel `s→s` on the existing bridge.
Proposed X11 Begin JSON has exactly these keys:

```json
{"protocol":1,"profile":"sdl-x11-a2-v1","desktop":1,"slot":2,"bounds":{}}
```

The original four-key Begin shape, with no `profile`, continues to select
**exactly the accepted native-Wayland v1 behavior**. Do not infer a profile from
XDG_SESSION_TYPE, DISPLAY, a log line or window ordering. Reject unknown profile
values, unknown/duplicate keys and invalid types. Unsupported/stock clients must
fail closed rather than fall back to A1, B or Wayland.

An X11 Begin reply retains v1 fields and additionally echoes `profile`. Bind,
Poll and Cancel replies for that request also echo it; protocol remains 1 and
all existing terminal-state/reason semantics remain. Wayland replies are unchanged.
An old broker rejects the new Begin shape; it must not arm a different profile.
The development launcher would gain explicit `--profile sdl-x11-a2-v1`; its default
continues to send the original Wayland shape. This is not a production recipe.

For the direct child only, set canonical `SDL_VIDEO_DRIVER=x11` and proposed
`JOETOO_SDL_X11_A2=1`; remove the legacy driver alias. The patched client recognizes
that opt-in only for this restricted desktop mode and a valid exact launch marker.
Retain the reviewed logging environment, fixed trusted executable and safe argv.
No new certificate, NLA, downgrade, credential or renderer-selection flags.
The broker requires actual PID-matching `x11` backend evidence as well as the
initial driver/opt-in settings. KWin must offer the supported X11 lookup path;
XWayland under a Wayland compositor is not accepted by this initial profile.

## 2. Matching source and earliest positive completion point

Inspected offline release sources:

| Source | Existing behavior / proposed point |
| --- | --- |
| FreeRDP `client/SDL/SDL3/sdl_context.cpp:360–437` | Ordinary desktop creation; select the opt-in here, validate single-desktop mode, and own publication epoch/state here. |
| FreeRDP `sdl_window.cpp:39–72` | Create properties/window at 63, renderer at 68, scale adjustment at 70 and monitor query at 72. Hidden creation is already expressible at 59–61. Capture initial XID after successful creation, before renderer setup. |
| FreeRDP `sdl_window.cpp:246–268` | Scale/size helper returns success/failure; the constructor currently ignores that result. The opt-in path must propagate/check it. |
| FreeRDP `sdl_context.cpp:426–434` | After `SdlWindow::create()` returns, explicitly check local initialization and collection insertion; this is the earliest desktop-specific completion boundary, subject to publication checks below. |
| FreeRDP `sdl_window.hpp:53–54`; `sdl_x11.cpp:50–59` | Existing window/renderer accessors and native `SDL_PROP_WINDOW_X11_WINDOW_NUMBER` lookup. SDL window ID is not native XID. |
| SDL `src/render/opengl/SDL_render_gl.c:1792–1806`; `src/render/opengles2/SDL_render_gles2.c:2317–2332` | Renderer setup may reconfigure the native window. |
| SDL `src/video/SDL_video.c:2310–2320,2653–2659,2713–2864` | Hidden flag suppresses automatic show; failed in-place reconfiguration can destroy/recreate the native window. |
| FreeRDP `sdl_context.cpp:365,496–514` | The existing created-event notification is not positive proof: the scope guard signals even on an error return. Never use that signal as the role predicate. |
| KWin `src/scripting/workspace_wrapper.cpp:305–309`; `src/workspace.cpp:1938–1944` | `getClient(xid)` uses client WindowMatch, not frame/wrapper ID matching. |

These paths are in the locally retained release archives; no source was patched
or compiled. The earlier archive correlation supports, but does not trace/prove,
the renderer-recreation explanation. This contract relies on new positive proof,
not that historical causal inference.

**Initialized** means valid local SDL window and renderer, successful required
scale/size initialization, valid positive-size monitor description, successful
collection insertion, valid current native XID, successful property publication,
one-time show and successful evidence emission. It does not mean first remote
frame painted, GDM authentication, desktop usability, transport trust or indefinite
persistence. No user interaction is required to reach this local role boundary.

## 3. Client lifecycle and hidden-window boundary

The opt-in creation path executes on SDL's existing main/event thread:

1. Validate profile/settings; allocate creation epoch **1** for this launch and
   a fresh 256-bit CSPRNG publication nonce. No second desktop epoch is accepted. Guard later desktop-creation entry points,
   including `SdlContext::addDisplayWindow()` (`sdl_context.cpp:974–977`), against
   another publication; redirection/hotplug/reentry cannot silently create a
   replacement desktop under this profile.
2. Create the desktop SDL window hidden. Check property creation/application,
   window creation and required synchronization outcomes before dereferencing it.
   Read `initial_xid` from its native X11 property; zero/unavailable is failure.
3. Initialize renderer, scale/size and monitor information while hidden. Check
   every required result, including non-null renderer and the initialization
   results currently ignored by the stock path. Initialization failure destroys
   only the owned incomplete object; no successful record is emitted.
4. Read completed native `xid`; set the nonce property specified in §4 on that
   object. Handle X errors and perform a server round-trip before proceeding.
5. Insert the initialized desktop object successfully. Explicitly show it once,
   check show success, hidden flag clearance and current native XID **after show**.
   That XID must equal the property-bearing completed XID. Recheck the property.
6. Emit/flush exactly one READY record. Only afterward report initialization
   success through the normal client control flow. On any failure, invalidate
   publication locally and unwind the owned object; never emit a replacement
   READY or retry under another UUID in this transaction.

Broker registration still waits for KWin's qualifying added/live UUID. A READY
record may arrive before or after the added event; neither alone authorizes it.
An X11 MapNotify/show return is not a KWin UUID or proof of a first remote frame.
SDL's show/synchronization routines may block in the child; external registration
and cleanup deadlines must remain effective without blocking the broker loop.

**Mapping/focus qualification:** SDL X11 `SDL_x11window.c:1538–1569` uses
`XMapRaised`; normal mapping may activate a window under WM policy. This contract
prohibits broker placement/focus/stack mutation, not ordinary client mapping.
FreeRDP `sdl_context.cpp:1663–1669` also explicitly raises hidden windows during
its draw path. Publish/show before entering that path so A2 does not accidentally
introduce an extra `SDL_RaiseWindow`; do not add raise, focus, grab, desktop or
placement calls. Later unexpected hide/recreate during initialization is failure.
Preserve stock behavior outside the opt-in path, including accepted Wayland.

**Boundary lineage:** `initial_xid` and completed `xid` describe observed setup
boundaries. `superseded_boundary_xids` is `[]` when equal, otherwise exactly
`[initial_xid]`. This does not claim exhaustive hidden SDL-internal XID tracing.
The client must keep setup hidden across renderer reconfiguration. No KWin UUID
is fabricated for an unmapped setup object. All actual mapped marked UUIDs must
be retained by the broker; an unexplained mapped predecessor/generation fails.
For this initial hidden profile, any additional mapped marked UUID is unexpected,
even if it later disappears. Do not classify it harmless merely from removal or
from its numeric equality to `initial_xid` after possible reuse.

If implementation inspection/native evidence shows hidden setup leaking mapping,
or a correctness issue requires exhaustive native lineage, stop for review before
adding SDL hooks. Multiple internal hidden replacements alone are not permission
to claim their IDs were observed. Later replacement before registration fails;
after registration it leaves the original record missing, never retargeted.

## 4. Exact client record, native property, bounds and replay

The READY line is ASCII prefix **`JOETOO_SDL_X11_A2 `**, followed by one compact
ASCII JSON object and newline. Exact keys (values below are schematic):

```json
{"protocol":1,"kind":"desktop_ready","role":"desktop_viewer","backend":"x11","pid":42,"marker":"joetoo-rdp-<64 lowercase hex>","epoch":1,"sdl_window_id":7,"initial_xid":100,"xid":101,"superseded_boundary_xids":[100],"publication_nonce":"<64 lowercase hex>"}
```

The marker uses the existing exact grammar; the nonce is independent per
publication. `pid` is the actual client PID. XIDs and SDL ID are positive uint32;
epoch is integer 1, never bool/float. No unknown/duplicate keys, nonfinite values,
embedded newline, extra suffix, arbitrary roles or alternate backends. The SDL ID
is diagnostic and cannot be used for KWin lookup. Initial/final equality and the
superseded list must obey §3. Zero READY records means no enrollment. A second
READY, even identical, is replay/contradiction and fails while pending.

Proposed X11 property: **`_JOETOO_SDL_X11_A2`**, type **`UTF8_STRING`**, format **8**,
PropModeReplace; value is compact ASCII JSON with exactly these keys:

```json
{"protocol":1,"role":"desktop_viewer","pid":42,"marker":"joetoo-rdp-<64 lowercase hex>","epoch":1,"xid":101,"publication_nonce":"<64 lowercase hex>"}
```

This is a new proposed atom/format, not an SDL/KWin standard property. It is set
only on the completed native client XID. Broker parsing applies the same exact
schema/number rules and requires semantic equality to the READY subset. Both
property size and record size are capped by the explicitly propagated existing
`rdp_backend_log_byte_limit`; never read an unbounded X reply. The same limit
continues to cap total pending log evidence. Every partial line and pending proof
counts against that budget. No raw property/log/environment is exported.

Serialize READY emission against other stdout stdio writers: hold stdout's stream
lock across complete record emission and explicit `fflush(stdout)`, check write,
flush and stream errors, then release. No reliance on WLog level, parent flush,
libc default buffering, `stdbuf`, a forwarding pipe or a new FD. `fsync` is not
required for live reader visibility and no durable-receipt claim is made.
stdout remains the same 0600 regular inode validated by Bind. Loss/partial output
fails closed; the existing launcher owns child reaping and private-log retention.

Nonce equality on the current native object prevents accepting an old READY
against a reused numeric XID. Recheck property/inode/process identity around
mapping and commitment. The nonce is an association value, not a secret or a
security boundary against a malicious owning same-UID client. Retain v1's trust
qualification; no cryptographic SDL-log/property attestation is claimed.

## 5. Automatic resolver, single mapping reply and native verification

### 5.1 Why a different initiator is necessary

The existing TigerVNC `managedViewerFromBroker()` is invoked by a registered
shortcut (`joetoo-kwin-resident.js:401–436`); it is not an automatic readiness
service. The inspected plain-JavaScript scripting API supplies asynchronous
`callDBus`, but no general D-Bus signal-subscription facility. Do not invent an
incoming signal handler, depend on an unrelated window event, or periodically
poll for an unbounded future Begin.

**Proposed initiator:** the broker starts a small transaction-local KWin resolver
script through the existing Scripting API, once for pre-spawn readiness and once
for post-READY mapping. This is a bounded KWin-side helper, not a new permanent
observer/daemon or a reload of the production lifecycle resident. The ordinary
resident continues producing the accepted window/source/revision history.
This replaces the earlier proposal that the existing resident spontaneously Take.

Source support: KWin X11 6.7.5 `src/scripting/scripting.h:327–330` exports
`loadScript`/`unloadScript`; `scripting.cpp:111` exports per-script objects at
`/Scripting/Script<ID>`, `:300–353` implements `callDBus` via the shared
`QDBusConnection::sessionBus().asyncCall`, and `:815` implements script loading.
The project already uses load/run paths at `libexec/joetoo-kwind:2064–2092`.
Those existing coordinator calls are synchronous: copy the API/path knowledge,
**not** their blocking five-second calls into the registration loop.

For each job the broker writes an exclusive 0600 private copy of a fixed,
reviewed resolver template in its own 0700 runtime directory. Inject only
JSON-encoded validated job data (no shell interpolation, caller code or paths).
Use a unique `joetoo-sdl-x11-<job_id>` name. Asynchronously call the pinned KWin
owner's `/Scripting`, interface `org.kde.kwin.Scripting`, `loadScript(path,name)`;
check its nonnegative ID, then asynchronously invoke `org.kde.kwin.Script.run`
on `/Scripting/Script<ID>`. Register job/watchdogs **before** invoking load.
A run reply alone is not readiness. Unload only this owned name/ID on completion
or expiry; remove its private file only after confirmed unload. Never unload or
restart `joetoo-bridge`, invoke a shortcut, move a window or autolaunch a service.
If load times out, reconcile a late ID or the unique owned name for bounded
unload; do not assume absence from a missing reply. Uncertain unload blocks new
X11 work and is cleanup failure, never permission to register.

### 5.2 Events and forward progress

**Readiness job:** created by X11 Begin receipt, before any SDL spawn. Its script
executes immediately on run: verify `workspace.getClient`, normal-window/UUID
access and QTimer support; call Take with purpose `ready`; in the callback send
Complete with the resulting readiness challenge and capability result. The broker
also runs the X display probe in §5.5. It arms the launch only after caller/KWin
authentication, synchronized source, positive readiness, successful probe and
confirmed cleanup of these preparation resources. Then it returns Begin's pending
launch specification. No client window, human trigger or mapping proof is needed
for readiness, so there is no Begin/Take circular wait.

**Mapping job:** starts automatically when the broker has parsed a valid READY
record, binding and backend proof. READY receipt starts the mapping deadline;
the first property check (§5.5) precedes resolver dispatch. The script executes
Take with purpose `map`; its callback resolves the descriptor's exact XID at once.
If not yet managed, subscribe only to workspace window-added/removed and relevant
candidate caption/class signals; rerun the same exact-XID lookup on those events.
A single-shot QTimer using the configured registration poll interval is a bounded
fallback for missed/unsupported notifications **only while this job is alive**.
Count callback/lookup work against the event budget. Stop this timer immediately
when match/rejection/expiry occurs; do not poll between jobs. No input selection
or user activity is required.

Send exactly one mapping Complete: a positive synchronous snapshot, an identity
rejection, or `not_mapped` when the mapping job expires. The broker's own deadline
still terminates if no reply arrives. No second script/attempt, renewed lease,
confirm round-trip or reply-resubmission loop occurs in this transaction.

Every load/run/Take/Complete callback is guarded by job ID, pinned unique bus
owners and remaining time. A local single-shot watchdog is installed before each
script Take/Complete call and each broker load/run/unload call, capped by its
applicable phase/cleanup deadline; KWin may omit JavaScript callbacks on
D-Bus errors. On callback absence the script disconnects its temporary signals
and stops its timers; the broker independently expires/unloads the job. Late
callbacks cannot restart it. Owner/source replacement invalidates both jobs and
closes the owning registration; no retargeting to a new broker/KWin/source.

### 5.3 Helper wire contract (proposed, not an accepted API)

Keep the four launcher-facing methods. Two additional KWin-only `s→s` helpers
on the existing bridge path/interface remain proposed:
`TakeSdlX11Identity` and `CompleteSdlX11Identity`. They convey readiness/mapping
evidence and no placement command. Do not reuse or change TigerVNC's interfaces.

At Begin, asynchronously obtain/pin the actual `org.kde.KWin` unique owner and
bus UID; require broker UID and monitor owner loss/replacement. The resolver uses
the pinned broker unique name injected by the broker, never a replacement name.
Both helpers authenticate actual sender metadata against the pinned/current KWin
owner and validate the armed job/source before consuming state. A payload UID,
name, challenge or UUID does not authenticate a caller. Wrong callers use
AccessDenied; malformed authenticated payloads use BadArguments and cannot change
another job. Unknown/expired jobs are inert. Only the owning launcher controls its
registration through Begin/Bind/Poll/Cancel.

Take input has exactly:

```json
{"protocol":1,"purpose":"ready","job_id":"<hex32>","bootstrap_nonce":"<hex64>","source":"<source>"}
```

`purpose` is `ready` or `map`; all values must equal that job's injected values.
One valid Take consumes its bootstrap nonce. No unsolicited idle polling is
supported. On a valid readiness Take return exactly:

```json
{"protocol":1,"action":"ready","job_id":"<hex32>","challenge":"<new hex64>","source":"<source>","remaining_ms":1000}
```

Readiness Complete has exactly:

```json
{"protocol":1,"purpose":"ready","job_id":"<hex32>","challenge":"<hex64>","source":"<source>","supported":true,"reason":null}
```

For unsupported capability, `supported` is false and `reason` is exactly
`unsupported`. The source here is a broker-injected request binding, **not** a
claim that the separate script can read the production resident's revision.
Broker source/owner checks and the readiness receipt fence below provide that
binding. A successful ready Complete acknowledges resolver code execution; it
cannot itself register a window or release Begin before preparation cleanup.

On a valid mapping Take return exactly:

```json
{"protocol":1,"action":"resolve","request_id":"<hex32>","job_id":"<hex32>","challenge":"<new hex64>","source":"<source>","arm_revision":1,"pid":42,"xid":101,"epoch":1,"publication_nonce":"<hex64>","marker":"joetoo-rdp-<hex64>","resource_class":"com.freerdp.client.sdl3","remaining_ms":1000,"poll_ms":100}
```

Mapping Complete has exactly:

```json
{"protocol":1,"purpose":"map","request_id":"<hex32>","job_id":"<hex32>","challenge":"<hex64>","source":"<source>","epoch":1,"xid":101,"publication_nonce":"<hex64>","status":"match","window_uuid":"<canonical UUID>","observed_pid":42,"resource_class":"com.freerdp.client.sdl3","normal_window":true,"marker_match":true,"reason":null}
```

The script re-resolves `workspace.getClient(xid)` at snapshot time, copies actual
PID/class/UUID, checks normal/live status and exact caption, and sends the reply
without pumping events or reentrant GUI operations between read and send. It
never manufactures an added event or selects a different XID. `status` is `match`,
`not_mapped` or `rejected`; for non-match, UUID/PID/class are null, booleans false,
and reason is exactly `no_client`, `identity_mismatch`, `gone` or `unsupported`.
Nonce echo binds the challenge, not an independent reading of the native property.
The broker checks that property separately. No arbitrary caption/error is returned.

Complete response for either purpose is exactly:

```json
{"protocol":1,"action":"stop","job_id":"<hex32>","accepted":true,"barrier_revision":2}
```

This acknowledges accepted helper evidence and processed observation revision,
**not registered/remote success**. An authenticated duplicate receives the cached
acknowledgement without advancing state; a conflicting duplicate fails its job.
An obsolete job returns `accepted:false,barrier_revision:null` with the same shape;
it cannot revive work. There is no `confirm`, `check_id`, `wait` or repeat phase.
All messages retain the 8192-byte ceiling, exact keys/types, canonical UUIDs,
hex32/hex64 IDs, nonnegative safe-integer revisions and no duplicate/nonfinite JSON
or booleans masquerading as numbers.

### 5.4 Observation acknowledgement and why one mapping phase suffices

The one-shot helper does not share the lifecycle resident's JavaScript variables.
It therefore **does not invent or echo an allegedly current observerRevision**.
Instead Complete is an authenticated **receipt fence** for the existing producer:

- The production resident is installed first; its lifecycle/property handlers
  run synchronously on KWin's scripting/main thread before a later helper's
  snapshot/send. No helper event pumping or nested GUI wait is permitted.
- In the inspected KWin implementation, both scripts' `callDBus` use the same
  process-global `QDBusConnection::sessionBus()` (`scripting.cpp:300–353`). The
  producer's ObserveWindow/SyncInventory calls and helper Complete go to the same
  pinned broker owner. D-Bus delivers method calls from that connection in order;
  replies need not be ordered. See the [D-Bus tutorial](https://dbus.freedesktop.org/doc/dbus-tutorial.html).
- The broker processes observation validation/revision/history mutation
  synchronously in GLib, before acknowledging a later Complete. Capture actual
  sender metadata for ObserveWindow/SyncInventory for this X11 fence; require
  the pinned KWin connection for its source. This is a proposed X11-only provenance
  check, not a change to accepted Wayland/generic payloads or signatures.
- At Complete receipt, validate source unchanged, synchronization, revision at
  least the arm floor, and no gap/eviction; acknowledge the **broker's processed
  revision R** as barrier_revision. Match the snapshot UUID/facts against that
  exact retained added/current history. An ahead-of-producer or forged reply must
  not be treated as a completed fence.
- After this fence, perform the second native-property batch and current process/
  source/history/liveness checks. Recheck any observations received meanwhile
  immediately before commit. Clean up mapping resources before registration.

**Mandatory ordering gate:** source inspection establishes the shared outgoing
API, not a completed live ordering proof. In this checkout the lifecycle producer
uses `callDBus(BRIDGE, PATH, BRIDGE, ...)` with the well-known broker name
(`joetoo-kwin-resident.js:288–290,373–378`); the proposed helper addresses its
pinned unique owner. Require those names to resolve to the **same unique recipient
at each send and receipt**, as well as the same authenticated KWin sender. They
are not identical destination header strings. A broker-owner change invalidates
the fence even if the well-known name is reacquired. The existing observation
handlers have no sender capture yet; the proposed X11 check must supply it before
this gate can pass.

Establish all of the following, with source references and later integration
traces: both scripts use the same session-bus connection/unique sender; lifecycle
signal callbacks actually enqueue observations before the mapping snapshot/send;
the bus preserves their method-call delivery order to that unique recipient; and
the broker finishes synchronous history/revision mutation before accepting
Complete. Source evidence includes KWin `scripting.cpp:348–351`, the resident's
`sendObservation`/synchronous signal handlers, and broker `ObserveWindow` and
`SyncInventory`; none alone proves the entire chain. A revision integer or nonce
cannot substitute for any missing link. Missing added evidence must reject, not
wait a guessed interval until a later observation makes an earlier fence look valid.

The shared connection, producer-before-snapshot execution and synchronous consumer
ordering are mandatory implementation/acceptance preconditions. Stage 0 below can
check protocol consequences under controlled orderings; mocks cannot establish
real Qt signal or bus scheduling. The later native gate must capture actual sender,
resolved destination, source/revision and receive/processing order without exposing
private titles. If source or integration evidence cannot establish the chain,
**stop for an explicit barrier redesign**. No arbitrary delay, second sample or
asserted-but-unverified transport ordering may enable registration.

No concrete correctness failure was identified that a second resolve/confirm
snapshot alone prevents: it merely takes another sample and still needs the same
property, lifecycle and ordering checks. It cannot prevent disappearance just
after its last reply. Remove it. Single snapshot + authenticated receipt fence +
fresh native/property/process checks preserve exact proof without extra round trips.
Liveness remains a latest mutually corroborated state, not an atomic guarantee
against future disappearance; subsequent removal marks the registered UUID missing.

### 5.5 Concrete asynchronous property verifier

**Selected mechanism:** a broker-owned, disposable Python worker performs libxcb
work; the broker integrates its private nonblocking output pipe with GLib. This
isolates even `xcb_connect`, atom lookup, `xcb_flush` and synchronous property
reply calls that can block. Do not claim that polling replies alone makes XCB
connection setup nonblocking, or that such integration exists in the RDP broker.

Read-only source precedents are `libexec/joetoo_kwin_vnc_identity.py:129–231`
(disposable native worker, nonblocking parent pipe, parent-death signal) and
`tools/joetoo-rdp-x11-use.py:124–195` (ctypes libxcb/property reply validation).
Reuse those techniques, **not** their blocking constructor/select/close loops
and not modifications to VNC behavior. Implement an RDP-specific worker entry
point in the approved adapter/helper envelope.

Requirements and sequence:

1. Parent uses existing stdlib ctypes/subprocess support and gi.repository.GLib;
   worker loads libxcb 1.x and libc through ctypes. Bind explicit native signatures
   for xcb_connect/connection_has_error/disconnect, intern_atom/reply,
   get_property/reply and length/value accessors; free every reply/error with libc.
   No python-xlib/xcffib dependency is presumed. libxcb 1.17.0 `src/xcb.h:576–596`
   documents connection/error checking; generated xproto property ABI must be
   checked by isolated native-ABI fixtures, including 32-bit format/LP64 layout.
2. Use only the broker's pre-existing local DISPLAY (`:N[.screen]` or
   `unix:N[.screen]`) and XAUTHORITY/default Xauthority resolution. libxcb handles
   normal X authorization. Do not accept client-supplied display/auth paths, read
   its /proc environment for credentials, change xhost, or try remote X/TCP.
   Missing authorization/display/library fails before spawn during probe. No
   automatic service/environment repair is authorized. A display that differs
   from KWin cannot pass subsequent nonce/XID/UUID corroboration.
3. Start one `probe` worker during readiness; it connects/authenticates, checks
   XCB setup/error status and exits. It creates no atom, property or window. Later
   launch one `read` worker per pre/post-mapping batch using validated numeric XID,
   limit and opaque job identifier as argv (no credentials or shell). Read workers
   use only-if-exists atom lookup, then read `_JOETOO_SDL_X11_A2`, `_NET_WM_PID`,
   `WM_CLASS` and `_NET_WM_NAME`. Precheck begins after READY and before map-script
   dispatch; postcheck begins after the single reply/fence. There are at most one
   preparation probe and two property batches; no native-read retry loop.
4. Each worker sets Linux parent-death SIGTERM and checks parent PID after setting
   it, as the existing VNC worker does. Its stdout/stderr are private pipe/DEVNULL,
   close_fds enabled; no SDL stdout/evidence FD is inherited or substituted.
   Emit exactly one bounded JSON result with job ID, mode, status and validated
   facts; raw bytes/auth material/arbitrary exception text never cross the pipe.
   A failed batch has a fixed rejection code. Probe/read must exit 0 before their
   result can count; a complete line followed by a hung worker is not success.
5. Parent immediately sets the pipe fd nonblocking and installs
   `GLib.io_add_watch(fd, GLib.PRIORITY_DEFAULT, IO_IN|IO_HUP|IO_ERR|IO_NVAL, cb)`
   and watchdog/child-status timers. PyGObject 3.58.0
   `gi/overrides/GLib.py:856–861` supports this API. Drain with os.read only while
   immediately available, cap cumulative output/partial JSON by the existing
   evidence byte budget, and return to GLib on EAGAIN. Consume final buffered bytes
   before interpreting EOF/HUP; ERR/NVAL, excess output or malformed JSON fails.
   Reap via nonblocking Popen.poll() on timer/pipe callbacks; do not combine a
   second waitpid owner with GLib child_watch or call blocking wait/select here.
6. XCB GetProperty uses delete=false, offset zero and a long_length derived from
   the configured byte limit. Validate error pointer, reply status, exact type,
   format, lengths and bytes_after=0 before copying. PID must be one CARDINAL32;
   class/name must match the approved bounded identity grammar; the nonce property
   must match §4. BadWindow, absent/changed property, denied authorization, lost
   connection, atom/type/length error and worker EOF/exit/timeout fail closed.
   Never accept a partial reply as a truncated valid value. The parent separately
   compares process/pidfd/start/inode facts around each completed batch.
7. No X event masks, raw input, root-client enumeration, property writes or GUI
   mutation are needed in this verifier. It is not the diagnostic activity
   observer. Connection/reply waits are isolated in the worker; broker D-Bus and
   watchdog dispatch remain responsive even against an unresponsive X server.

**Native property acceptance (both batches):** use GetProperty with ANY type so
that actual type/format can be validated; never coerce a wrong-type value. Require
bytes_after=0, exact returned byte/item counts and the configured cumulative byte
bound before decoding. XCB format 32 is uint32 data, not an array of C unsigned
long on LP64. All atoms are looked up only-if-exists; absence fails the batch.

| Property | Required type / format | Exact acceptance |
| --- | --- | --- |
| `_JOETOO_SDL_X11_A2` | `UTF8_STRING` / 8 | The complete bounded ASCII JSON in §4, with no NUL or extra bytes and exact READY-subset equality. |
| `_NET_WM_PID` | `CARDINAL` / 32 | Exactly one uint32 (four bytes), equal to the bound live direct-child PID; never sufficient on its own. |
| `WM_CLASS` | `STRING` / 8 | Exactly `instance\0class\0`: two nonempty strings, both terminated, no third string/trailing bytes. Parse instance first, class second. For this restricted profile require ASCII bytes matching the reviewed executable basename (`sdl-freerdp`) and exact application class (`com.freerdp.client.sdl3`), respectively. No case folding, splitting on whitespace, concatenation, wildcard or interchange of fields. |
| `_NET_WM_NAME` | `UTF8_STRING` / 8 | A nonempty, strictly valid UTF-8 byte string equal to the generated ASCII marker, byte for byte; no trailing NUL, decoration, whitespace, suffix or embedded NUL. |

SDL 3.4.18 `src/video/x11/SDL_x11window.c:793–799` assigns `res_name` from
`SDL_GetExeName()` and `res_class` from `SDL_GetAppID()`;
`src/filesystem/unix/SDL_sysfilesystem.c:258–270` derives the executable basename.
FreeRDP 3.32.1 `sdl_context.cpp:81–87` sets the app identifier from WmClass or its
default. This profile permits no override of that reviewed tuple; a differently
named packaged executable needs explicit profile review, not a runtime alias guess.
KWin 6.7.5 `src/x11window.cpp:3882–3885` supplies name/class separately to
`Window::setResourceClass` (`src/window.cpp:181–185`). Compare parsed instance to
the broker's synchronized `resource_name` for the verified UUID and parsed class
to both its `resource_class` and the mapping reply. Do not reinterpret STRING as
UTF-8 or treat the class as the instance.

SDL `SDL_x11window.c:2283–2316` publishes `_NET_WM_NAME` via XUTF8StringStyle when
available. A successful title-setting return alone does not establish that this
property exists: that path is compile-conditional and has earlier returns. KWin
`src/x11window.cpp:2375–2381` can simplify its name or fall back to `WM_NAME`;
**neither fallback nor KWin caption equality rescues absent/empty/invalid native
_NET_WM_NAME**. Missing, malformed, wrongly typed, oversized, truncated or unequal
values fail immediately once READY starts verification; no WM_NAME substitute,
replacement decoding, title normalization or retry to wait for correction. The
patched client must publish the exact title before READY, and both pre/post checks
must agree. Changes/loss before commit fail even if KWin's cached caption matches.

On cancellation/deadline, detach the pipe watch, asynchronously terminate only the
owned worker, then escalate TERM→KILL after the configured cleanup interval. Reap
nonblockingly under a final cleanup deadline, close pipes and remove timers. Never
signal the viewer from this verifier. A worker that cannot be reaped or resolver
that cannot be unloaded causes cleanup_failed/uncertainty and blocks a new X11
job; retain its ownership handle rather than pretending cleanup succeeded. The
launcher's existing bounded owned-SDL cleanup remains separate. No new permanent
process, synchronous X call or hidden infinite wait is introduced in the broker.

**Cleanup is a separate acceptance gate, not implied by a terminal reply.** Success
requires acknowledged unload of each owned helper and reaping of each worker,
not merely sending unload/TERM, closing a pipe, receiving complete JSON or seeing
an exit notification. Retain script name/ID/path, worker Popen/pidfd if allocated,
and cleanup state. Watches run only within §5.6 budgets; after expiry retain
unresolved handles/guard without renewing timers. A missing/false unload reply,
unknown load outcome, unreaped worker or exceeded cleanup deadline cannot yield
registered; report cleanup_failed when it is the terminal cause and retain an
explicit cleanup-uncertain diagnostic/guard. If an earlier failure is already
cached, keep that terminal result stable but surface the unresolved cleanup
separately; do not erase its handles or admit another X11 Begin. Clearing the guard
requires positive reconciliation, not elapsed time or a fresh request.

Regression gates must deliberately deliver load IDs, successful mapping replies,
worker output/exit and unload acknowledgements after failure/cancel/expiry and in
duplicate. They may discharge only the corresponding retained resource; they
cannot arm, spawn, commit, retry, change a cached terminal result or clean up a
newer job's resources. A late unload acknowledgement must match the original
unique owner/name/ID; a reaped PID cannot be reused as authority over another
process. Assert bounded timers/watches, retained ownership on uncertainty, blocked
new X11 work, zero placement and no false cleanup PASS on every such path.

### 5.6 Deadlines and resource accounting

All proposed X11-only settings are template/config overridable and explicitly
propagated through X11 Begin bounds. Wayland retains its five accepted settings.
New defaults/ranges proposed for approval:

| Setting | Default / validated range | Starts and covers |
| --- | --- | --- |
| rdp_x11_ready_timeout_ms | 5000 / 100–30000 | T0 at X11 Begin receipt; covers caller/KWin authentication, source readiness, probe, readiness script load/run/Take/Complete and preparation cleanup. D_ready=min(D_reg,T0+ready_timeout). |
| rdp_x11_mapping_timeout_ms | 3000 / 100–30000 | T_READY when the first valid bound READY is accepted; covers precheck, script load/run/Take, bounded window-event wait, single reply/fence, postcheck and cleanup. D_map=min(D_reg,T_READY+mapping_timeout). |
| rdp_x11_cleanup_timeout_ms | 3000 / 100–30000 | One TERM/unload acknowledgement interval and one final KILL/reap/reconciliation interval, run concurrently across owned resources; at most two intervals for terminal cleanup. |

D_reg remains T0 + rdp_registration_timeout_ms, including all pre-spawn work and
interactive authentication. Capture source/baseline/event floor and arm only after
readiness; return Begin before allowing the direct SDL spawn. Pre-spawn failure
returns NotSupported for absent facilities or the appropriate existing error; no
registry intent/client is created. The pending-auth job still prevents competing
Begin calls. Launcher loss cancels preparation just as it cancels an armed intent.

The X11 launcher's existing call-timeout option must be at least
min(registration_timeout,ready_timeout)+registration_poll_ms; validate this before
Begin (for defaults, explicitly use 10000 ms rather than silently relying on the
Wayland 3000 ms call timeout). No change to the accepted Wayland default. Individual
asynchronous load/run/native operations cannot outlive their enclosing phase.
Their callbacks use remaining budget; they never reset a phase deadline.

Readiness ends before spawn. Afterward there is no live readiness helper and no
polling while waiting for NLA/READY. Valid READY is a one-time event that starts
mapping even when it precedes KWin's added event. Mapping expiry, missing
callbacks, source/KWin/broker replacement, failed fence/property or cancellation
terminate the attempt without another mapping script or lease. Before readiness
or mapping success can count, its workers are reaped and scripts unloaded within
that phase budget. Cleanup after expiry is allowed only to release resources;
it does not extend proof validity or permit a late registration. Return/retain
terminal failure while bounded cleanup finishes, and refuse new X11 work if it
remains uncertain. Late load IDs/callbacks are reconciled for cleanup only.

Reuse existing event/window/log budgets for accepted callbacks, bounded lookups,
records and retained candidate histories; one preparation job and one mapping job
maximum, never overlapping or renewed mapping jobs. The mapping watchdog covers
revision/receipt fencing too: no separately renewable barrier timer exists.

## 6. Broker states, commitment and cleanup

Internal X11 states (launcher wire state remains `pending` until terminal):

`PREPARING → ARMED → CHILD_BOUND → AWAIT_PROOF_AND_ADDED → MAPPING → VERIFYING → REGISTERED`

Valid evidence/addition can arrive in either order; every state is under the
original Begin deadline/watchdog. Authenticate and pin caller ProcessFD, direct
child parent/start/pidfd/executable/stdout inode, baseline, source/revision and
event floor exactly as v1. Keep process/backend checks before and after evidence
reads and immediately before registration. Require the approved opt-in build and
actual x11 backend; missing client evidence is unsupported, not permission to guess.

Unlike Wayland, X11 candidate discovery starts as provisional. Retain complete
birth/marker/change/removal history before PID binding and do not enroll its first
marked window. A provisional removal is recorded rather than automatically
registered or silently discarded; proof reconciliation rejects every unexpected
mapped marked UUID. Wayland's existing immediate marked-removal/competition rules
are unchanged. Exactly one final role-qualified UUID must satisfy:

- New, live normal window with retained added event after the arm floor, absent
  from baseline; same source and complete non-evicted ordered lifecycle.
- Bound live child and matching PID/app identity at birth and commitment. Require
  exact marker before qualification and at commitment; late marker arrival may
  qualify only that same positively added UUID, with complete history and no
  subsequent loss/mutation of a qualifying marker.
- One valid READY epoch, consistent boundary data and current native nonce.
- The single authenticated mapping snapshot agrees on exact client XID and
  canonical UUID, with an acknowledged observation receipt fence and fresh
  postcheck; no unexplained mapped predecessors or competing role candidates.
- Registry ownership/slot checks succeed; evidence/mapping cleanup succeeds.

Only then call existing registry registration, **without** placement. Do not route
through a placement-coupled completion method. Intended desktop/slot is allocation,
not a command to move the window. First frame, remote GDM and GNOME state are not
registration prerequisites or inferred successes.

Retain wire terminal states and reason codes from v1. Use `evidence_rejected` for
malformed or contradictory role/property/challenge evidence, `competing_uuid` for
ambiguity, `expired` for deadline, and existing source/history/marker/viewer/child/
caller/budget/cleanup codes where applicable. No new public reason enum is needed.
No evidence before deadline stays pending, then timeout; contradictions fail early.
Terminal results remain stable within the existing one-result cache policy;
completed managed/request history is not erased by a later request.

On terminal outcome remove broker timers/pipe watches and challenge/partial
buffers, close only owned duplicates/pidfds, and make queued callbacks inert.
Boundedly stop/reap verifier workers and unload only owned resolver scripts.
The transaction-local KWin helper releases temporary signals/timers on completion,
expiry or failed callback; the broker unloads it on owner/source loss. The
production lifecycle resident is not reloaded. Broker never signals/reaps the SDL
client; verifier workers are broker-owned with the separate cleanup rules in §5.5.
Launcher retains existing owned-child cleanup and log retention. The native property dies with its owned window; before show, a client
failure removes its owned provisional property/object. After registration, do not
unregister, replace or restart anything to hide failure. No geometry, desktop,
stack, focus, grabs, input capture, certificate changes or automatic fallback.

## 7. Smallest staged implementation envelope — future authorization only

| Stage | Proposed files / boundary |
| --- | --- |
| 1. Client proof candidate | FreeRDP `client/SDL/SDL3/sdl_window.cpp/.hpp`, `sdl_context.cpp/.hpp`, and a narrowly scoped X11/evidence helper (or approved `sdl_x11.cpp/.hpp` extension). Opt-in only; hidden creation, checked initialization, boundary metadata, nonce property, show and flushed record. No SDL patch for initial boundary-lineage contract. Client patch/build/deployment/overlay-ebuild work requires separate maintainer-controlled authorization and protected-repository policy compliance. |
| 2. Offline validator and broker candidate | `libexec/joetoo_kwin_rdp_launch.py`, `libexec/joetoo-kwind`; new client record/property parser, X11 profile/process/backend checks, disposable XCB workers, GLib pipe integration and bounded mapping jobs; preserve Wayland paths. |
| 3. Read-only resolver | New `libexec/joetoo-kwin-sdl-x11-resolver.js` fixed template plus broker async Scripting job driver and the two authenticated helper handlers. Original lifecycle resident stays loaded/unchanged; add X11-only sender capture/fence validation to broker observation handlers without changing their payload/signatures. No VNC/generic placement change. |
| 4. Development integration | `tools/joetoo-sdl-registration-launch.py`, `joetoo-kwin-template.conf` for the three approved X11-only timing settings, focused Python/JS tests and disposable fixtures. No configured recipe/CLI dispatch, installer/package changes by implication. |

Registry is read-only unless a concrete defect requires separate approval. Existing
smoke client, generic/VNC runtime and accepted Wayland contracts are preserved.
Stages are review boundaries, not grants: first review the client proof and helper
wire contract, then authorize each bounded source/test/build/native envelope.

### 7.1 Proposed Stage 0 — test-only authorization envelope (not granted)

**Objective:** isolated resolver-protocol verification before implementing the
helper, broker handlers or native workers. Smallest proposed write envelope:
one new `tests/test_sdl_x11_resolver_protocol.js`, with synthetic fixtures/vectors
inline. Follow the Node `node:test`/`vm`/fake-signal conventions inspected in
`tests/test_step1_3a.js` and `tests/test_rdp_x11_use.js`; leave those files unchanged.
No new production module, resolver template, dependency, package or bus service.
If a second fixture file becomes necessary, request that narrow expansion first.

Read/execute the **existing resident only inside a VM** with fake workspace,
windows, Qt-style signals, timers and `callDBus`; prohibit all mutation methods.
Collect its actual ObserveWindow/SyncInventory messages. Model the proposed
resolver/broker transport as an explicitly test-only protocol trace checker,
not as completed production code or proof of the future implementation. Supply
ready/map messages and authenticated sender/destination metadata as synthetic
vectors; no native KWin, session bus, X server, worker process or SDL is started.

The transport fixture must allow separate send/delivery/handler-completion queues,
well-known-to-unique owner resolution, independent connection identities, delayed/
lost/duplicate replies, fake monotonic expiry, source replacement and cleanup
acknowledgement/reap events. Test automatic readiness before spawn permission,
READY-driven mapping without a shortcut, one mapping reply, observation receipt
fencing, no renewal, cross-job rejection and inert late callbacks. Include positive
ordered traces and deliberately broken sender/destination/order/history traces;
assert the latter cannot enable a success. Model unresolved unload/load/reap as
retained ownership blocking new work; never treat modeled cleanup as an actual
OS cleanup test. Include strict WM_CLASS pair and property type/name vectors from
§5.5 as contract fixtures, explicitly not coverage of an unimplemented XCB parser.

**What this can establish:** current resident callback code's message emission
order under the supplied synchronous fake signals; internally consistent protocol
vectors/state transitions and conservative rejection under injected faults; bounded
modeled resources and no placement calls. Pair these with read-only inspection of
the matching KWin shared-callDBus path and current synchronous broker handlers.

**What it cannot establish:** actual Qt connection identity, signal delivery/
reentrancy order, session-bus routing/dispatch, future helper/broker code, XCB ABI/
authorization, native XID/UUID mapping, OS reaping or FreeRDP publication. A mock
that assigns a shared sender proves only its fixture assumption. Record those
limits and the outstanding source/native gates; never call Stage 0 an X11
registration acceptance or a verified production receipt fence. Once implemented,
real helper and broker code must replace the protocol model in later tests.

**Stop conditions:** a mismatch between inspected producer/transport code and the
required order; no defensible shared-connection/same-recipient premise; a trace
that can register with missing history, unresolved ownership or a stale challenge;
need for production edits, observer hooks, a real bus/display/session, or a new
public contract. Report the exact blocker for review; do not fix it using delays,
extra mapping rounds or scope expansion. Proposed execution is only the new Node
file plus applicable existing headless JS regressions, after explicit Stage 0
authorization. No Stage 0 tests are created or executed by this documentation task.

## 8. Required headless matrix — proposed, not executed

| Area | Positive and negative cases |
| --- | --- |
| Client lifecycle | Hidden creation; same initial/final XID; renderer-driven hidden replacement; non-null renderer/valid scale/monitor/insertion; failure at each required step; no READY on failed show/property/output; final XID differs after show; no unintended explicit raise/focus; desktop reentry/redirection/hotplug; opt-in disabled/Wayland unchanged. |
| Evidence | WM_CLASS instance/class order, missing/extra NUL, reversed/empty fields and wrong STRING type; CARDINAL32 length/LP64; absent/empty/invalid UTF-8 or decorated/NUL-terminated NET_WM_NAME cannot use WM_NAME fallback. Exact complete record and property; partial/delayed/oversized line, wrong schema/type/PID/marker/backend/epoch/nonce; duplicate READY, replay, truncation, mode/inode substitution; flush errors; property missing or changed around mapping. |
| Boundary/history | No fabricated UUID for hidden setup; added before/after READY; unexpected mapped marked predecessor, disappeared competitor, extra epochs, multiple role windows, missing/evicted/reordered added/removal/marker history; unknown hidden internals never falsely claimed enumerated. |
| Resolver/security | Actual broker/helper paths with fake bus/X server: automatic readiness before Begin returns/spawn; READY automatically dispatches mapping; no shortcut; wrong sender/UID/source, missing helper or ProcessFD, forged challenge, guessed request, cross-request replay, bounded not-yet-managed then match, identity mismatch, source replacement, missing load/run/Take/Complete callbacks, expired challenge, duplicate/late reply and no job renewal. |
| Receipt fence | Producer sends added/changed/removed before helper snapshot; same authenticated KWin connection and broker destination; delayed observation delivery precedes Complete processing; exact processed revision acknowledgement; missing/evicted history, wrong observation sender, reordered or unsatisfied fence rejected. Postcheck sees marker/property loss, removal or replacement before commit. |
| Native worker/cleanup | Absent/unauthorized display or libxcb; blocked connect/reply cannot block GLib; correct property type/format/length/bytes_after checks; output overflow/partial JSON/EOF/HUP/error; complete result with nonzero/hung child rejected; TERM/KILL/reap deadlines, late load IDs, failed unload, caller/broker loss and no inherited SDL FD. All callbacks inert after terminal; uncertain cleanup blocks new X11 work. |
| Budgets | Readiness starts at Begin, mapping only at bound READY; no helper polling during NLA; deadlines include probe/load/reads/fence/cleanup; too-short launcher call timeout rejected; timers never renew; source replacement/expiry at each callback; success requires resources released before phase expiry. |
| Reuse/liveness | Destroy/reuse same XID between publication/precheck/snapshot/postcheck/commit, nonce mismatch, different UUID at same XID, wrong PID/executable/parent/start identity, process exit and caller loss at every phase. |
| Registration | Actual registry: one exact UUID; duplicate UUID/slot refusal; stable terminal results; A missing then B distinct registration; unrelated viewers/dialogs excluded; no replacement ownership and no active leaked intent. |
| Compatibility | Full accepted Python/JS regression suites, including generic/VNC/Wayland; no placement on every positive/negative path. Headless proof is not physical/native attestation. |

Use disposable non-networked children/fixtures and no real SDL connection for
broker tests. Client compilation/tests and any synthetic display facility need
separately defined authorization; do not assume this documentation task permits it.

## 9. Subsequent gmki91 native gate — outline only

**NO restart or broker/resident reload, and NO `mw` operations between the recorded
baseline and final checks.** The explicitly approved transaction-local resolver
load/run/unload is protocol work, not a production resident reload; it must leave
`joetoo-bridge` unchanged. Native execution, installation and client-build
integration each need separate approval. Verify the approved patched build, target-bus ProcessFD support and
source versions before the baseline; do not reuse stock-client captures as A2 PASS.

1. Record synchronized source/owner/revision, free intended slot, managed history,
   no active registration/layout and IDLE placement. Keep an unrelated SDL viewer
   available only in its separately approved isolation case; keep logs private.
2. Launch the explicit X11/A2 development profile through one persistent owning
   connection. Complete any necessary pre-viewer NLA authentication normally;
   do not interact with the viewer to trigger registration.
3. Verify no setup-time marked normal UUID is prematurely enrolled. Record initial/
   completed native boundary XIDs and nonce/READY output; independently check the
   live property, child/parent/start/executable/stdout inode and actual x11 backend. Record readiness
   and mapping helper ownership, phase deadlines, sender/fence revision and
   verifier exit/reap outcomes; no helper is left resident between transactions.
4. Compare final client XID, resident resolved UUID and KWin Debug Console internalId,
   marker/application/normal state. Confirm only that UUID registered and no broker
   placement occurred. Ordinary mapping activation is not asserted absent.
5. Close the viewer; verify owned child gone, no pending/running request, IDLE
   placement, unchanged source/owner and the original UUID retained as missing.
6. Separately approved negatives: NLA cancel, refused endpoint, pending Ctrl+C,
   missing/contradictory proof and unrelated-viewer isolation. Native fault injection
   is not implied; cover dangerous/adversarial timing via headless fixtures first.

Stop on any unexplained mapped generation, UUID/property mismatch, setup failure
reported as ready, uncontrolled wait, source/owner change, new focus/placement
operation, leaked state/child or security exception. Retain evidence and report;
do not clear state with a restart or substitute another UUID. No acceptance of
Increment 2 follows until maintainer review of implementation and native results.

## 10. Alternatives, deferred workflow and remaining approvals

**A1** remains an unapproved restricted stock-renderer alternative. Even if both
software rendering and disabled framebuffer acceleration avoid recreation, it still
needs positive successful desktop initialization tied to the exact native XID;
observing no replacement is not that proof. No A1 trial or switch is authorized.
**B** remains the positively demonstrated Nov 5 composite interaction/lifecycle
fallback, with its separate operator-selection contract still unapproved. A2 never
silently falls back to B when evidence is absent, and requires no post-creation click.

Noninteractive role proof removes an avoidable human registration gate. It does
not remove pre-viewer NLA/VNC authentication, establish GDM readiness or decide
where pending dialogs belong. Sequential `-o -f CONFIG` progression, pending-status
alerts/staging/resumption, ownership/lock scheduling and placement remain in the
[deferred workflow](increment2-deferred-authentication-workflow-section.md),
principally Increments 3–4; production security remains Increment 5.

**Maintainer review decisions still required:** approve/revise exact profile and
Begin/reply additions; client opt-in selector, record/atom/schema and build policy;
the two KWin-only helper schemas, automatic transaction-local script dispatch,
shared-connection receipt fence and X11-only observation sender checks; disposable
verifier/GLib integration; the three configurable phase/cleanup budgets;
client failure/show semantics and conservative handling of unexpected mapping.
The selected direction/hidden basis/boundary-lineage principle are already approved;
these precise interfaces and implementation envelopes are not. After approving
this draft, authorize bounded implementation stages explicitly. No general plugin
framework, additional RDP client, protected-repository write or publication is implied.
