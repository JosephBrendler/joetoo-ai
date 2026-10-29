# joetoo-kwin Step 1.4d — candidate review and native validation (proposed handoff)

**Status:** review candidate; not a publication approval. Prepared 2026-10-28.

**Repository:** `JosephBrendler/joetoo-ai`  
**Task branch:** `task/joetoo-kwin-step1.4d-multiwindow-validation`  
**Published base:** `05fac27`  
**Local candidate:** uncommitted on both `gmki91` and `q552u01` (per maintainer logs).

## Problem and scope

The old placement callback assessed KWin window geometry immediately after setting it. On Wayland two of four newly launched Konsole windows reported ERROR despite reaching the correct final desktop/geometry. This is different from genuinely non-converging geometry (an attempted 900×900 resize remained 700×700).

Candidate limits itself to asynchronous placement confirmation and independently tracked placement status, preserving positive PID/UUID correlation and its 0.5-second quiet period. It does not implement configured `-o`, destructive `-d`/`-x`, persistence or production launch authorization.

## Files and source inspection

The change proposal is reproducible from `make_step14d_async_patch.py` (source-hash guarded to `05fac27`) and affects exactly five files:

- `joetoo-kwin-resident.js`: after applying desktop/geometry, emits `Complete(..., 'VERIFY', ...)` containing the target KWin UUID and diagnostics rather than treating immediate mismatch as terminal failure.
- `libexec/joetoo-kwind`: verifies the exact UUID's desired desktop and frame through synchronized `ObserveWindow` / `SyncInventory` data, bounds non-convergence at 15 seconds, serializes verification, and associates placement results with a positively registered managed UUID.
- `libexec/joetoo_kwin_registry.py`: permits pending placement to fail after window disappearance while prohibiting success for a non-present window.
- `tests/test_step1_4d_placement.py` (new): 11 headless Python tests of deferred confirmation, timeout, cross-UUID safety, registration/placement ordering, disappearance, compatibility and invalid input.
- `tests/test_step1_4d_placement.js` (new): four Node.js tests of the resident's VERIFY signaling and immediate error boundaries.

The reviewed artifact here is the **patch generator** plus inspected published baseline and user-reported native/headless logs; we have **not** directly retrieved and compared the two machines' uncommitted five-file blobs. Check their staged trees/hashes before publication.

## Maintainer-performed validation evidence

| Check | gmki91 — Plasma X11 | q552u01 — Plasma Wayland |
| --- | --- | --- |
| Python suite | 144 tests pass | 144 tests pass |
| Node.js suite | 8 pass | 8 pass |
| Syntax / whitespace | Bash and JS checks pass; `git diff --check` clean | Bash and JS checks pass; `git diff --check` clean |
| Resident update/reload | Installed, unloaded old resident, reloaded and synchronized | Installed, unloaded old resident, reloaded and synchronized |
| Managed registrations | 4/4 | 4/4 |
| Confirmed placement | 4/4 `OK`, correct geometry | 4/4 `OK`, correct geometry; previously 2 false errors |
| Managed placement state | all `succeeded` | all `succeeded` |
| Baseline UUID exclusion | no overlaps | no overlaps |
| Close lifecycle | win-004 `missing`, registry retained | win-004 `missing`, registry retained |

Other maintainer lint checks: `validate_scripts joetoo-kwin -l`, `validate_scripts tools/ -l`, and `validate_scripts tests/ -l` passed for recognized shebang scripts on gmki91; scripts and bytecode skipped for unrecognized/no shebang should not be counted as lint passes.

## Review findings and remaining risks

1. **Positive finding:** source preserves separation of registration, placement and presence. Reporting `VERIFYING` pending through `Status` avoids premature Wayland false negatives. No D-Bus signature change, and legacy `OK`/`ERROR` completion remains supported.
2. **Boundary remains:** `Complete`, `ObserveWindow`, `SyncInventory` and launch/PID handoff presently lack strong sender/provenance authentication. Current success must not authorize arbitrary future close/delete operations. Security review is an explicit later gate.
3. **Native failure-path gap:** a truly non-converging 900×900 attempt was observed *before* this candidate. Headless tests cover non-convergence and deadline but the updated native path has not yet been exercised against that case. Recommend an optional controlled negative native check if failure classification must be acceptance evidence.
4. **Deadline nuance:** broker measures verification deadline relative to request creation; if confirmation starts late, the remaining window may be less than 15 seconds. This is a reviewable implementation policy; clarify if a fresh 15-second settling interval after `VERIFY` is intended. The current code evaluates exact matched geometry before checking elapsed timeout, so a late observed match can still produce success.
5. **Payload/observation trust:** `VERIFY` detail is parsed without a separate upfront payload-size limit. Existing D-Bus authentication boundary reduces confidence in treating these messages as durable authorization. Consider input-size bounds and more explicit source/revision tests in a security-focused follow-up.
6. **Test fixture scope:** JS tests exercise a source-extracted placement function with stubs, not a live KWin compositor; the two native runs provide the independent KWin evidence.
7. **Diff gate:** `git diff --check` excludes new/untracked test files. Before committing, explicitly stage the intended five files, inspect `git diff --cached --stat`, `git diff --cached`, and run `git diff --cached --check`.

## Recommended next gate

Given the positive two-backend native evidence, the candidate is appropriate for **maintainer review of the complete five-file diff**. Record the outstanding risks above and decide whether to address deadline/payload concerns in this task or defer explicitly. Do not commit, push or open a PR without the maintainer's next authorization. Do not touch official `joetoo` or `joetoo-upstream` repositories.

## Proposed commands (review only)

From the project directory on each machine:

```bash
git status --short
git diff --stat
git diff -- joetoo-kwin-resident.js libexec/joetoo-kwind libexec/joetoo_kwin_registry.py
sha256sum joetoo-kwin-resident.js libexec/joetoo-kwind libexec/joetoo_kwin_registry.py tests/test_step1_4d_placement.py tests/test_step1_4d_placement.js

# End of commands
```
