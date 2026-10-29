# Step 1.4 — completed milestone handoff

**Status:** COMPLETE in the `joetoo-ai` collaboration repository; historical closure record, not an active authorization.  
**Maintainer acceptance/publication evidence:** PRs [#19](https://github.com/JosephBrendler/joetoo-ai/pull/19), [#20](https://github.com/JosephBrendler/joetoo-ai/pull/20), [#21](https://github.com/JosephBrendler/joetoo-ai/pull/21), and [#22](https://github.com/JosephBrendler/joetoo-ai/pull/22).  
**PR #22 merge commit:** `6e3196cff9e3ce7124102514646d44abbf9f1643` (October 28, 2026).  
**Intended location:** `workspace/projects/joetoo-kwin/task_step1.4/HANDOFF.md`.  
**Provenance:** Drafted from published project architecture, merged PR metadata and the maintainer's reported `gmki91`/`q552u01` validation logs. This file itself was not part of PR #22.

## 1. Objective and delivered scope

Complete the initial in-memory managed-window model, broker-private correlation and registration, UUID-based observation reconciliation, read-only management queries, and integration of several distinct managed windows with asynchronously confirmed placement on both KWin backends.

| Gate | Delivered capability | Review reference |
| --- | --- | --- |
| 1.4a | Registry identities, independent state dimensions, contract tests | PR #19 |
| 1.4b | Broker-private registration, multiple records and conservative per-UUID reconciliation | PR #20 |
| 1.4c | Read-only `ListManaged`, `GetManaged`, `RegistryStatus` | PR #21 |
| 1.4d | Managed four-window launch, bounded asynchronous placement confirmation, registry placement outcome and native dual-backend validation | PR #22 |

The active implementation lives in the project root (`joetoo-kwin`, `joetoo-kwin-resident.js`, `libexec/`, `tests/`, etc.), not this historical task folder. The `archive/` directory contains older POC implementations. This handoff is not a replacement for `ARCHITECTURE.md`.

## 2. Verified validation evidence

Maintainer-reported results from October 28, 2026:

| Test | `gmki91` Plasma X11 | `q552u01` Plasma Wayland |
| --- | --- | --- |
| Python `unittest` | 144 passing | 144 passing |
| Node resident JavaScript tests | 8 passing | 8 passing |
| Four new managed Konsole registrations | 4/4 | 4/4 |
| Placement confirmations | 4/4 `succeeded` | 4/4 `succeeded` |
| Observed desktop/geometry | exact requested values | exact requested values |
| No adoption of preexisting UUIDs | confirmed | confirmed |
| Close `win-004` manually | 3 present, 1 missing; prior placement retained | same |

Fixture geometry at 1920×1080: desktops 1 and 2; top-left positions `(19,54)` and `(873,54)`; window size `816×918`. This is a **test fixture**, not a universal multi-monitor geometry contract.

User service stop/update/start and resident unload/reload were performed on both machines. The output demonstrated a synchronized observed inventory after broker startup. The corrected Wayland protocol no longer reported premature placement errors in the four-window test.

Evidence boundary: tests and native execution were **performed/reported by the maintainer**; this handoff does not claim independent AI execution. Headless tests exercised the stale-geometry timeout and exact-UUID safeguards, but a deliberately nonconverging *native* placement was not separately demonstrated.

## 3. Accepted behavior to carry forward

- Observation is not ownership. A managed window requires positive correlation to an authorized launch and exact KWin UUID association.
- A PID may be shared by more than one top-level window; do not use PID/class/title alone to authorize destructive actions.
- Registration, placement, presence and application/SSH connection states remain distinct.
- KWin resident requests placement; broker confirms convergence from window observations; stale immediate geometry is not itself a failure.
- `joetoo-kwind` lifecycle does not own or terminate client Konsole/SSH processes.
- Preexisting observed windows are not implicitly registered when the broker restarts or synchronizes inventory.

## 4. Deferred and explicitly out of scope

- Step **1.5**: generalized geometry policy, `mw l/r`, colored configuration dry-run `-c`, `-o` planned layouts with SSH placeholders, and `-v/-q`.
- Step **1.6**: managed `-a`, `-d`, `-x`; authorization and identity safety must be reviewed **before enabling destructive actions**.
- Steps **1.7–1.9**: private checkpoint/reconciliation, durable restore configuration and packaging/full regression.
- Current placement timeout starts at operation/request creation; it can be revisited when there is evidence of a problem, with Phase 2 optimization otherwise preferred.
- Bounded input validation of `VERIFY` JSON and session D-Bus sender/authorization hardening remain review items; do not treat Step 1.4d's successful native tests as validation of a future destructive API.

## 5. Source and artifact provenance

- Current accepted implementation: merged `joetoo-ai/main`, PRs #19–#22.
- Legacy POCs and plan/SSH prototypes: `archive/README.md`.
- AI-generated review ZIPs, patch builders, handoffs and test guides are **development artifacts**, not canonical source. Some older artifacts were never committed. Retain recovered originals with a manifest marking superseded patches; don't replay them against merged `main`.
- [Project README](../README.md) provides the short current-status summary. [Architecture](../ARCHITECTURE.md) governs design and milestone acceptance.

## 6. Closure and next actor

**Milestone:** closed by maintainer's PR #22 merge. No outstanding Step 1.4 implementation authorization is implied.  
**Next proposed milestone:** Step 1.5; see `../task_step1.5/HANDOFF.md`.  
**Maintainer decision needed:** review and approve Step 1.5 scope and permissible actions before implementation starts.
