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
Unix-FD transport or Linux pidfd support means unsupported/fail closed. The
maintainer subsequently verified ProcessFD/ProcessID/UnixUserID/UnixGroupIDs with
matching UID/PID on q552u01; this prerequisite is satisfied on that tested bus.
No alternative self-pidfd interface is needed or implemented.

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

## 6. Installer integration and non-networked smoke preparation — 2026-11-06

**Baseline:** `2938ec977f6a556ca27f432550369387d41a944a` on the existing
`task/joetoo-kwin-step1.5c5d-managed-rdp-implementation` branch. The maintainer's
uncommitted short HANDOFF updates were present before this work and are preserved.
No historical iteration table was restored. The maintainer independently reports
575 Python / 99 JavaScript PASS on gmki91, four live SDL signatures exposed there,
and successful q552u01 credential preflight including ProcessFD. These are
maintainer observations, distinct from the headless checks below. Earlier sandbox
preflight limitations in §5 remain historical, not an unresolved host prerequisite.

### Installer change and bounded review corrections

The existing installer now includes `rdp_launch` in the same source/destination,
mode, check, immutable content-addressed archive and install/update inventories.
It installs `~/.local/libexec/joetoo_kwin_rdp_launch.py` at 0644 and reports ten
managed files plus the SDL adapter path. Missing, altered, wrong-mode, non-regular
or symlink adapter destinations cannot pass check. Check now validates the current
UID for every managed component, complementing the archive's existing ownership
checks. No separate install mechanism or restart-wrapper responsibility was added.
The maintainer's restart wrapper and all broker/registry/resident/adapter/VNC/CLI
runtime sources remain byte-unchanged in this iteration.

Seven focused installer cases cover missing/outdated/wrong-mode, nine-to-ten
upgrade and repeat-update stability, preserved bytes/mode/provenance, symlink
refusal, archive failure before replacement, running-service refusal and simulated
foreign ownership without privileged chown. Existing all-component mode/archive
and preview-count tests now cover ten files; six-file upgrades add both VNC and
SDL dependencies through the ordinary installer.

The disconnected-caller tests now examine internal stable terminal reporting
instead of issuing an external Poll through a lost connection. The fixture
rejects Begin/Bind/Poll from a disconnected sender/transport; a regression checks
that prohibition. Owner-name loss is not mislabeled as an actual owner-process
exit. Both RDP test modules now put `unittest.main()` after all classes, including
the public declarations and smoke tests, so direct execution discovers them.

**Logging source review (no SDL run):** installed pkg-config metadata identifies
FreeRDP client 3.32.1. The cached matching release tarball SHA-256 is
`3021cf8848efbd0064664e187cb61e6101e4e74a4d8ffb495d9f7715e22d67de`.
`client/SDL/SDL3/sdl_freerdp.cpp:695–696` uses `WLOG_DEBUG` for the driver message.
`winpr/libwinpr/utils/wlog/wlog.c:127` defaults to the CONSOLE appender;
`ConsoleAppender.c:118–127` routes TRACE/DEBUG/INFO to stdout and higher levels
to stderr; `:260` selects default stream policy. The SDL source contains no
appender override. Thus stdout is the source-supported default expected by the
adapter, rather than stderr-only capture. `WLOG_APPENDER` or explicit appender
settings can change routing. The console writer uses `fprintf` without an
explicit flush; prompt visibility in a regular redirected file is not proved.
The previous proof merged stdout/stderr, so it cannot independently distinguish
streams. No logging policy/runtime change is needed for this no-child smoke;
later SDL acceptance must verify effective logging settings and timely visibility.
Do not weaken the backend check or silently substitute another evidence stream.

### Maintainer procedure — prepare now, execute only after review/approval

Run from a local non-root Plasma Konsole on q552u01 in its existing session.
Do not use separate qdbus invocations for Begin/Cancel. The new verification client
uses one persistent connection and imports the **installed** adapter without
writing bytecode. It never launches SDL, invokes Bind, selects an endpoint,
reads credentials or performs a remote network operation.

First use the existing approved maintainer update/start procedure; these commands
have **not been executed by Codex**:

