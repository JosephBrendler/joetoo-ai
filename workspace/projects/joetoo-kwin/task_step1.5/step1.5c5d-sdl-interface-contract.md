# SDL development interface contract v1 — implementation candidate

Scope: four additive methods on existing `org.joetoo.KWinBridge`, path
`/org/joetoo/KWinBridge`, for native-Wayland SDL registration **without placement**.
The maintainer authorized bounded interface implementation/headless testing on
2026-11-06; native execution, deployment and production-security acceptance
remain unapproved.
Reuse the private core, registry and existing sender/UID-check patterns from the
standalone diagnostic; generic/VNC methods and semantics remain unchanged.

## 1. Wire contract

All replies are one JSON string. `s`, `i`, `h` mean string, signed int32 and Unix
FD. No method accepts a selected UUID, backend assertion, password or log path.

| Method | In → out | Contract |
| --- | --- | --- |
| `BeginSdlRegistration` | `s → s` | JSON `{protocol:1, desktop, slot, bounds:{...}}`; pin owner, source/revision, baseline and event floor before spawn. Return `pending`, opaque request ID, exact unpredictable title marker and effective bounds. |
| `BindSdlRegistration` | `sih → s` | Request ID, actual child PID, private regular log FD; validate once, bind process/log evidence, return `pending` or terminal evidence failure. No placement. |
| `PollSdlRegistration` | `s → s` | Request ID; return pending or stable terminal result. Never renew deadline. |
| `CancelSdlRegistration` | `s → s` | Request ID; pending becomes `failed` with reason `cancelled`; terminal result is unchanged. Never unregister or close a registered viewer. |

Every normal reply includes `protocol:1`, `request_id`, `state`,
`placement:"not_requested"`, `remote_session:"unverified"`. Terminal states:
`registered`, `failed`, `ambiguous`, `timeout`; terminal replies have a fixed,
redacted reason code. Only `registered` includes `managed_id` and `window_uuid`.
Cancellation is a failed registration outcome, not a new registry state.
Reason codes: `registered` for success, `competing_uuid` for ambiguity, `expired`
for timeout; failures use `cancelled`, `caller_lost`, `child_identity_rejected`,
`backend_unverified`, `evidence_rejected`, `source_lost`, `history_incomplete`,
`marker_lost`, `viewer_lost`, `budget_exhausted`, `duplicate_ownership` or
`cleanup_failed`. No backend text is used as a reason.

Begin JSON is capped at 8192 UTF-8 bytes; reject duplicate/unknown keys, nonfinite
numbers, booleans as integers, unsupported protocol and invalid desktop/slot.
Bounds use exactly the private adapter's five validated settings/template defaults;
no new policy timer or resource limit. Malformed calls use existing `.BadArguments`
or `.InvalidRequest`; conflicts use `.Busy`; unknown/evicted IDs use
`org.joetoo.KWinBridge.UnknownRequest`; unauthorized calls use standard D-Bus
`AccessDenied`. Errors contain no raw payload/log. A valid owner's first Bind
with rejected child/evidence terminates that intent as `failed`. A second Bind
is `.InvalidRequest`, without replacing or disturbing the first binding.

## 2. Caller and transaction ownership

Use dbus-python's actual sender metadata, never a payload identity. Require the
existing local Unix session bus, non-root broker UID, and bus-authenticated
`GetConnectionCredentials` UID equal to broker UID. Pin unique sender name,
caller PID and bus-provided `ProcessFD`; require this credential for race-safe
caller identity, with **no numeric-PID-only fallback**. Missing process credentials,
Unix-FD transport or Linux pidfd support means unsupported/fail closed. Availability
on q552u01 is a prerequisite to verify, not a demonstrated fact.

One persistent launcher connection must Begin, spawn the direct child, Bind and
Poll/Cancel; separate `qdbus6` invocations cannot own this protocol. Only that
unique sender may inspect/control its request, even if another caller has the
same UID and knows the ID/marker. Caller loss/exit before registration fails the
intent; reconnecting with a new unique name cannot reclaim it. Recheck owner
liveness immediately before commit. After success, owner exit leaves the viewer
and registered UUID intact.

Reuse registry serialization and slot conflicts. Keep one current/last terminal
transaction, matching the bounded private core; a subsequent successful Begin
evicts the prior response cache, never its registry entry. Old IDs cannot affect
the new transaction. Authenticate/authorize before mutation. Unauthorized calls
cannot cancel, expire, rebind, disclose or overwrite another owner's state.

## 3. Child, descriptor and evidence provenance

Bind requires a live same-UID **direct child** of the pinned launcher, born in
this armed launch interval. Pin its Linux pidfd and `/proc` start-time identity;
check identity/liveness before and after reading metadata and before registration.
Never reopen a reused numeric PID as the original process. Reject exit,
reparenting, UID/start-identity changes or unverifiable provenance.

