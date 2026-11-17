# Step 1.6 — Managed operations HANDOFF

**Status (2026-11-16): Step 1.6 implementation candidate — shared authenticated graceful close, `-d` and broker-owned `-x`; headless validation complete, native acceptance/publication reserved.**

## 1. Task identity and authority

**Repository:** `JosephBrendler/joetoo-ai`\
**Project:** `workspace/projects/joetoo-kwin/`\
**Implementation branch:** `task/joetoo-kwin-step1.6-managed-close`\
**Reviewed base:** `cdcdc9e8c842d0be04447c06b90a25d3cc59f107` (PR #31 merged)\
**Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)\
**Task index:** [README.md](README.md)

Step 1.6 is the active development milestone. This HANDOFF records the current assignment and authorization boundaries; it does not independently grant permission. Neither the architecture roadmap nor historical task instructions authorize implementation, native operations or publication.

## 2. Accepted predecessor

Step 1.5 is complete.

- Step 1.5c.5d accepted and merged through [PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29) at `3e9c4bf311bc65b32d332a00d3b50163a9043303`.
- Step 1.5d accepted and merged through [PR #30](https://github.com/JosephBrendler/joetoo-ai/pull/30) at `f72407278fa0a9c923079f3b38ce834440d2fef2`.
- Accepted behavior includes configured managed launches, exact-UUID registration and placement, remote access integration, single-window `-L` launch, read-only `-l` inventory, and verified one-shot raising of newly launched managed windows.
- Final XCB test-fixture correction and regression evidence are preserved in the [native acceptance record](../archive/task_step1.5/step1.5d-native-acceptance-2026-11-12.md) and [fixture addendum](../archive/task_step1.5/step1.5d-xcb-evidence-addendum.md): 7 focused Python, 1,000/1,000 stress repetitions, 100 additional leak-check repetitions, 949 full Python and 163 JavaScript passes. These recorded results were not rerun during this documentation task; the original 948/949 result and eleven passing reruns remain intact.

Historical records: [archived Step 1.5 README](../archive/task_step1.5/README.md) and [closed HANDOFF](../archive/task_step1.5/HANDOFF.md).

These completed milestones are accepted foundations, not outstanding work.

## 3. Documentation transition (completed)

PR #31 merged the archive/init transition at `cdcdc9e`. All 213 tracked Step 1.5
artifacts and modes were preserved; no runtime behavior changed. Historical
transition validation and publication checkpoints remain in the
[initial HANDOFF](step1.6_initial_historical_HANDOFF.md) and PR #31.

The read-only source review and final contract design are complete. The
maintainer authorized both close commands and the minimal native adapter.
Current candidate changes remain uncommitted; native operations and publication
are separately reserved. The four pre-existing maintainer documentation edits
were preserved when preparing this implementation.

## 4. Step 1.6 objective

The intended milestone is safe management of existing and newly added managed windows through:

- `-d MANAGED_ID` — selective graceful close.
- `-x` — graceful closure of positively identified managed windows.

Approved scope: explicit confirmation; exact authenticated native UUID/owner
proof; ordinary graceful close only; fixed bulk snapshot, serialized by the
broker; retained per-target results after CLI exit. Missing/uncertain targets
are excluded and remain reserved. No `-a`, `-D`, `-S`, `-r`, retirement or restore.

Implementation: three additive broker methods (`PrepareManagedClose`,
`CommitManagedClose`, `ManagedCloseStatus`), one import-safe close module and
private frontend pipe, plus the exact-version native effect/XCB helper.
Legacy observation traffic cannot authorize close or prove completion.
See [adapter build, safety contract and native matrix](../native/managed-close/README.md).

## 5. Invariants and exclusions

Preserve exact managed UUID identity, source and ownership validation, retained missing reservations, existing broker protections and isolation of unrelated windows.

Never close or adopt a window using class, title or PID alone, or substitute an observed UUID for the managed identity.

Keep separately scoped outcomes distinct: window placement, managed-window lifecycle, RDP/VNC connection state, and independent broker/service lifetime.

Step 1.7 runtime checkpoint/restart reconciliation, Step 1.8 durable last-good layout/restore, Step 1.9 packaging, and unrelated architectural redesign remain outside this task.

## 6. Development and native testing hosts

- **q552u01:** Primary development host, native KWin Wayland; first planned native testing.
- **slim2:** Subsequent native X11 testing.
- **gmki91:** Additional X11 development and testing when available.

Host assignments do not themselves authorize native test execution, service changes or destructive operations.

## 7. Next actor and authorization

**Next actor:** maintainer, reviewing the integrated uncommitted candidate and
headless evidence. Publication and native install/load/destructive testing
require explicit authorization. Codex must not begin later milestones.

Native acceptance order: q552u01 Wayland, slim2 X11, then gmki91 if needed.
Include close refusal, exact identity, XID reuse/unsupported-protocol rejection,
CLI loss during bulk close, retained reservations and ordinary Konsole/SSH
termination with independent remote tmux persistence. No such test has run here.

## 8. Recent decisions
- there will be no `-a` (add window) requirement - this is satisfied already by `-L`
- I have removed references to `-a` where I could find them, any others should be taken only as historical reference to something once considered.

## 9. Latest candidate result

999 Python tests: 998 PASS / 1 SKIP; 163 JavaScript PASS. The 107-test focused
set has 106 PASS / the same SKIP. Both KWin 6.7.6 native variants compile;
Bash/Python syntax, ShellCheck and diff checks pass. The skip is the sandbox's
SO_PASSCRED prohibition: wire tests use an explicit credential double here.
No native loading/closure is claimed. Exact commands and limitations are in the
[task README](README.md) and [adapter notes](../native/managed-close/README.md).
Concurrent maintainer edits to workspace instructions/role documents were left
untouched and are separate from this project candidate.

## 10. Next decision

Review the candidate diff and headless evidence; separately authorize publication
and the native acceptance procedure. Step 1.6 is not yet accepted.

Historical evidence and earlier draft instructions must not override this HANDOFF or subsequent explicit maintainer decisions.
