# Step 1.7 — Combined recovery and last-good snapshot

> **Archive closure (2026-11-19): FORMALLY ACCEPTED AND MERGED.**
> The combined Step 1.7 (former Steps 1.7 and 1.8) implementation, native
> Wayland (`q552u01`) and X11 (`slim2`) evidence, and formal acceptance were
> merged via [PR #33](https://github.com/JosephBrendler/joetoo-ai/pull/33)
> to `main` at `df118da`; the task branch was deleted. See the
> [merge closure record](step1.7-pr33-merge-closure-2026-11-19.md),
> [formal acceptance](step1.7-maintainer-acceptance-2026-11-19.md), and
> [archived HANDOFF](HANDOFF.md). The active task is
> [Step 1.9 packaging](../../task_1.9/HANDOFF.md).

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

- [Accepted architecture §8](../../ARCHITECTURE.md#8-recovery-and-restorable-layout-combined-version-1-step-17).
- [Step 1.6 archived HANDOFF](../task_step1.6/HANDOFF.md) and
  [accepted task index](../task_step1.6/README.md).
- [Native X11 predecessor evidence](../task_step1.6/step1.6-slim2-native-x11-evidence-2026-11-18.md).
- [Wayland/XWayland predecessor evidence](../task_step1.6/step1.6-progressive-sweep-implementation-native-evidence-2026-11-16.md).
- [Project README](../../README.md), [project instructions](../../AGENTS.md).

**Previous milestone:** Step 1.6 accepted and merged through
[PR #32](https://github.com/JosephBrendler/joetoo-ai/pull/32)
(`a6999e2`). No additional Step 1.6 tests or implementation are prerequisites
for starting the next *authorized* work. Step 1.9 packaging follows this
version 1 objective; [Version 2](../../ARCHITECTURE.md#12-version-2-considerations)
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

### Maintainer-native acceptance plan (historical; executed 2026-11-19)

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
- [The user manual](../../docs/joetoo-kwin_user_manual.md): all implemented CLI
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

The narrowly scoped native checks listed above were pending when the refinement
candidate was written. They were subsequently executed by the maintainer;
see the evidence and disposition below.

## Native validation and acceptance review — 2026-11-19

**Status: ready for maintainer acceptance decision, NOT yet accepted or merged.**
Maintainer committed and pushed the exact refined 25-file candidate as
`33bbbee03a5effbf1c4c31b5600254ab28374510` on
`task/joetoo-kwin-step1.7-recovery-snapshot`; the `slim2` checkout matched
`origin` at that commit with a clean worktree. This is a task-branch candidate,
not a merge to `main`. Native tests below were run by the maintainer.

### Evidence with complete terminal logs (trailing whitespace normalized)

- [q552u01 native Wayland and snapshot refinement](step1.7-q552u01-native-evidence-2026-11-19.md):
  [initial native-context 47-test console](step1.7-q552u01-initial-native-focused-console-2026-11-19.txt),
  [full native console](step1.7-q552u01-refined-native-console-2026-11-19.txt),
  [full focused/headless console](step1.7-q552u01-refined-headless-console-2026-11-19.txt).
- [slim2 native X11 recovery and restore](step1.7-slim2-native-x11-evidence-2026-11-19.md):
  [initial baseline/launch console](step1.7-slim2-initial-native-console-2026-11-19.txt),
  [complete X11 snapshot/restart/close/restore console](step1.7-slim2-recovery-native-console-2026-11-19.txt).

### Observed outcomes

| Capability | q552u01 Wayland | slim2 X11 |
| --- | --- | --- |
| Native managed launch | Three of three restored from legacy snapshot | Two of two on desktop 3, duplicate-slot refusal |
| Broker-only restart | Original IDs/UUIDs and missing history retained; recovery ready | IDs, UUIDs, reservations and KWin owner unchanged; 2 present, recovery ready |
| Snapshot save | Complete `-S`, protocol 2, shared 47 settings; regular legacy file migrated byte-identically | Three distinct saves, protocol 2, two recipes, 47 settings |
| History and private files | Relative latest link, `0700` directory, `0600` files, depth 2 | Relative latest link, `0700` directory, `0600` files, depth 2 |
| Native single close and missing record | `-d` retained missing identity and full last-known observation after broker restart (`diff` status 0) | Verified native X11 `-d`, missing record and observation survived broker restart |
| Fail-closed snapshot | Missing record refused; preserved legacy file, then later latest symlink and complete history | Missing record refused; preserved latest symlink |
| Progressive close and restore | `-x` retired missing/live records; legacy `-r` launched three new UUIDs; occupied-slot `-r` refused | `-x` retired missing/live records; confirmed `-r` launched two new UUIDs |

**Regression/static validation on q552u01:** 79 focused Python PASS; full
Python 1080 PASS (no skip on this native host); JavaScript 163 PASS. Four
scripts passed *separate* `validate_scripts` runs. The earlier **combined**
ShellCheck command printed `Killed`, so it is not called a combined PASS; its
cause remains undetermined, with no OOM evidence in the shown `dmesg` excerpt.
Existing earlier candidate/sandbox results remain documented above and are
not conflated with these host-run results.

**Remaining qualifications (no demonstrated source-code blocker):** the
refined X11 console demonstrates confirmed `-r`, but not a declined `-r` (the
maintainer had reported a declined Wayland case with the prior candidate).
Native-effect owner/method introspection was not independently completed on
this X11 run; a verified X11 close did succeed. The restart helper sometimes
queried D-Bus before registration completed, while later bounded polling
succeeded; this is a startup-readiness UX item, not an observed lasting failure.
No reboot/new-KWin-session adoption is claimed. Historical geometry is only
informational and is never restored as live placement or close authority.

**Formal maintainer acceptance — 2026-11-19:** Step 1.7 is **ACCEPTED**.
The maintainer made that decision after the evidence above, including both
native backends, complete-snapshot refusal and fresh-instance restore. The
small coverage qualifications described above are recorded without reopening
acceptance. See the [acceptance record and verbatim q552u01 fast-forward
output](step1.7-maintainer-acceptance-2026-11-19.md).

The implementation commit is `33bbbee`; the subsequent nine-file evidence
update reached task-branch commit `2985113` (`git pull --ff-only` on `q552u01`).
Acceptance and merge were separate maintainer actions: both are now complete.
The final [PR #33 merge record](step1.7-pr33-merge-closure-2026-11-19.md)
confirms `main` at `df118da` and the deleted task branch. Project status and
architecture language were reconciled in the documentation-only Step 1.7
closure/Step 1.9 kickoff transition. Packaging proceeds under the distinct
[Step 1.9 active HANDOFF](../../task_1.9/HANDOFF.md); Version 2 remains deferred.