For this development profile, require `/proc/PID/exe` to match the pinned,
resolved `/usr/bin/sdl-freerdp` executable (root-owned, executable, not group/world
writable); reject wrappers, shells and other binaries. Verify this path on the
native host before testing. This is not the final configured executable grammar.
Require the child's initial `SDL_VIDEO_DRIVER=wayland` setting as corroboration;
retain the PID-matching SDL `wayland` log requirement and exact KWin application,
marker, new normal UUID, source and complete lifecycle checks. Never export
`/proc` environment contents, command lines or raw log data.

Take ownership only of the received FD duplicate. Require readable, regular,
non-append read access, UID-owned, mode 0600, one link, bounded file size and
stable device/inode. Reject pipes, sockets, directories, devices and invalid FDs.
Require it to identify the actual child's stdout log inode; revalidate process
identity around this check. Use independent-offset `pread`; check size,
permissions/link count, truncation, byte budget and backend contradictions while
pending. Close every received/duplicated FD on rejection, duplicate Bind or
completion; never close the launcher's writer or signal the viewer.

**Trust limit:** this authenticates a local account/connection and corroborates
child/window identity; it does not attest launcher code. The authorized same-UID
launcher can write its log, and the existing KWin observation protocol is not a
security boundary against a malicious same-account process. Neither FD ownership
nor pidfds make fabricated logs cryptographically authentic. This contract rejects
structurally forged/substituted evidence and non-owner interference; protection
against a malicious owning launcher is explicitly outside it and would require
a separately approved trusted-spawn/observation design.

## 4. Failure, cleanup and tests

The configured monotonic budget runs from Begin receipt, including asynchronous
credential lookup; never block the GLib loop waiting for bus replies. Lookup and
arming do not restart the budget. Bind/Poll/activity cannot extend it. Watchdog, source/revision/history/marker guards and configured budgets
remain active without polling. Caller loss, child exit, bad evidence or cleanup
failure prevents registration. Cleanup is bounded/idempotent: remove callbacks,
close broker-owned caller/child/log descriptors and release only the unregistered
intent. Queued callbacks are inert. The spawning launcher owns child reaping and
private-log retention; cancellation does not authorize broker process signals.
No window mutation, ownership transfer, security downgrade or fallback occurs.

Headless gates must exercise the real wrappers plus private core and registry:
wrong/missing sender, different UID, same-UID non-owner, guessed/stolen ID,
owner disconnect/PID reuse, unsupported credentials/FD transport; unrelated,
preexisting, reparented, wrong-executable/UID/start-time or exited child; invalid,
public, substituted, truncated, oversized or leaked FD, wrong stdout inode,
forged PID/backend line and driver contradiction; malformed/repeated Bind,
concurrent Begin, stale IDs and cross-transaction cancellation; expiry without
Poll, terminal idempotence, bounded callback/FD cleanup and no placement on every
path. Retain all private-core identity tests and full generic/VNC regressions.
A fabricated but internally consistent log from the trusted owning launcher is
not claimed to be detectable. No native acceptance follows from headless PASS.

