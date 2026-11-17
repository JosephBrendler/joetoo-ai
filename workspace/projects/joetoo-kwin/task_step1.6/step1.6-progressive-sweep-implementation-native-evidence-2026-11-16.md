# Step 1.6 — Progressive `-x` correction: implementation review and maintainer-native evidence (2026-11-16)

**Status:** Corrected `-x` **positive path demonstrated natively on `q552u01`**; source/tests reviewed for the approved bounded correction. **Step 1.6 milestone not yet finally accepted**: native failure/refusal, caller-terminal loss, process cleanup and a separately running native X11 compositor remain incompletely tested. No additional coding defect was demonstrated by the submitted evidence.

**Provenance:** Codex's maintainer-supplied review at `/tmp/joetoo-step1.6-progressive-sweep-review.md`, the complete ten-file patch printed from `/tmp/joetoo-step1.6-progressive-sweep.patch`, the user's q552u01 console outputs (including `./tools/restart_joetoo-kwind t`, configured launches and `./joetoo-kwin -x`), and the earlier [Wayland/XWayland evidence](step1.6-native-wayland-evidence-2026-11-16.md). The commands below are **maintainer-executed** except where labeled Codex/headless. This is a curated evidence record, **not** a full raw transcript or a claim of tests executed by a cloud reviewer. The supplied logs remain in the collaboration; no credentials/private session data are reproduced here.

## Objective / baseline

Approved distinctions:

- `-d MANAGED_ID` gracefully closes **one** positively managed window, retaining its registration/reservation and original placement record.
- Confirmed `-x` is a **progressive clean sweep** of the fixed managed snapshot. Already-missing entries retire after fresh authenticated native absence proof; present entries retire as each exact-window graceful close is **verified gone and its helper is reaped**. One failed entry must not undo prior retirements or prevent independently safe work. Source/owner/helper uncertainty is a safety stop for *unsafe subsequent dispatch*.
- A completely resolved sweep leaves **no managed registrations, no reservations** and a genuinely empty `-l` **without broker restart**; operation history remains separately queryable. No forced kill, batch rollback or retargeting; `-D` remains deferred to version 2.

The candidate was produced on branch `task/joetoo-kwin-step1.6-managed-close`, starting/ending local `HEAD f26027a0add26442937c32b92fdc1ef9b54f1de9` according to Codex. It reported **10 tracked files modified, none staged/untracked**; the implementation patch was **not committed or published** at report time. A `git fetch` failed because `.git/FETCH_HEAD` was read-only; that is a **source-sync limitation**, not an application test failure. These exact local changes were supplied as a printed patch, so their source behavior could be reviewed even though the cloud GitHub branch still contains the pre-correction source.

## 1. Scoped code review — what was actually changed

The submitted patch modifies **ten files**, reportedly **+374/−33**:

| File(s) | Relevant change |
| --- | --- |
| `libexec/joetoo_kwin_managed_close.py` | Scope-aware `-x`; classify `retire_missing` versus `close`; recheck native absence after confirmation; retire on verified absence/disappearance; continue safe failures; keep uncertainty guard and result history; truthful aggregate retention flags. |
| `libexec/joetoo_kwin_registry.py` | Guarded `retire_missing` removes the record from both `managed_windows` and `uuid_by_managed_id`; leaves `_next_managed_number` and launch history untouched. |
| `joetoo-kwin` | Clear distinction between retained `-d` and retiring `-x` in help/preview. |
| `tests/test_managed_close.py`, `tests/test_managed_close_cli.py` | Focused confirmation, auth/expiry, all-missing/mixed sweep, recheck failure, known-safe rejection, uncertainty, result and CLI cases. |
| `tests/test_step1_4a_registry.py`, `tests/test_step1_5d_inventory.py`, `tests/test_single_recipe_launch.py` | Two-index retirement guard, monotonic aliases, empty CLI inventory and freed-slot preflight. |
| `ARCHITECTURE.md`, `native/managed-close/README.md` | Narrowly align the existing Step 1.6 `-x` contract; no architecture rewrite. |

No changes were made to the C++ KWin effect, XCB helper, metadata/CMake, RDP/VNC workers or configuration defaults. Existing D-Bus method signatures remain unchanged; per-target result fields (`action`, `retired`, `reason`) are additive under protocol 1.