```bash
cd /home/joe/joetoo-ai/workspace/projects/joetoo-kwin
./tools/restart_joetoo-kwind notest
./tools/joetoo-kwind-install-poc --check
cmp -- libexec/joetoo_kwin_rdp_launch.py "$HOME/.local/libexec/joetoo_kwin_rdp_launch.py"
stat -c '%U %a %n' "$HOME/.local/libexec/joetoo_kwin_rdp_launch.py"
rc-service -U joetoo-kwind status
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge
# End of commands

```

Expected: ten managed components report Current, the adapter matches the checkout,
its UID is the current user and mode is 644, and the service reports started.
Introspection must expose Begin `s→s`, Bind `sih→s`, Poll `s→s`, Cancel `s→s`.
The four signatures were maintainer-observed on gmki91; this corrected installed
path and live Begin/Cancel behavior have **not yet been observed on q552u01**.
Begin currently checks installed `/usr/bin/sdl-freerdp` executable metadata even
though this smoke does not execute it; that binary must remain available.

Before arming anything, the client requires synchronized inventory, an empty
managed registry, no pending/running registration, no active initial layout or
uncertain viewer cleanup, and IDLE placement with no request ID. Existing unmanaged
windows are allowed. If synchronization is still pending after startup, inspect
RegistryStatus until it is synchronized; do not bypass the guard. Avoid concurrent
launchers, moves, restarts or source reloads during the short smoke test.

```bash
python3 tools/joetoo-sdl-registration-smoke.py --call-timeout-ms 3000
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge org.joetoo.KWinBridge.RegistryStatus | jq '{observation, placement_transaction, managed_count, request_count, request_counts}'
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge org.joetoo.KWinBridge.ListManaged | jq .
# End of commands

```

The adjustable call timeout is for this verification client, not an identity quiet
period. The client passes installed adapter defaults explicitly as registration
bounds. It pins the broker's unique owner and verifies all four XML signatures.
It performs Begin → Cancel → terminal Poll → repeated Cancel, then a second
Begin/Cancel cycle as a reservation-release probe. All calls use the same bus
connection. Any exception fails the smoke; best-effort owner cancellation runs
when the request ID is known, and main always closes the connection so owner-loss
cleanup can finish if a reply is lost. Do not treat a timeout as successful cleanup.

Expected passing client JSON:

```json
{"active_requests":0,"broker_owner_unchanged":true,"cancelled_transactions":2,"managed_count":0,"ok":true,"placement":"IDLE","source_unchanged":true}
```

From a fresh restart, RegistryStatus should show request_count=2, failed=2,
pending=running=0; ListManaged should show count=0 and windows=[]. Placement must
remain `{id:null,state:"IDLE"}` and observation source/synchronization remain valid.
The two failed records/last cached terminal response are intentional history,
not active transactions. The second Begin proves the previous active reservation
was released. Subsequent read-only RegistryStatus/ListManaged calls demonstrate
that ordinary broker queries remain available; this is not a new native test of
Konsole/Dolphin/VNC launch behavior. Internal timer/FD release is headless-tested,
not directly observable through those read-only methods. Any source/owner change,
nonempty registry, active work, unexpected counts or terminal result is a failed
or inconclusive smoke. The count guard may conservatively reject a heavily used
bounded history; use the reviewed fresh-start procedure rather than bypassing it.

This gate does not test Bind's input Unix-FD marshalling, an SDL backend, a viewer
UUID, TLS/NLA, credentials, placement or remote usability. No native PASS is claimed.

### Validation and next decision

Actual checks executed this iteration:

- `PYTHONPATH=tests python3 -m unittest test_openrc_user_setup test_rdp_broker test_rdp_launch -q`:
  **156 PASS**, no failures/errors/skips (11.758s).
- `python3 -m unittest discover -s tests -p 'test_*.py' -q`:
  **591 PASS**, no failures/errors/skips (90.278s).
- `node --test --test-isolation=none --test-reporter=spec tests/test_*.js`:
  **99 PASS**, no failures/skips.
- Direct `python3 tests/test_rdp_broker.py -q`: **80 PASS**;
  direct `python3 tests/test_rdp_launch.py -q`: **26 PASS**, confirming all classes
  are discovered, including the declarations and smoke tests.
- `sh -n tools/joetoo-kwind-install-poc`,
  `shellcheck tools/joetoo-kwind-install-poc`, in-memory Python compilation of the
  new client/changed tests, tracked/new-file whitespace checks: PASS.
