# Step 1.5c.4 native acceptance record

The first-increment results below are historical. The final bounded-candidate
closure at `a3c50fc` is recorded in the last section; earlier failures and proposed
retests are retained rather than retroactively relabeled.

## First increment — historical baseline

Provenance: **maintainer-reported native acceptance**, supplied in the task message
following ChatGPT review of actual logs/screenshots. Codex did not execute native
GUI/KWin/SSH tests or retrieve missing raw logs. Both hosts tested committed candidate
35d1b072b763df8126c602d9840c0ad243a9a656. This is an evidence summary, not manufactured
raw output. The current corrective changes require only the narrow retests below.

| Scenario | gmki91 X11 | q552u01 Wayland |
| --- | --- | --- |
| Actual count and ordered desktop UUID inventory | PASS | PASS |
| Offline/descriptive -c; decline causes no provisioning/application launch | PASS | PASS |
| Missing directory rejection before confirmation; empty target opens HOME | PASS | PASS |
| Dolphin new-window positive PID/UUID registration, membership and geometry | PASS | PASS |
| Append required desktops before launching; observed existing IDs stay ordered | PASS | PASS |
| Adequate existing capacity causes no provisioning | PASS | PASS |
| Mixed Konsole/Dolphin distinct managed UUIDs | PASS | PASS |
| Duplicate original slot guard, including after manual geometry change | PASS | PASS |
| Independently launched Dolphin not adopted | PASS | PASS |
| Existing Konsole SSH functionality | PASS | PASS |
| Controlled Busy before confirmation, cancellation, subsequent reacquisition/provisioning | NOT REPORTED in this increment | PASS |
| Completed invocation releases lock with Dolphin alive | NOT REPORTED in this increment | PASS |
| Closed Dolphin becomes missing while retaining history | NOT REPORTED in this increment | PASS |
| Original Bash after SSH logout (PID 3562219 unchanged) | Earlier accepted evidence | PASS |
| Actual graphical underlay stacking | NOT IMPLEMENTED | NOT IMPLEMENTED |

X11: count 20 manually reduced to 16; append 16 to 17 succeeded and Dolphin verified
on desktop 17. Two-Konsole/one-Dolphin and two-Konsole/two-Dolphin plans completed.
Desktop 21 rejected with configured desktop_limit=20. Overlap shows graphical geometry
alone is not an underlay. Manual movement did not release the logical slot association.

Wayland: initial six desktops, KWin owner :1.9. Append 6 to 7 and then 7 to 17
succeeded. Launch orders Dolphin→Konsole (2/2), Konsole→Dolphin (2/2), two Konsole→
Dolphin (3/3), and two Konsole→two Dolphin (4/4) passed. Later windows generally
appeared above earlier ones: observed ordering, not a guaranteed stacking contract.
Moving/resizing win-018 preserved its original slot guard. Independent Dolphin did
not increase managed count. Closing win-004 retained history as presence=missing.

## Definitive Wayland lock/cancellation evidence

While A waited for confirmation, B immediately returned Busy; managed count stayed 15.
After A was declined with n, B acquired the lock, reached confirmation and was approved.
B appended desktop 18 from 17, spawned Dolphin PID 3585470, registered win-016 with
UUID 0ec37d9f-e30f-4ff9-b83c-19d5110bfea7, and verified desktop 18 at (96,32),
1804x972. Final state: 18 desktops, 16 managed windows; Dolphin visually present.
Disposition: PASS. No further native concurrency test is required for this increment.

## Untested/disruptive cases and corrective retests

KWin session replacement, desktop removal/reordering during provisioning, deliberate
capacity exhaustion and destructive races were NOT TESTED natively. Existing headless
coverage is retained; do not infer passes from the normal append tests.

For the current correction, maintainer should verify on both backends:

1. Put a config outside HOME and use a relative Dolphin directory that exists beneath
   HOME, including spaces; verify it opens that directory. Empty and absolute behavior
   should remain as accepted. This revised relative-path contract has no native PASS yet.
2. Trigger one invalid desktop/configuration: announcement, single diagnostic and
   failed result should occupy readable lines, with a nonzero status and no launch.
3. With adequate desktops, notice should explicitly say capacity is adequate. With a
   shortfall, it should give the exact missing count before confirmation. Keep provisioning
   and cancellation behavior as previously accepted; no need to repeat disruptive races.

New mock lifetime coverage verifies Dolphin does not retain FD 9 after completion.
Graphical layer/protrusion policy remains a separately reviewed proposal, not part of
these acceptance results. No additional native test results are claimed by Codex.


## Graphical layers and bounded focus — acceptance closure at a3c50fc

**Tested candidate:** `a3c50fc54f95e25fd766b58037e773977f854f33`,
`joetoo-kwin: implement graphical layers and bounded focus verification`, on
`task/joetoo-kwin-step1.5c4-graphical-launch` (not merged by this record).
**Provenance:** maintainer-reported X11/Wayland observations supplied in the
acceptance-closure task. Logs/screenshots were reviewed in the maintainer's ChatGPT
conversation; no additional raw artifact paths were supplied for this closure.
Codex inspected the local source/tests at this SHA, but did not execute native tests,
retrieve those missing artifacts or rerun the automated suites during documentation closure.
The maintainer explicitly identified the Wayland checkout as this SHA with no source
changes; X11 testing included the feature and subsequent focus correction accepted
as this baseline. Individual earlier X11 experiments are not assigned invented SHAs.

