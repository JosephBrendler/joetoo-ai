## Summary

Step 1.3b adds a read-only diagnostic launch-to-KWin-window correlation probe in two increments:

- **1.3b.1:** `BeginCorrelation`, `SetCorrelationPid`, and `PollCorrelation` snapshot the observed window inventory before a launch, record the launching shell's child PID, and report a unique new KWin UUID only when exact-PID evidence survives a settling interval. Preexisting windows, ambiguous matches, timeouts, and KWin resident source changes fail conservatively.
- **1.3b.2:** Correlation responses include newly observed class-matching candidates (`window_uuid`, KWin PID, lifecycle `event_id`, `currently_observed`, and diagnostic evidence) and `candidate_history_complete`. Class/title-only evidence is never promoted to `MATCHED`. Eviction of bounded lifecycle history prevents claiming a uniquely proven single PID match.

Also adds the diagnostic Bash launcher, regression tests, probe notes, and Python bytecode cache ignores. Existing D-Bus move/launch methods and KWin resident JavaScript are unchanged.

**This PR does not implement a managed-window registry, ownership adoption, placement changes, or safe-close operations.** Chrome windows delegated to an already-running browser session deliberately remain `TIMEOUT`, with candidate diagnostics only.

## Validation

Maintainer-native tests on Gentoo/OpenRC KDE Plasma 6.7.5:

| Launch | gmki91 / KWin X11 | q552u01 / KWin Wayland |
| --- | --- | --- |
| `konsole --separate` | exact PID `MATCHED` | exact PID `MATCHED` |
| `dolphin --new-window` | exact PID `MATCHED` | exact PID `MATCHED` |
| Chrome `--new-window` with existing profile | `TIMEOUT`; new class candidate under existing browser PID | `TIMEOUT`; new class candidate under existing browser PID |
| Chrome with unique `--user-data-dir` | exact PID `MATCHED` | exact PID `MATCHED` |

On **both** hosts: **74 Python tests passed, four JavaScript tests passed**, Bash syntax passed, `git diff --check` passed, and the installed broker was verified byte-for-byte against the source after the POC user-service update. Existing applications survived broker restarts in earlier lifecycle validation.

## Boundaries and follow-up

- This is a **diagnostic** PID/UUID result, not a production-grade ownership proof. Class-only and title-hint candidates are observational, not causation evidence.
- Browser profile isolation is an application-specific workaround to encourage PID correspondence, not a general solution to process delegation; temporary profile lifecycle management remains separate.
- Near-simultaneous delegated windows, bounded event-history loss, and application launches that fork or delegate require stronger transaction identity before any managed-window ownership or close operation.
- No protected `joetoo` / `joetoo-upstream` repository changes are included.
