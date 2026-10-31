# Step 1.5c.4 first-increment native acceptance record

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