### gmki91 — KWin X11

| Scenario | Result and observed dimensions |
| --- | --- |
| Managed Konsole/Dolphin | PASS: positive registration, geometry and desktop placement |
| Panel/under and five-window mixed layers | PASS: relative stacking; mixed bottom-to-top slots `1 4 3 2 5` |
| Interleaved desktops | PASS: desktop groups launched and finalized separately |
| Four panels plus explicit under | PASS: panel allocation and explicit-budget warning |
| Under-only | PASS: no deliberate focus target |
| Manual overrides / duplicates | PASS: raise, resize, movement and desktop switching persist without restoration; occupied slots reject |
| Displayed-desktop preferred Dolphin focus | PASS after correction: keyboard Ctrl+L reached panel without preceding click; bounded verification succeeded |
| Configuration default | PASS: unset XDG_CONFIG_HOME and absent user file selected `/etc/joetoo-kwin/joetoo-kwin.conf` with `-c` |

**Historical failure retained:** the pre-correction two-Dolphin runs on desktops 4
and 2 had successful geometry and matching under→panel stack, but immediate focus
readback still named the underlay. The later Ctrl+L observation supported delayed
focus without establishing causation. See the [focus investigation and correction](step1.5c4-delayed-focus-review.md)
and [earlier UUID compatibility investigation](step1.5c4-initial-layout-compatibility.md).
The corrected transaction reported `SUCCEEDED`, `focus=verified`,
`focus_observation=delayed`, `focus_elapsed_ms=5`, with configured 500/25 ms bounds.
This closes the demonstrated premature-readback failure, not every possible focus race.

### q552u01 — KWin Wayland

The maintainer synchronized/deployed the same candidate and verified a genuine
KWin Wayland session. Reported headless results: **287 Python tests PASS**, **50
JavaScript tests PASS**, with relevant syntax, ShellCheck and project validation PASS.
These are maintainer-executed results, not a new Codex run. Earlier Codex Node logs
counted four test files; the maintainer's runner enumerated individual cases.

| Desktop(s) | Configuration | Result |
| --- | --- | --- |
| 2 | `final-under.conf` | PASS: panel/under placement and relative stack |
| 3 | `under-only.conf` | PASS: two underlays, no automatic focus target |
| 4 | `cascade_joe2.conf` | PASS: displayed-desktop panel focus verified immediately |
| 5 | `cascade.conf` | PASS: five-window mixed-layer relative stack |
| 6, 7 | `interleaved.conf` | PASS: separate successful group transactions |
| 8 | `budget-warn.conf` | PASS: four implicit panels plus one explicit underlay |

Displayed-desktop focus reported `focus=verified`, `focus_observation=immediate`,
`focus_elapsed_ms=0`, with preferred and observed UUIDs matching. Geometry, stack
and focus were separately reported; inactive groups' preferred targets are intent,
not simultaneous keyboard focus. Neither the Wayland immediate nor X11 delayed
sample establishes a backend-wide timing guarantee.

After the layout battery, ListManaged reported **21 windows**, all
`placement=succeeded` and `presence=present`. On desktop 5, moving/resizing/raising
windows persisted after leaving/returning; managed UUIDs and original slot associations
remained. Repeating the configuration rejected conflict `win-007` without disturbing them.

**SSH regression — PASS:** on desktop 9, Konsole registered as `win-022`, UUID
`9fc13176-8644-4b3f-a16f-508a2bb9015e`; initial placement/stacking succeeded and the
remote shell identified `nuthuvia`. Logout returned the same Konsole to original
local Bash on q552u01, reported PID `3957428`. Presence remained present and initial
placement succeeded. This is shell-lifecycle evidence, not broker transport telemetry.

### Disposition and limits

The maintainer's planned native graphical-layer battery is complete on both backends.
The accepted first-increment results above remain scoped to their tested baseline.
HOME-relative paths containing spaces, exact invalid-config diagnostic formatting,
and user-file precedence are headless-covered but have no additional explicit native
transcript in this closure; do not invent new PASS results for them. Exhaustive clickable
exposure across decorations/scaling, remembered per-desktop active-window behavior,
disruptive session/capacity changes and rare expiry/interruption races are not established
by these normal native runs. Existing focused tests cover bounded failures; this does
not require destructive native testing for merge readiness.

This closes the **implemented bounded candidate**, not every transport in the wider
Step 1.5c.4 outline or the separate Step 1.5d regression gate. SFTP, SSH-protected VNC,
RDP and packaging integration remain deferred. See the [merge-readiness audit](step1.5c4-review.md#merge-readiness-audit--a3c50fc)
for traceability, follow-ups and the maintainer's next decision.
