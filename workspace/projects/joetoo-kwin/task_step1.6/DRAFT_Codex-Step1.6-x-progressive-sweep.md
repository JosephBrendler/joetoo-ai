# DRAFT — Codex implementation task: Step 1.6 `-x` progressive clean sweep

**Draft only: maintainer review/authorization required.** This is a focused correction to the current implementation candidate, not permission to run native tests, publish, start another increment or design a new subsystem.

## Current source and evidence

- Repository `~/joetoo-ai/`; branch `task/joetoo-kwin-step1.6-managed-close`; project `workspace/projects/joetoo-kwin/`.
- Begin by checking actual local branch/HEAD/status. Preserve the **pushed maintainer edits** and any newer local changes. Read applicable AGENTS and `workspace/LOCAL_AGENTS.md`, active `task_step1.6/HANDOFF.md` and `step1.6-native-wayland-evidence-2026-11-16.md`.
- Native KWin plugin is already working on q552u01. Existing `-x` closed **6/6** eligible targets while excluding six already missing records, then retained **all 12** registration/slot reservations; `-l` still showed 12 missing records. The bulk result was `partial` merely because earlier missing records were excluded.
- `libexec/joetoo_kwin_managed_close.py`: `prepare`/`inspect_next` snapshot and classify `targets`/`excluded`; `commit` and `dispatch_next` serialize; `native_result` verifies native disappearance and only calls `registry.set_presence(..., 'missing')`; `report` hardcodes retention booleans and uses excluded count in bulk success test. `libexec/joetoo_kwin_registry.py` holds `managed_windows` and `uuid_by_managed_id`, with no current retire operation. The CLI close preview incorrectly promises all slots retained.

## Accepted contract and required code change

**`-d MANAGED_ID`: unchanged** — exact authenticated graceful close; keep its registered ID/desktop/slot/placement and `presence=missing` when closed. **`-D MANAGED_ID`: version 2, not this task.**

**`-x`:** one confirmed broker-owned **progressive clean sweep** of the fixed registered set:

1. Before confirmation, never mutate any record, reservation, application or native close state. Declined/expired previews remain harmless.
2. Once confirmed, iterate the snapshot. A **positively already-missing** record should immediately lose its registration and desktop/slot reservation; no redundant close dispatch. A **positively present** eligible target uses the existing exact-UUID, owner-checked native graceful-only close; on verified `state=closed` **and** `gone=true`, immediately retire that one record and reservation. Do not wait for other windows or use all-or-nothing rollback.
3. A deterministic refused/not-closed/unsupported/identity-lost target is **not** claimed closed. Retain only the minimal safety-critical unresolved record, report a precise reason and continue independently safe targets when there is no native dispatch/ownership hazard. One failed window must not prevent retiring verified successes or unrelated already-missing records.
4. A genuinely uncertain native helper, owner or observation source may prohibit subsequent **unsafe native close dispatch**. Preserve the minimal safety guard for manual resolution; report it as unresolved. Never erase evidence or claim verified closure. Prior safe retirements remain retired. Do not manufacture a recovery mechanism or force-kill anything.
5. On fully verified completion, `./joetoo-kwin -l` must say `No managed windows (no retained managed reservations).` Do **not** restart the broker. Preserve any separate future last-good snapshot and unrelated unmanaged windows.
6. Implement one small, guarded retirement operation in the existing registry model as needed, updating `managed_windows` and `uuid_by_managed_id` consistently. Never recycle managed aliases within the broker lifetime; preserve bounded operation history separately. Keep fixed snapshot, safe broker serialization, authentic caller/native UUID and confirmation rules.
7. `ManagedCloseStatus` must remain queryable after CLI loss and truthfully distinguish closed+retired, already-missing+retired, failed/unresolved/skipped and overall completion. Do not report fixed `registration_retained=true`, `reservations_retained=true` for successful `-x`. Prefer the smallest compatible response change, without broad new APIs. `-x` preview must correctly describe retiring managed registrations; `-d` retains its old wording and behavior.

**Scope:** work only in existing broker/registry/CLI and focused tests. Preserve native C++ adapter/XCB helper, RDP/VNC launch/cleanup paths, Konsole/SSH, configuration defaults, unrelated KWin logic, Step 1.7/1.8, and all version 2 features. No force kill, new framework, dependency or programming language.

## Required headless regression evidence

Cover: `-x` decline/expiry leaves all records intact; confirmed all-missing sweep empties registry and reports success; mixed present/missing clears each as independently verified; known-safe failure permits later independent successes but retains minimal unresolved state; genuine native cleanup uncertainty never authorizes later unsafe dispatch; previous retirements are not undone; original `-d` retention passes; `-l`/future `-L` sees released slots and monotonic managed IDs; no wrong/unmanaged window close; broker/CLI loss and close-status retention; self-terminal behavior unchanged. Run relevant existing managed-close, registry/inventory and full Python/JS/shell regressions. Record exact counts and skips; do not conflate prior native tests with new code.

After the correction, make only the **needed wording** consistency amendments to `ARCHITECTURE.md` and `native/managed-close/README.md`, which presently describe retained `-x` records. Don't overwrite the maintainer's native evidence with simulated results or prolong documentation work unnecessarily.

## Deliver and stop

Return changed paths, concise diff/behavior explanation, exact test commands and results, output example showing `-x` leaves empty `-l`, limitations and remaining maintainer-native checks. No native install/load/close, OpenRC restart, commit, push, PR, merge or later work without explicit maintainer authorization. **Stop after one implementation and reviewable tests.**

**Expected local Codex cost: MODERATE** (registry/result-lifecycle changes and regression testing); no new native work is in scope. Cloud ChatGPT has already performed the source review and documentation drafting.