- Byte comparisons against HEAD confirm the maintainer's restart wrapper, broker,
  adapter, resident, registry, VNC modules and CLI were preserved.

Complete current-working-tree diff (including the new smoke client):
`/tmp/step1.5c5d-installer-smoke-review.patch`. It includes the maintainer's
pre-existing HANDOFF changes as well as the small, explicitly labeled Codex
follow-up; the original maintainer dispatcher is preserved. Source/tests/client
and this focused evidence record are retained in the checkout, with no source
or meaningful findings existing only in `/tmp`. The patch is a redundant review
export; test-owned temporary files are disposable and cleaned by fixtures. No
existing native evidence was moved/deleted and no historical cleanup was done.
No staging, commit, push, installation, deployment or live smoke execution.

The eight smoke-client tests reuse the actual broker/registry fixture, including
no-child/no-placement success, quiescence/introspection guards, missing ProcessFD,
lost cancel reply, owner replacement and cleanup. Native service execution was
not attempted. The next maintainer decision is approval of this installer/client
candidate and the above bounded Begin/Cancel procedure before operational execution.

## 7. Accepted smoke and persistent launcher candidate — 2026-11-06

**Accepted maintainer evidence:** q552u01 at `2bb9c74` passed two native
Begin/Cancel cycles: zero active requests/managed windows, unchanged owner/source,
IDLE placement, and two intentional terminal cancellations. The maintainer has
accepted that bounded gate and previously verified ProcessFD. The 156 focused
checks and ten-component installation/signatures passed on both hosts. These
are maintainer results, not native executions by Codex. §6 remains the earlier
preparation record; its pending smoke decision is superseded by this acceptance.