**Source-grounded checks:** `retire_missing` checks original managed ID, UUID, launch request ID, missing presence, non-pending placement and both indexes *before* removing either index. Bulk `Inspect` revalidates missing UUID after confirmation. Authenticated `closed` plus `gone=true`, after `helper_reaped=true`, retires one target immediately. For `-d`, the established `set_presence(..., 'missing')`/retain path remains intact. A known-safe target rejection continues later targets; owner/helper/source ambiguity preserves the block and previous retirements. The tests explicitly cover these cases. No material code blocker was identified in the submitted diff, but **source review and mocks do not prove every real X11/event-ordering or refusal case**.

**Important interpretation:** `registration_retained=false` and `reservations_retained=false` are documented as flags for **the fixed sweep snapshot**, not a statement about any future windows registered after it. A `partial` result with unresolved records is still legitimate; a sweep of already-missing but positively verified targets is now a success, not a false `partial`.

## 2. Codex headless tests — reported, not rerun by this reviewer

Codex review output (final, after correcting an **intermediate test fixture invocation** involving `-f` with `-h`):

| Check | Final result |
| --- | --- |
| Focused Python | 107 run: **106 PASS, 1 SKIP**, zero failures/errors |
| Full Python | 1,016 run: **1,015 PASS, 1 SKIP**, zero failures/errors |
| JavaScript | **163 PASS**, zero failures/skips |
| Bash syntax, ShellCheck, Python AST, `git diff --check` | PASS |
| Reverse-patch applicability | PASS (per Codex) |

The skipped sandbox check is real kernel credential transport (`SO_PASSCRED`), which that sandbox prohibits; the synthetic credential seam runs the other tests. The initially failed help-test invocation was corrected; an overlapping earlier full run had one failed assertion, but the **fresh final-tree** full run reported zero failures. Neither should be relabeled a production defect.

A representative headless broker/registry plus synthetic adapter/CLI test ended:

```text
state=succeeded
win-002 action=retire_missing state=already_missing retired=true
win-001 action=close state=closed retired=true
registration_retained=false
reservations_retained=false
No managed windows (no retained managed reservations).
```

These results substantiate software control flow but are **not native KWin closure evidence**.

## 3. Maintainer installed the corrected broker and reran regressions

On `q552u01`, the maintainer executed `./tools/restart_joetoo-kwind t`. Its output shows:

```text
Stopping joetoo-kwind service                                      [ ✅ ]
Running ./tools/joetoo-kwind-install-poc --update
Installed twelve user-owned joetoo-kwind files. No service was started.
Update done; result: (success!)                                     [ ✅ ]
Unloading joetoo-bridge KWin script (true)                          [ ✅ ]
Starting joetoo-kwind service                                       [ ✅ ]
Running python unit tests
----------------------------------------------------------------------
Ran 1016 tests in 146.774s

OK
Running javascript unit tests
...
tests 163
pass 163
fail 0
skipped 0
javascript tests done; result: (success!)                           [ ✅ ]
Running ./tools/joetoo-kwind-install-poc --check
Checks done; result: (success!)                                      [ ✅ ]
```

The `OK` output did not report a skip on this maintainer run; do **not** conflate it with the Codex sandbox's 1-SKIP result. The user service restarted as part of this **maintainer-run test**, not as a cleanup step after `-x`. The installer check showed all twelve files current, and the D-Bus introspection listed `PrepareManagedClose`, `CommitManagedClose`, `ManagedCloseStatus`.
The transcript does not include a byte-for-byte hash of the deployed Python files; do not claim the native installation was independently SHA-matched to the attached Codex patch. The installer check and observed runtime behavior are the evidence actually available.

Immediately **after the restart and before new launches**, the broker showed `ListManaged` count 0 and `RegistryStatus managed_count=0`, `viewer_cleanup_uncertain=false`, synchronized observation. This initial zero is a starting-state check, *not* evidence of the later `-x` cleanup.

## 4. New nine-window native test: local launches and fixed set

The maintainer launched and positively registered all nine entries on KWin 6.7.6 Wayland using `-o` configured example plans: **5/5** local KDE/Konsole windows, **2/2** SDL FreeRDP viewer windows, **2/2** TigerVNC/Dolphin windows. Configured stacking/placement was reported successful. As before, RDP authentication and remote VNC usability remained separately **unverified**.

Pre-sweep `./joetoo-kwin -l` contained:

