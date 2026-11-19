# Step 1.7 — Combined recovery and last-good snapshot

**Status:** uncommitted Step 1.7 implementation candidate for maintainer review;
headless validation is recorded below. Native acceptance and publication remain
separately authorized maintainer actions. The maintainer
agreed that the former Steps **1.7 (same-session checkpoint)** and **1.8
(durable restorable layout)** should be developed and reviewed as one Step 1.7
milestone with **two separate data and trust contracts**. See the
[current HANDOFF](HANDOFF.md) for decisions and actor; it does not itself grant
code, native-operation or publication authorization.

## What this milestone covers

| Responsibility | Artifact and scope | Key acceptance distinction |
| --- | --- | --- |
| Same-session recovery | Private, atomic `$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json` checkpoint of authenticated managed identity and reservations | Reconcile **existing exact UUIDs** only after verifying unchanged KWin session/source; never close/relaunch on broker restart |
| Last-good layout | Separate trusted `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/last-session.conf` of validated desired launch recipes | `-S` exports only approved intent; `-r` confirms and launches **new** instances without adopting old windows/PIDs/UUIDs |

Keep the shared planner, existing configuration precedence and registration
security model. A correctly placed unreachable-SSH placeholder may be a
valid recipe despite unavailable transport; window/placement success remains
independent of remote login. Avoid an additional generic lifecycle framework.

## Continuity and sources

- [Architecture §8 and unresolved version 1 decisions](../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17).
- [Step 1.6 archived HANDOFF](../archive/task_step1.6/HANDOFF.md) and
  [accepted task index](../archive/task_step1.6/README.md).