**Candidate baseline:** `2bb9c741d817ada9f3ab7577b9f37b73e4f2c7aa`, branch
`task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. Pre-existing maintainer
changes to HANDOFF and the restart wrapper are preserved without agent edits.

### Implemented ownership and lifetime

`tools/joetoo-sdl-registration-launch.py` uses one explicit existing local Unix
session-bus connection, pins the broker owner and checks all four signatures.
It validates arguments/executable and synchronized/quiescent broker state, then
Begins before directly spawning `/usr/bin/sdl-freerdp`. No shell, wrapper, path
search, log-forwarding pipe or alternate executable is used. POSIX Python Popen
waits for its exec error pipe before returning (`subprocess.py:1938–1949` on the
inspected Python 3.14 installation); positive native child verification remains
mandatory regardless of this source behavior.

It retains a child pidfd, checks parent/executable, and Binds the actual PID plus
a separately opened read-only UnixFd duplicate of the private stdout inode.
The existing broker independently verifies bus ProcessFD, UID, parent, start
identity, executable, environment, descriptor and full KWin lifecycle/UUID.
Polling never supplies a chosen UUID or renews the Begin deadline. Reply IDs and
registration-only result fields are checked; owner substitution/unknown IDs are
errors. There is no reconnect/retry/UUID replacement path or placement call.

SIGINT/SIGTERM request cancellation through ordinary control flow. Pending
failure uses best-effort same-connection Cancel, then closes the connection even
if a reply/ID is lost. A disconnected sender issues no further external call.
The launcher stops/reaps only its direct child: retained pidfd TERM, bounded
wait, pidfd KILL, bounded wait. The configurable call timeout (default 3000ms,
100–30000ms) also bounds each cleanup wait. If child pidfd allocation fails before
Bind, ordinary Popen cleanup is restricted to its still-owned unreaped direct
child in this single-threaded launcher; no provenance fallback is offered to the
broker. Cleanup failure is an error, never successful registration.

After registration it reports the exact UUID/managed ID promptly and stays in
the foreground supervising/reaping the child. Broker replacement/disconnection
**after success** does not trigger child closure. Operator cancellation or log
integrity/budget failure stops its own child; success never unregisters or
transfers the UUID. Child exit status is reported separately; launcher exit 0
means local registration occurred, not remote login/transport success. SIGKILL
or host/process failure cannot guarantee user-space cleanup.

Logs are created atomically at 0600 in a new 0700 temporary directory, retained
on success and failure, never echoed or automatically removed. stdout and stderr
share this regular file. Evidence reads remain capped by the existing byte
budget. The supervisor checks metadata/size every configured poll interval,
including after registration, and stops the child on excess. This is **not a
hard filesystem quota**: writes can overshoot between checks/while stopping.
No truncation or evidence synthesis hides that outcome. Private logs may contain
endpoint/authentication context; retain them locally, outside public Git.

### Logging qualification and proposed remedy boundary

The matching FreeRDP 3.32.1 source cited in §6 confirms console DEBUG output to
stdout, but its `fprintf` has no explicit flush. `wlog.c:117–167,742–760,885–900`
and `Layout.c:404–441` establish inherited `WLOG_APPENDER`, `WLOG_FILTER`,
`WLOG_LEVEL` and `WLOG_PREFIX` overrides. The narrow adapter change clears those
four child-only overrides, explicitly selects `CONSOLE`, and retains the existing
SDL DEBUG filter and canonical Wayland driver setting. The parent is unchanged.
No TLS/NLA/certificate flag or parser acceptance is changed. Merging stderr into
the same private stdout inode preserves diagnostics; it does not attest which
stream emitted a line or make caller-writable evidence independent.

**Still unverified:** timely visibility of the real backend line while SDL is
alive with this regular-file redirection. Neither Popen `bufsize` nor flushing the
parent's file flushes the child's libc stdout. A no-flush disposable-child test
expires without registration; raising timeouts is not positive backend evidence.
If native testing confirms buffering prevents registration, stop that gate.
A minimal evidence-preserving remedy for **separate approval** is a validated
root-owned `libstdbuf` preload into the direct SDL exec with `_STDBUF_O=L` (or 0),
without a wrapper/pipe or inode change. Cached coreutils 9.12 `src/libstdbuf.c`
implements `_STDBUF_O` with `setvbuf`; `src/stdbuf.c` injects LD_PRELOAD then
execs. Library path/ownership, dependency and loader/trust implications require
review; **no preload or stdbuf is implemented or approved here**. Do not substitute
FILE/UDP logging, accept environment alone, fake/flush a backend line, or weaken
process/UUID evidence. Timeliness remains a native gate, not a headless claim.

### Proposed q552u01 procedure — requires maintainer approval before execution

Use the existing non-root local Plasma/Konsole session. Review this diff first;
update/check the installed adapter through the already approved maintainer-owned
installation procedure. This candidate deliberately refuses an installed adapter
whose bytes/UID/0644 mode differ from the checkout. No restart-wrapper repair or
installation was performed by Codex. Keep other launch/move/restart activity idle.
Use an unoccupied desktop/slot and a maintainer-approved endpoint/test account
with acceptable existing certificate/negotiation behavior. This launcher provides
no password argument, certificate exception or security-negotiation override.
Stop on an unresolved trust/security prompt; this procedure grants no exception.

In terminal A, after the reserved native authorization:

```bash
./tools/joetoo-kwind-install-poc --check
rc-service -U joetoo-kwind status
qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge
read -r -p 'Approved test host: ' RDP_TEST_HOST
read -r -p 'Test username (no password): ' RDP_TEST_USER
python3 tools/joetoo-sdl-registration-launch.py "$RDP_TEST_HOST" "$RDP_TEST_USER" --desktop 1 --slot 1 --rdp-registration-timeout-ms 300000
# End of commands

```

Expected (not yet observed natively): private evidence directory, actual child
PID/start and request ID, then either a redacted failure or `registered` with exact
UUID/managed ID, `placement:not_requested`, `remote_session:unverified`. Keep A
alive. At the unmarked NLA dialog, leave it visible briefly and use terminal B:

```bash
bus=org.joetoo.KWinBridge
path=/org/joetoo/KWinBridge
qdbus6 "$bus" "$path" "$bus.RegistryStatus" | jq '{observation,placement_transaction,managed_count,request_counts}'
qdbus6 "$bus" "$path" "$bus.ListManaged" | jq .
read -r -p 'Child PID printed by launcher: ' RDP_TEST_PID
ps -o pid=,ppid=,stat=,comm= -p "$RDP_TEST_PID"
readlink "/proc/$RDP_TEST_PID/exe" "/proc/$RDP_TEST_PID/fd/1"
# End of commands