```text
MANAGED_ID  DESKTOP  SLOT  PRESENCE  PLACEMENT  WINDOW_UUID
win-005     2        1     present   succeeded  5a4bf195-b0ee-4753-aef3-2d3085f80b13
win-008     3        1     present   succeeded  628b8d5f-d46c-463a-a146-58ce618c9c00
win-009     3        2     present   succeeded  f43bd205-e915-4962-b481-f1d4d9cfaf6b
win-001     4        1     present   succeeded  8e2b69e8-fe18-4263-b721-8ff79caa909c
win-002     4        2     present   succeeded  ba658a89-b614-4792-9cf2-04a865b7f9b4
win-003     4        3     present   succeeded  ce283657-8194-40a2-8399-457b1266213b
win-004     4        4     present   succeeded  d3dccd28-de90-4cf7-9fe2-9c36eb42d135
win-006     11       1     present   succeeded  00a74bc2-50f4-4fa4-b4da-3023b2bbc446
win-007     11       2     present   succeeded  b36c14c6-a3fb-473b-871e-7556ce2b4e09
```

Before the subsequent sweep, `win-005` was `missing` and was offered as `retire_missing`. The supplied new transcript does **not** include exactly how `win-005` became missing; do not label it a fresh `-d` test merely from that state. Earlier [selective-close evidence](step1.6-native-wayland-evidence-2026-11-16.md) independently establishes unchanged `-d` functionality on the previous candidate.

## 5. Native confirmed `-x`: eight closed + one retired = zero remaining

The maintainer's `./joetoo-kwin -x` output:

```text
Managed clean sweep (confirmed verified removals retire registrations and reserved slots):
  win-005 desktop=2 slot=1 UUID=5a4bf195-b0ee-4753-aef3-2d3085f80b13 action=retire_missing
  win-008 desktop=3 slot=1 UUID=628b8d5f-d46c-463a-a146-58ce618c9c00 action=close
  win-009 desktop=3 slot=2 UUID=f43bd205-e915-4962-b481-f1d4d9cfaf6b action=close
  win-001 desktop=4 slot=1 UUID=8e2b69e8-fe18-4263-b721-8ff79caa909c action=close
  win-002 desktop=4 slot=2 UUID=ba658a89-b614-4792-9cf2-04a865b7f9b4 action=close
  win-003 desktop=4 slot=3 UUID=ce283657-8194-40a2-8399-457b1266213b action=close
  win-004 desktop=4 slot=4 UUID=d3dccd28-de90-4cf7-9fe2-9c36eb42d135 action=close
  win-006 desktop=11 slot=1 UUID=00a74bc2-50f4-4fa4-b4da-3023b2bbc446 action=close
  win-007 desktop=11 slot=2 UUID=b36c14c6-a3fb-473b-871e-7556ce2b4e09 action=close
Retained close result: a5ac9323bd95406290e0ac5fe666b433
Do you want to continue? [Y/n]: y
Affirmative response from user; continuing
```

The retained result identified **zero exclusions**, `state=succeeded`, `reason=verified`, both flags `registration_retained=false` and `reservations_retained=false`, and nine terminal target results:

| ID | Action | Backend reported | Native result | Retired |
| --- | --- | --- | --- | --- |
| `win-005` | `retire_missing` | Not applicable | `already_missing` | `true` |
| `win-008` | `close` | `x11` (local XWayland) | `closed` | `true` |
| `win-009` | `close` | `wayland` | `closed` | `true` |
| `win-001` | `close` | `wayland` | `closed` | `true` |
| `win-002` | `close` | `wayland` | `closed` | `true` |
| `win-003` | `close` | `wayland` | `closed` | `true` |
| `win-004` | `close` | `wayland` | `closed` | `true` |
| `win-006` | `close` | `wayland` | `closed` | `true` |
| `win-007` | `close` | `wayland` | `closed` | `true` |

Representative exact retained-result excerpt:

```json
{
  "excluded": [],
  "protocol": 1,
  "reason": "verified",
  "registration_retained": false,
  "request_id": "a5ac9323bd95406290e0ac5fe666b433",
  "reservations_retained": false,
  "self_terminal": "excluded",
  "state": "succeeded",
  "targets": [
    {"action":"retire_missing","managed_id":"win-005","state":"already_missing","retired":true,"reason":"verified"},
    {"action":"close","managed_id":"win-008","backend":"x11","state":"closed","retired":true,"reason":"verified"},
    {"action":"close","managed_id":"win-009","backend":"wayland","state":"closed","retired":true,"reason":"verified"}
  ]
}
```

The JSON excerpt is intentionally **abridged** (six additional closed targets and per-target desktop/slot/UUID/request ID fields omitted); refer to the original maintainer transcript for the complete result.

**Independent post-transaction CLI check:**