- [Native X11 acceptance and original logs/screenshots](../archive/task_step1.6/step1.6-slim2-native-x11-evidence-2026-11-18.md).
- [Wayland/XWayland progressive-sweep evidence](../archive/task_step1.6/step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
- [Project README](../README.md), [project instructions](../AGENTS.md).

**Previous milestone:** Step 1.6 accepted and merged through
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32)
(`a6999e2`). No additional Step 1.6 tests or implementation are prerequisites
for starting the next *authorized* work. Step 1.9 packaging follows this
version 1 objective; [Version 2](../ARCHITECTURE.md#12-version-2-considerations)
remains deferred.


## Local implementation candidate — 2026-11-18

Source baseline: `f18fea2afb9f6e3a474b87ad5969f1606895723e`, branch
`task/joetoo-kwin-step1.7-recovery-snapshot`, initially clean. The maintainer's
current direct assignment authorized implementation and the bounded data/API
additions. This result is a candidate, **not milestone acceptance**. Git fetch
could not update `.git/FETCH_HEAD` (read-only filesystem); the local baseline was
verified without claiming a fresh remote synchronization.

### Implemented contracts

- A private, atomic runtime checkpoint preserves managed IDs, UUIDs, original
  reservations, registration/placement metadata, complete available launch
  intent and the next alias counter. New managed IDs are checkpointed before
  publication. Memory remains authoritative while running; persistence failure
  blocks new work. Ordinary frame/caption changes do not cause disk writes.
- Recovery verifies session-bus identity, KWin's unique owner and mandatory
  D-Bus ProcessFD/UID/PID/start-time continuity. Only authenticated KWin inventory
  and native exact-UUID/PID/class evidence can restore live presence. A legitimate
  resident reload may change observerSource within that same compositor session.
  Unproved records retain reservations as missing/uncertain; pending operations,
  process credentials, close tokens and remote sessions are not resumed.
- Launch-time metadata includes DESKTOP, logical SLOT, PROGRAM, MODE, TARGET,
  explicit/defaulted LAYER and allowlisted effective settings. The legacy launch
  API remains valid; records without complete exportable metadata remain managed
  but make the complete arrangement ineligible for `-S`. Metadata never grants
  registration, window adoption or destructive authority.
- Bare `-S` exports the complete present, successfully placed, authenticated and
  restorable arrangement. Empty/partial/missing/uncertain state, native identity
  mismatch, incompatible effective policies or failed offline validation cannot
  replace last-good state. Only generated assignments/recipe arrays are saved;
  credentials, private logs, PIDs, UUIDs, connection state and tokens are excluded.
- `-r` validates the private generated snapshot, then calls the existing serial
  `open_plan()` path: lock, preflight, reservation checks, confirmation, new
  children/new identities, placement and common initial layout. It does not adopt
  old windows, bypass retained reservations or change the selected profile.
- Version 1 restores **original recipes and policy**, not operator-adjusted
  geometry. Original logical slots retain ordering; new-instance slots are
  derived by the existing planner. Optional `desktop_session_frames` is original
  explicit per-recipe policy (`X|Y|WIDTH|HEIGHT`, or empty), never sampled from
  current windows. Without overrides the original geometry calculations remain
  unchanged. Snapshots explicitly reset absent frame overrides so later defaults
  cannot silently introduce them.
- `snapshot_validation_timeout_ms=30000` (100..120000 ms) bounds offline snapshot
  validation only. It is configurable through existing layers, documented in the
  template and shown at debug severity; it is not an authentication/viewer timer.
- Existing native adapter/resident code, RDP/VNC lifecycle and security defaults,
  graceful close dispatch, and snapshot independence from `-d`/`-x` are preserved.
  The development installer's inventory adds the two Python runtime modules;
  official packaging and live installation remain outside this assignment.

### Additive interfaces and file format

`SubmitManagedLaunchIntent(s JSON) -> s JSON` wraps the original managed launch:
`{intent:{desktop,slot,program,mode,target,layer,settings[,frame_override]},
frame:[x,y,width,height]}`. Original `SubmitManagedLaunch` is unchanged.
`BeginSdlRegistration` and `SubmitManagedViewerLaunch` accept the optional
validated `intent` object; their old payloads remain accepted. Settings are an
allowlisted map of canonical Bash-value strings (pseudo-booleans `0`/empty,
literal enums and decimal numbers); `frame_override` is an optional policy string.
`ExportManagedSnapshot() -> s` requires authenticated same-user ProcessFD
credentials and returns only the generated configuration, not close authority.
`RegistryStatus` adds `recovery_snapshot_protocol:1` and a recovery state.
`ObserveWindow`/`SyncInventory` retain their wire signatures; the broker now
checks the actual D-Bus sender when production recovery is active.

Runtime JSON protocol 1 contains compositor/session proof, source ordering
metadata, alias counter and managed records. Files must be regular, singly
linked, owned by the user and mode 0600 in a mode-0700 private directory;
symlink traversal is refused. Atomic writes fsync both file and directory.
The durable `.conf` contains generated Bash plus a canonical data comment;
`-r` rejects tampering or arbitrary added Bash rather than executing it.

### Headless validation

- Dedicated recovery/snapshot suite: **38 PASS** (4.178 s).
- Focused recovery/configuration/startup/registry/close/installer set: **166 PASS** (38.993 s).
- Full Python discovery: **1054 run, 1053 PASS, 1 SKIP**, no failures/errors (223.618 s).
- JavaScript: **163 PASS**, no failures/skips/cancellations (1016.654 ms).
- Bash/sh syntax, Python AST syntax, ShellCheck and `git diff --check`: **PASS**.

The Python skip is the existing sandbox-denied native credential IPC fixture
(`SO_PASSCRED`), not a claimed native success. An earlier broad run exposed an
obsolete startup bus stub (one ERROR); another exposed two stale configuration
display expectations. Those fixtures were corrected; final full discovery above
ran against the finished source candidate and passed.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_recovery_snapshot
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_recovery_snapshot test_config_presentation test_step1_2a test_step1_4a_registry test_managed_close test_openrc_user_setup
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
node --test --test-isolation=none tests/test_*.js
bash -n joetoo-kwin joetoo-kwin-template.conf libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions
sh -n tools/joetoo-kwind-install-poc
shellcheck -x joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions tools/joetoo-kwind-install-poc
git diff --check
# End of commands

```

Focused tests use the production broker, registry, persistence code,
`CallerIdentity`, real disposable files/ProcessFDs and Python children where
applicable. KWin/native transport and application launches are synthetic.
Development installer tests use disposable HOME directories and service mocks.
They are **not** evidence of native KWin recovery or real RDP/VNC connectivity.

### Maintainer-native acceptance still required

On q552u01 Wayland first, then slim2 X11, after separately approved update:

1. Use a disposable complete managed arrangement with current launch metadata.
   Confirm `-l` identity/reservations and `RegistryStatus.recovery=ready`.
2. Save with `-S`; inspect mode/ownership and verify no runtime IDs or secrets.
   A manual frame change must not become a saved geometric promise. Verify an
   ineligible/missing record causes `-S` to refuse while preserving prior bytes.
3. Restart only the broker under maintainer control. Verify no app/SSH/viewer is
   closed or relaunched, and the same IDs/UUIDs/slots are recovered. Check one
   legitimate resident reload in the same KWin session; unrelated windows must
   stay unmanaged. Unknown/source/native-identity evidence must fail closed.
4. Verify `-r` refuses conflicting retained reservations before launch. In a
   disposable confirmed clean sweep, verify `-x` empties managed reservations
   while leaving last-good unchanged. `-d` must still retain its missing record.
5. Run `-r`, decline once, then confirm. Verify ordinary derived geometry,
   layering/focus, new identities and existing remote/security/SSH-placeholder
   semantics. Do not interpret local placement as remote authentication.

Different KWin/bus sessions and invalid checkpoints are not restart-adoption
paths; they remain unresolved for operator review. Transient placement/close
claims and completed close-result history are not replayed across broker restart.
The durable snapshot is generator-owned; edit ordinary per-run profiles instead.
The native effect's existing authenticated `Inspect` capability must be loaded;
no native source/ABI expansion is included here.


## Refinement candidate — 2026-11-19

The maintainer reports positive q552u01 native Wayland checks of configured
launch (2/2), single launch (1/1), private save, recovery of three original
identities after broker-only restart, conflict refusal, retained single close,
progressive sweep (3/3), declined restore and confirmed restore (3/3 new
identities). The maintainer also reports an unconfined 47-test focused PASS,
including SO_PASSCRED. These are **human-reported results preceding this
refinement**, not native operations repeated by the agent or acceptance of the
new history behavior.

The existing uncommitted candidate was preserved at local HEAD `f18fea2` on
`task/joetoo-kwin-step1.7-recovery-snapshot`. The refinement adds:

- New private sortable UTC/nanosecond/random snapshot files for every save,
  including identical content. Latest is one validated relative symlink;
  file/link publication is atomic and history pruning starts only after
  publication. Failed pre-publication saves preserve prior history/selection.
- `snapshot_history_depth=10` (1..1000), loaded from current optional config
  layers/per-run selection for `-S`; optional `-f` selects settings, never a
  window subset. Depth is independent of original launch/ownership policy.
  Valid regular legacy last-good migrates into history before replacement;
  depth 1 explicitly retains only newest. Post-commit fsync/prune uncertainty
  is reported as a published-save warning rather than a false rollback.
- Snapshot protocol 2: common effective launch settings occur once at plan
  level and recipes keep their own desktop, slot/order, program/mode/target,
  layer and original individual frame policy. Valid protocol-1 snapshots are
  verified and normalized on read without rewriting the old file. Incompatible
  policies are still refused; no arbitrary Bash or secret material is copied.
- Bounded complete relevant historical observations in runtime JSON. Older
  identity-only checkpoints remain valid; `GetManaged` omits unknown optional
  facts instead of crashing or inventing values. Geometry/caption-only updates
  do not write on each event; authoritative changes and clean broker shutdown
  persist last-known facts. They never substitute for fresh identity proof.
- [The user manual](../docs/joetoo-kwin_user_manual.md): all implemented CLI
  forms, configuration/profiles/recovery/history, practical examples and
  troubleshooting, every one of the 41 exposed bridge methods and all four
  native methods, with wire signatures and caller/state/use boundaries.
  Signatures, links and non-executing Bash syntax are checked against source.

Headless verification against this exact refined source candidate:

- Focused: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_user_manual test_snapshot_refinements test_recovery_snapshot test_config_presentation test_step1_2a` — **79 PASS**, 0 failures/errors/skips (17.996 s).
- Full Python: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'` — **1080 run: 1079 PASS, 1 SKIP**, 0 failures/errors (231.236 s). The existing native credential IPC fixture skips because this sandbox denies SO_PASSCRED; this is not evidence of native IPC success.
- Full JavaScript: `node --test --test-isolation=none tests/test_*.js` — **163 PASS**, 0 failures/skips/cancellations (1231.746 ms).
- `bash -n joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions joetoo-kwin-template.conf`, `sh -n tools/joetoo-kwind-install-poc`, and AST parsing of the broker, Python libexec modules and Python tests — PASS.
- `shellcheck -x joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions tools/joetoo-kwind-install-poc` and `git diff --check` — PASS.

These are disposable/headless tests, including 21 refinement and five manual
checks. Manual native examples were reviewed/parsed, never executed. Local Git
metadata cannot be refreshed: fetch cannot write read-only `.git/FETCH_HEAD`;
no fresh remote synchronization is claimed.

No native effect, resident, project architecture/README, policy or archived
evidence was changed. No native installation/service/window/network action or
publication was performed. The native results above remain attributed to the
maintainer. The new Markdown manual is authoritative; no PDF/HTML was generated.

Only additional native checks after review: on the working disposable Wayland
arrangement, verify regular-file migration, two identical saves, relative latest
link/modes and configured retention; use `-r`'s existing reservation refusal to
exercise the latest reader without launching replacements. Verify one already
missing disposable record's full `GetManaged` history after a broker-only restart.
Reuse these storage/query checks during remaining X11 acceptance; no new native
adapter build, renderer experiment or PKI matrix is needed for these changes.
