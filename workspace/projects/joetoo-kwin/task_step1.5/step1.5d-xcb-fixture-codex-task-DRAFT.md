# Codex task — Step 1.5d accepted; one isolated XCB fixture stabilization before publication

**Read first:** `workspace/projects/joetoo-kwin/AGENTS.md`, parent/repository AGENTS instructions, `task_step1.5/HANDOFF.md`, `task_step1.5/README.md`, and `task_step1.5/step1.5d-native-acceptance-2026-11-12.md`. Confirm the actual branch, HEAD and dirty/clean status; do not overwrite the maintainer's local edits.

**Repository:** `JosephBrendler/joetoo-ai`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Existing task branch:** `task/joetoo-kwin-step1.5d-integrated-regression`

## Decision / scope

**Step 1.5d is functionally ACCEPTED by the maintainer (2026-11-12).** Do **not** reopen or expand `-L`, `-l`, initial layout, stacking, existing `-o`, remote security or production libxcb semantics. This assignment is one focused *test-only fixture* hardening and regression/evidence round before separately approved commit/push, PR and merge.

The maintainer demonstrated native X11 `gmki91`, native Wayland `iota01` (1920x1080 and 1024x600 configured geometry), and a second Konsole on the same Wayland desktop raised above the preexisting one. `-L`/`-l` are accepted. One full `iota01` run reported 949 Python tests with one failure and 163/163 JavaScript PASS. The isolated failing Python test was then rerun **11 consecutive times**, all PASS. Full transcript excerpts and uncertainty are documented in the acceptance evidence.

## Precisely targeted issue

```
FAIL: test_real_libxcb_receives_isolated_server_event
  (test_vnc_identity.IdentityPrototypeTests.test_real_libxcb_receives_isolated_server_event)
AssertionError: Lists differ: [] != [('desktop', 123)]
```

`tests/test_vnc_identity.py` starts a Python socketpair-based fake X11 server thread, which sends an actual 32-byte wire `ClientMessage` as part of the synthetic protocol. After constructing `NativeObserver` using the socketpair proxy, the fixture immediately calls `observer.drain(16)`. The **production** `NativeObserver.drain` intentionally uses nonblocking `xcb_poll_for_event()` and may legitimately return `[]` if the fake server's event has not been processed/received yet. This is a **likely scheduling/synchronization race, not yet proven**. `LC_CTYPE` changes have not been demonstrated as causal.

## Requested investigation / implementation

1. Inspect the full exact test and its peer protocol. Confirm the race or another precise cause with a focused, source-grounded explanation. Do not merely infer from a single failing assertion.
2. Improve **the isolated fixture's synchronization** to guarantee a bounded opportunity for the event to become *available to the tested libxcb poll*, not merely that the fake server has called `write`. A sender-side acknowledgement alone is insufficient if the receiving side has not yet consumed the wire event. Prefer an explicit bounded readiness protocol (e.g. `select`/`poll` on the observer's XCB fd plus appropriate XCB processing) or another correct deterministic fixture handshake. Explain why the chosen wait guarantees the subsequent actual-native-ABI assertion is meaningful. Avoid arbitrary sleeps, indefinite waits, and retry loops that erase genuine assertion failures.
3. Keep an explicit deadline and a useful timeout/peer-error diagnostic, ensure no goroutine/thread/socket/file descriptor leak, and preserve the assertion of the actual decoded event `('desktop', 123)`, the expected mask, and no unexpected fake-server errors. Keep the fixture fully offline: no actual X server, DISPLAY, KWin, GUI or remote endpoint.
4. **Do not modify production** `libexec/joetoo_kwin_vnc_identity.py` nonblocking `drain`, event budget, source/owner gates, observer teardown, or other operational code unless you first show an independently demonstrated production defect and request explicit maintainer authorization. Do not suppress, skip, xfail or relax the test.
5. Add focused tests only if useful for the race and its bounded failure behavior. Preserve test runtime/cleanup budgets.

## Evidence and verification

- Reproduce or stress-test the exact isolated fixture appropriately. Record repeat counts and failures honestly; do not claim that a race was deterministically reproduced if not.
- Run the applicable focused Python tests, complete Python discovery and complete JavaScript suite against the exact patched working tree. Report exact PASS/FAIL/SKIP/ERROR totals and command lines. Perform applicable Bash/Python syntax, ShellCheck, and `git diff --check` where relevant.
- Explain briefly why the fixture modification cannot alter accepted `-L`/`-l` behavior and why production's nonblocking behavior was preserved.
- Supply a concise proposed addendum to `task_step1.5/step1.5d-native-acceptance-2026-11-12.md` with new focused/full-suite evidence and tested SHA or working-tree status. Do not rewrite away the historical 948/949 run or the eleven passing reruns.
- Supply an exact changed-file inventory and patch for maintainer review.

## Authority / stop condition

Work inside `joetoo-ai` only, respecting repository AGENTS/scope. No change to `joetoo` or `joetoo-upstream`. Do not install/restart services, alter real host locale, launch windows, exercise real RDP/VNC/SSH connections, or run native X11/Wayland activities.

**Do not commit, push, open a PR, or merge** under this assignment. Stop after the patch, tests and proposed evidence addendum. The maintainer will review and explicitly authorize publication steps separately.