Primary references: [D-Bus credentials and ProcessFD](https://dbus.freedesktop.org/doc/dbus-specification.html#bus-messages-get-connection-credentials),
[Python pidfd support](https://docs.python.org/3/library/os.html#os.pidfd_open).

## 5. Implementation and review evidence — 2026-11-06

**Baseline and preserved work:** designated branch
`task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`, HEAD
`5d322e9d254b08248ef6384f5c4815d30b4c267c`. On arrival the adapter, tests and
this contract were untracked; earlier tracked broker/template candidate edits
were absent. Restored only their cleanly matching private-core patch hunks from
`/tmp/step1.5c5d-increment1-registration.patch`, after `git apply --check`;
no older HANDOFF or maintainer source was overwritten. No index/history change.

**Implemented, not deployed:** all four methods retain their v1 signatures and
bind dbus-python sender metadata to one persistent connection. Begin performs
asynchronous bus credential lookup; one bounded lookup is allowed, late replies
release FDs, owner loss invalidates pending work, and the absolute deadline
includes lookup time. Missing optional `ProcessFD` returns `NotSupported` before
arming. There is no numeric-PID fallback. Bind pins the actual direct child with
a Linux pidfd and rechecks start identity, UID, executable, parent, stdout inode
and the initial driver setting. Readers validate private log descriptors and
bounded contents without attestation claims. All broker-owned descriptors and
signal/timer hooks are released on terminal outcomes. Neither broker nor reader
signals, reaps or replaces the viewer. Terminal results use the v1 redacted
schema, and remain stable for the owner.

Both owner-name loss and broker bus disconnection fail pending registration.
Authorization precedes polling/expiry/mutation; a non-owner cannot use an
expired owner's ID to trigger its state transition. Only the watchdog/owner
advancement does so. Failure to read/revalidate process or log metadata is a
rejection, never permission to substitute another PID or UUID.

Existing 32 public declarations retain their signatures/decorators; exactly four
SDL methods are added. All pre-existing Broker method bodies are AST-identical
except initialization and the two private observation taps from the private core.
Registry, resident, VNC modules, CLI and shared launch functions are byte-unchanged.
No placement request, desktop/geometry/layer/focus operation or configured recipe
is added. Bounds remain the existing five private settings/template defaults.

**Read-only availability preflight:** this environment has dbus-python,
`os.pidfd_open`, and D-Bus daemon 1.16.2. A connection to the already configured
local session bus was denied with `org.freedesktop.DBus.Error.AccessDenied`
before credentials could be discovered. Therefore live `ProcessFD` availability
is **unverified, not absent**; daemon version alone does not establish it.
A disposable isolated-bus test also could not start: Unix socket bind returned
`Operation not permitted`. This is a sandbox/test-facility limitation, not an SDL
identity failure. No desktop service was started or changed. Real dbus-python
method metadata was validated without connecting to a bus; live message dispatch
and Unix-FD marshalling remain untested here.

Maintainer-only read-only preflight on q552u01, in its existing graphical session:

```bash
python3 - <<'PYCODE'
import dbus, json, os
address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
if os.geteuid() == 0 or not address.startswith('unix:') or ';' in address:
    raise SystemExit('Existing local non-root session bus required')
bus = None
try:
    bus = dbus.bus.BusConnection(address)
    proxy = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspect=False)
    credentials = dbus.Interface(proxy, 'org.freedesktop.DBus').GetConnectionCredentials(
        bus.get_unique_name(), timeout=3)
    print(json.dumps({'credential_keys': sorted(map(str, credentials)),
        'uid_matches': int(credentials.get('UnixUserID', -1)) == os.geteuid(),
        'pid_matches': int(credentials.get('ProcessID', -1)) == os.getpid(),
        'ProcessFD_available': 'ProcessFD' in credentials}))
    if 'ProcessFD' in credentials:
        os.close(credentials['ProcessFD'].take())
except dbus.DBusException as error:
    print(json.dumps({'preflight_error': error.get_dbus_name()}))
finally:
    if bus is not None:
        bus.close()
PYCODE
# End of commands

```

If this reports `ProcessFD_available:false`, keep the implemented gate closed.
The source-grounded alternative for **separate approval**, not implemented, is a
launcher-created **self-pidfd**, opened before Begin and retained with its bus
connection, using Linux's existing pidfd lifetime semantics and Unix-FD transport.
It would require amending Begin input to `sh` (JSON plus caller self-pidfd), while
retaining four operations. The broker would validate the FD's kernel PID against
bus-authenticated PID/UID, pin start identity/liveness and apply the same child
checks. That pins the supplied process lifetime but is **caller-supplied**, not
bus-attested provenance; it relies explicitly on the trusted owning launcher and
is not a silent equivalent to the bus credential. Missing/mismatched/dead FDs
would still reject. Approve or reject that narrow signature/trust amendment only
if actual credential absence is established. No such fallback is enabled now.

**Test method:** disposable
Python children simulate SDL output and the executable-identity seam; no SDL,
Wayland/X11 display, credentials or remote endpoint was exercised. PID reuse is
simulated through changed kernel-metadata snapshots while retaining real pidfds;
no host PID churn or unrelated-process manipulation is performed.

### Actual validation and disposition

- `PYTHONPATH=tests python3 -m unittest test_rdp_broker test_rdp_launch -q`:
  **97 PASS**, no failures/errors/skips.
- `python3 -m unittest discover -s tests -p 'test_*.py' -q`:
  **575 PASS** in 88.625s, no failures/errors/skips. Earlier 573-test run passed;
  final bus-disconnect checks prompted the final full rerun.
- `node --test --test-isolation=none --test-reporter=spec tests/test_*.js`:
  **99 PASS**, zero failures/skips.
- In-memory compilation of broker/adapter/two test modules, Bash template syntax,
  `shellcheck -s bash -e SC2034 joetoo-kwin-template.conf`, tracked/new whitespace:
  PASS. SC2034 is intentionally excluded for sourced config assignments. No Python
  linter or live D-Bus marshalling PASS is claimed.
- Real dbus-python decorators verify the four signatures/sender metadata without
  creating a service. Existing public declarations and pre-existing method bodies
  (apart from initialization/two observation taps) and protected-file comparisons
  pass. Positive/negative fixtures assert placement inactive and all registry
  placements `not_requested`; unauthorized operations leave owner state untouched.

Complete uncommitted candidate (including private core and all untracked files):
`/tmp/step1.5c5d-sdl-public-interface.patch`. This is a reproducible review export;
source/tests and this focused document remain retained in the task working tree.
Earlier private-core patch is preserved; temporary insertion/governance snippets
are superseded/disposable, fully represented elsewhere. Disposable child/log
fixtures were cleaned by tests. No unique engineering work or native evidence
exists only in new temporary storage. Existing evidence was not relocated or
cleaned; no staging, commit, push, installation or deployment occurred.

**Next actor:** maintainer reviews this candidate and repeats the read-only
credential preflight on q552u01. Report `ProcessFD` present/absent or the exact
redacted failure before native approval. If absent, decide the separate lifetime-
provenance alternative; current code remains fail-closed. Live FD marshalling,
production security settings and native registration-only acceptance need their
own maintainer-operated validation; no X11, placement or later increment begins.