```

Before an eligible viewer: no new managed entry, placement IDLE, synchronized
source; PPID must be A's Python launcher and executable the approved SDL binary.
Enter credentials only through SDL's own prompt. Once the real viewer appears,
expect one exact registered UUID, never the credentials UUID. Use existing KWin
Debug Console read-only inspection to compare viewer PID/application/exact marker
and UUID with `GetManaged <managed_id>` observation. Compare desktop, geometry,
stack/focus evidence before/after registration, allowing ordinary SDL/user-driven
window creation/activation; no broker placement request is allowed. Viewer
registration at GDM is sufficient here and proves no GNOME authentication.

While the child remains alive, read only bounded backend evidence in terminal B:

```bash
read -r -p 'Evidence directory printed by launcher: ' RDP_TEST_EVIDENCE
python3 - "$RDP_TEST_PID" "$RDP_TEST_EVIDENCE/stdout.log" <<'PYCODE'
import json, sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path.home() / '.local/libexec'))
from joetoo_kwin_rdp_launch import BackendEvidence
with open(sys.argv[2], 'rb') as log:
    reader = BackendEvidence(SimpleNamespace(pid=int(sys.argv[1])), log, {})
    try:
        print(json.dumps({'observed_backend': reader.read_backend()}))
    finally:
        reader.close()
PYCODE
# End of commands

```

Expect `wayland`; `null` means no complete accepted line yet. Keep raw logs private. Absence until process exit is failure of
the timeliness gate, even if the line later appears. Do not use a second bus
connection for Bind/Poll/Cancel; A alone owns those operations. Live FD marshalling
and successful Bind are established only by this operational run, not by source.

Close the viewer normally after collecting evidence; A must reap it and report
child exit separately. Repeat fresh invocations for NLA cancellation, wrong NLA
password, approved refused local endpoint and Ctrl-C while pending. Expect no
new managed entry on those runs, no active pending/running transaction afterward,
unchanged source/owner and IDLE placement. Leave an unrelated existing viewer
open for a separate isolation check. Registered entries from the positive run
may remain present/missing history; compare baseline IDs, not an assumed empty
registry. Do not restart the broker to hide a failed cleanup. Read-only
RegistryStatus/ListManaged/GetManaged must remain available. Any unexpected
registration, source change, FD/backend/identity failure or placement ends the
gate for maintainer review; no X11 or subsequent increment follows automatically.

### Actual headless validation and review disposition

- `PYTHONPATH=tests python3 -m unittest test_openrc_user_setup test_rdp_broker test_rdp_launch test_rdp_development_launcher -q`: **178 PASS**, 11.874s.
- `python3 -m unittest discover -s tests -p 'test_*.py' -q`: **613 PASS**, 93.970s.
- `node --test --test-isolation=none --test-reporter=spec tests/test_*.js`: **99 PASS**, zero failures/skips.
- `python3 tests/test_rdp_development_launcher.py -q`: **22 PASS**, 0.304s; all classes discovered.
- In-memory compilation of launcher/adapter/new tests; tracked and new-file
  whitespace; protected-runtime comparisons: PASS. No Python linter/native PASS
  is claimed. Initial new-test execution exposed a test-fixture monkeypatch
  collision; separate test instances corrected it before these final runs.

The new tests use disposable Python children, real pidfds, the actual public
broker wrappers/private selector/registry and a fake persistent transport. They
cover ordering, direct-child/FD provenance, pending/registered replies, cancellation,
child exit, buffered/contradictory evidence, forged PID/substituted log, competing
UUIDs, busy/unknown IDs, mismatched replies, owner replacement/caller loss,
deadlines/log budget, pidfd allocation failure, reaping and no placement.
Existing broker tests retain PID-reuse, unauthorized-sender and cross-owner gates.
Broker, registry, resident, CLI, generic/VNC paths and smoke client are unchanged.

Complete review export, including new files and clearly separable pre-existing
maintainer HANDOFF/wrapper changes:
`/tmp/step1.5c5d-persistent-launcher-review.patch`. Source/tests/evidence remain in
the working tree; this export and test logs are redundant review copies. Test
fixture directories/children are disposed; existing native evidence is untouched.
No implementation, source or finding exists only in temporary scratch storage.
No installation, native execution, network operation or Git publication occurred.

**Next decision:** maintainer review of this candidate, then explicit authorization
for the proposed q552u01 direct-child/Bind/backend/exact-UUID native gate. The
buffering remedy, any security-policy/interface expansion and publication remain
separate decisions. Increment 1 is not yet natively accepted.
