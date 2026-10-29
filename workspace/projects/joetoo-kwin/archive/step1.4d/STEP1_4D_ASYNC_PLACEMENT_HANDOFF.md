# Step 1.4d — asynchronous placement confirmation (candidate for review)

Target: JosephBrendler/joetoo-ai, branch `task/joetoo-kwin-step1.4d-multiwindow-validation`, commit `05fac27`.

Scope: The candidate **does not** alter registry correlation's 0.5-second ambiguity quiet period and does not implement production `-o`, `-d`, or `-x`.

## Observed issue

On q552u01 (Wayland) two of four launches reported `ERROR launch` on immediate geometry readback, but the independently observed final geometry of all four was correct. Separately a 900x900 active move was never realized (remained 700x700), so waiting indefinitely or reporting unconditional success would be incorrect.

## Proposed behavior

- Resident applies desktop and geometry, then reports `Complete(request_id, "VERIFY", JSON)` including the KWin UUID of the exact acted-on window, rather than immediately judging a stale geometry readback.
- Broker waits for the existing resident `ObserveWindow` / `SyncInventory` stream. It verifies the observed UUID, desktop membership and all four geometry fields.
- Broker reports `OK` only after the requested result is observed; reports `ERROR` for invalid/deleted targets, mismatched UUID and non-convergence by a 15-second deadline. A pending observation does not imply success.
- Broker correlates a managed launch's separately registered UUID with the placement UUID. It records `pending` then `succeeded` or `failed` in the registry, independent of registration outcome.
- Legacy `Complete(..., "OK"/"ERROR", ...)` remains accepted; in this POC, legacy OK without an explicit UUID is **not** used to assert a managed window's placement success.
- All D-Bus method signatures are unchanged. `VERIFY` is an additive result value within the existing `Complete` protocol.

## Candidate files

- `make_step14d_async_patch.py`: non-mutating patch generator with exact Git blob guards, including embedded tests.
- `tests/test_step1_4d_placement.py` (new): 11 Python tests for delayed success, timeout, unrelated UUID, disappearing target, in-flight serialization, registration before/after placement, failed cross-UUID claim, and legacy behavior.
- `tests/test_step1_4d_placement.js` (new): four Node tests of the resident's `VERIFY` behavior.

Affected source:
- `joetoo-kwin-resident.js` — no immediate geometry-negative acknowledgment.
- `libexec/joetoo-kwind` — event-driven verification and managed placement reporting.
- `libexec/joetoo_kwin_registry.py` — allow an already pending placement to fail even after window disappearance; never declare success while missing.

## Review / headless instructions (no repository writes until applying patch)

From the **joetoo-ai repository root** (not from `workspace/projects/joetoo-kwin`):

```bash
python3 ~/Downloads/make_step14d_async_patch.py > ~/Downloads/step1.4d-async-placement.patch

git apply --check ~/Downloads/step1.4d-async-placement.patch
less ~/Downloads/step1.4d-async-placement.patch

# End of commands
```

Once the candidate diff is approved for local application:

```bash
git apply ~/Downloads/step1.4d-async-placement.patch
cd workspace/projects/joetoo-kwin
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_step1_3a.js tests/test_step1_4d_placement.js
bash -n joetoo-kwin
git diff --check

# End of commands
```

Do **not** commit/push/merge/deploy solely on the basis of this draft. Review and run headless tests first.

The resident JS file is already loaded in KWin. Updating installed disk files and restarting `joetoo-kwind` may **reuse the old running resident**; native validation needs a reviewed script reload or a fresh Plasma/KWin session. No automatic script unload or desktop session restart is performed by this candidate.

## Verification performed here

- Generated patch checked/apply-tested on an **isolated synthetic checkout** (not full commit 05fac27).
- Python syntax compilation of the generated broker, registry and test code passed in that synthetic fixture.
- Four Node tests passed against generated resident function in that synthetic fixture.
- The actual 133+ regression suite and actual Wayland/X11 runs remain for the maintainer's checkout. The generator refuses if actual source hashes no longer match 05fac27.

## Security review remains open

Existing session D-Bus observation and public launch-PID calls are not authenticated as independent, trusted KWin/client provenance. Correlated registration is not yet production authorization to close/delete windows. No `-d` or `-x` behavior is added here.