```text
joe@q552u01 ~/joetoo-ai/workspace/projects/joetoo-kwin $ ./joetoo-kwin -l
No managed windows (no retained managed reservations).
```

**This is the previously missing native acceptance proof for the clarified `-x` success path.** It demonstrates 8/8 eligible live windows closed and retired, one preexisting missing record authenticated/retired, no excluded entries, and zero retained managed records/reservations, all **without an intervening broker restart**.

The same local Wayland compositor hosted one XWayland TigerVNC viewer; `backend=x11` is **not** a native `kwin_x11` session. Separate `slim2` X11 acceptance remains outstanding.

## 6. Review judgment: what is fixed, what is not proven

| Acceptance item | Evidence / status |
| --- | --- |
| Exact close with unchanged `-d` semantics | Earlier maintainer-native `-d` passed; new patch leaves path intact, headless regression passed. No post-patch selective native transcript supplied here. |
| Confirmed mixed `-x` with missing and present | **PASS on q552u01**: one `retire_missing`, eight `closed`, nine `retired=true`, empty `-l` without restart. |
| `-x` result/report distinguishes success vs incomplete | **PASS in this successful case** (`succeeded/verified`, no exclusions; retention flags false). Other cases headless-only. |
| Progressive per-target retirement, known-safe failure continuation | Source/tests cover individual retirement and continuation; native positive result covers terminal end state, not independently timestamped intermediate steps or failure continuation. |
| Decline/expired sweep and no side effects | Headless tests; earlier declined selective `-d` passed native. A post-change native declined `-x` transcript not supplied. |
| Unrelated unmanaged window protection | Existing exact-UUID mechanism unchanged; no new controlled before/after unmanaged target evidence in this batch. |
| `ManagedCloseStatus` after initiating CLI has exited | Earlier `-d` status query passed, headless new `-x` tests pass; post-change native `-x` status query not supplied. |
| Close refusal / `not_closed_timeout` with another successful target | Headless cases pass; **not tested natively**. Prior Nano/Kate attempts do not constitute directly managed application refusal. |
| Native helper/source/owner uncertainty | Headless cases pass; no safe live uncertain-path test shown. |
| Managed invocation terminal / CLI loss | Headless behavior and warning policy; no new native test shown. |
| Remote RDP/VNC/SSH process cleanup, tmux persistence | Not independently established by registration, close status or GUI disappearance. |
| Separate native `kwin_x11` compositor / lifetime fence and unsupported `WM_DELETE_WINDOW` | **Outstanding** on `slim2` (optional `gmki91`). |
| Post-sweep freed slot and monotonic managed IDs | Source and headless registry/preflight tests pass; native post-sweep relaunch not shown. |

**No actual new code blocker has been demonstrated.** It is appropriate to review/accept the *bounded `-x` correction* as provisionally validated on q552u01, while reserving **final Step 1.6 milestone acceptance** until the required remaining native tests are performed or explicitly waived by the maintainer. Do not open an additional implementation stage or change native/XCB code solely because such evidence is pending.

## 7. Shortest responsible next actions

1. **Maintainer-native, q552u01:** non-destructively query `ManagedCloseStatus(a5ac9323bd95406290e0ac5fe666b433)` from another terminal, if the same broker instance still runs; run one declined `-x`, verify unchanged inventory and unmanaged peers; launch new disposable managed windows to confirm freed slots and monotonic IDs. No code change implied.
2. **Maintainer-native, q552u01:** exercise a **directly managed** client's refusal/timeout alongside another disposable eligible target and independent RDP/VNC/SSH cleanup as practical. If the existing launcher cannot directly manage a refusing application, record the coverage limitation rather than misclassify a Konsole-hosted Nano/Kate case. Test an invoking managed terminal in a disposable configuration where loss cannot strand important work. Do not bypass the allowlist without a separately justified controlled fixture.
3. **Maintainer-native, slim2:** the separately built native X11 effect and XCB lifetime-fence acceptance, including unsupported `WM_DELETE_WINDOW` and stale/reused XID rejection. Avoid any install/close action on live work; execute only after maintainer review of the native test procedure.
4. **Closeout:** if these remaining checks pass (or the maintainer explicitly accepts documented limits), record final evidence and decide on Step 1.6 acceptance/publication. Codex is **not required** for the already-passing clean-sweep behavior; only dispatch a bounded defect-fix prompt if a **reproducible blocker** is identified.

No publication, remote-branch update, protected-repository operation or native test is authorized by this evidence document alone.
