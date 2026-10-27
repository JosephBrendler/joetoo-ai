# Step 1.3b.1 — diagnostic launch correlation (review candidate)

The aim is to determine which observed KWin UUID belongs to a particular
program launch, regardless of whether it opens a Konsole, another local GUI,
or a local terminal for SSH/VNC. The target host, if any, is not itself a KWin
window identity. This increment is read-only and **does not** grant managed
ownership, request placement or change the legacy `test-launch` contract.

## Proposed native experiments (ordinary Plasma user, X11 and Wayland)

Run the Python and JS regression tests before replacing the POC broker. The
updated broker adds `BeginCorrelation`, `SetCorrelationPid`, and
`PollCorrelation`, each on `org.joetoo.KWinBridge`. The resident JS does not
need replacement in this increment because Steps 1.3a–1.3a.2 already report
window UUIDs, PIDs, titles, and lifecycle changes.

For a disposable new Konsole, while the updated broker is running:

```bash
cd ~/joetoo-ai/workspace/projects/joetoo-kwin
bash tools/joetoo-kwin-correlation-probe konsole -- konsole --separate
```

The probe arms the request before starting the program, records Bash's `$!`,
and polls for newly observed windows. **Only one new, exact PID match** after a
short settle interval returns `MATCHED` and its UUID. Two new same-PID
windows give `AMBIGUOUS`; a changed-only event, unmatched PID, prior UUID,
missing inventory, or resident restart must never be silently adopted.

The optional syntax `--title-token TOKEN` records title matches for diagnosis;
**title alone is not proof**. If a program forks, the KWin PID may differ
from the shell PID, yielding a deliberate `TIMEOUT` with possible title hints.
That result is valuable evidence for designing a stronger transaction token
in a later Step 1.3b increment.

The tool does not terminate the launched process on completion, failure, or
timeout, and it does not change placement. Close disposable windows normally.
Run same-class interference tests and then repeat on both backends. The
existing `test-launch` retains its historical class-only placement POC and
must not be mistaken for a safe managed-window correlation implementation.

## Headless checks

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_step1_3a.js
bash -n tools/joetoo-kwin-correlation-probe
```

Native PID/title correspondence, timeout behavior, and process independence
remain subject to human desktop validation. This is not the Step 1.4 registry.

## Step 1.3b.2 — class candidate diagnostics (review candidate)

The existing `PollCorrelation` JSON now includes `class_candidates` on
`PENDING`, `MATCHED`, `AMBIGUOUS`, and `TIMEOUT`. Class-only matches
never affect the exact-PID decision. One conservative exception: if the
lifecycle buffer overflowed during the request, a single surviving PID
match is not declared unique; it times out with incomplete-history status. Each candidate records:

- `window_uuid`: KWin's observed UUID, not a managed-window identifier;
- `pid`: its latest observed KWin PID, which may differ from the launched PID;
- `event_id`: the broker-lifetime **added** event ID, not a durable ID;
- `currently_observed`: whether this UUID is in the live inventory now;
- `evidence`: `pid`, `class_title_hint`, or `class_only`.

An observed addition must be newer than `BeginCorrelation`, must not have
been in its baseline inventory, and must match the expected class via the
observed resource class or desktop-file hint. A later change can establish
class identity without fabricating a second addition. Removed windows may
still appear using retained lifecycle details (`currently_observed: false`).
A class or title hint is **never promoted** to `MATCHED` or ownership.

`candidate_history_complete` is false if the 128-record lifecycle cap has
lost any event since the probe began; candidates may then be missing. A
single PID candidate cannot produce `MATCHED` when history is incomplete.
A `STALE_SOURCE` response returns no candidates and marks history incomplete.
D-Bus signatures, legacy fields, managed-window behavior, KWin JS and Bash
CLI are unchanged. Probe output already prints the full terminal JSON.

Native results from Step 1.3b.1 (before this diagnostic extension): Konsole
`--separate` and Dolphin `--new-window` matched PID/UUID on gmki91/X11 and
q552u01/Wayland; an existing Chrome browser session created `about:blank`
windows under the existing browser PID on both machines, yielding the expected
exact-PID `TIMEOUT`. Confirm the new `class_candidates` output in those same
Chrome conditions; do not interpret one candidate as proof of causation.
