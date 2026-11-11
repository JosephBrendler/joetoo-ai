# Step 1.5c.5d / Increment 4 Stage 3 — native acceptance (2026-11-10–11)

**Disposition: MAINTAINER ACCEPTED for Stage 3's bounded objectives.** This is an evidence record, not a new implementation authorization. Source is the maintainer's chat-supplied operator transcripts, screenshots, and local test output; records below are selected verbatim or faithfully normalized excerpts, with endpoint hostnames omitted. No remote-authentication, TLS/NLA, server-identity, or GDM-usability claim is made.

## Scope actually accepted

1. `rdp_registration_timeout_ms` and `vnc_viewer_ready_timeout_ms` default to **300000 ms**, preserving valid per-run overrides and independent mechanical deadlines.
2. Serial configured `-o` continues after **positively confirmed terminal, known-clean pre-registration failure**, independently rechecking eligibility; failed entries remain failed.
3. Unresolved or uncertain cleanup blocks continuation; registered viewers are not sacrificed to force progress.
4. Desktop-cohort initial stacking/focus includes **successful registrations only**; the final command reports partial failure and exits normally.

No VNC/RDP normalization, broker API/schema change, configuration-loader change, or missing-slot release was accepted. Differences between existing VNC and RDP implementations may be addressed in a separate version-2 effort, not as a Stage 3 reopening.

## Validation record

| Evidence | Observed result | Limits |
| --- | --- | --- |
| Codex Stage 3 candidate report | 447 focused Python PASS, 869 full Python PASS, 161 JavaScript PASS; syntax, ShellCheck and whitespace checks PASS | Reported by Codex, not independently executed by this document author |
| `gmki91`: `./tools/restart_joetoo-kwind t` | Local **869 Python** `OK`, **161 JavaScript** PASS / 0 skipped; installation update/check, user-service restart, D-Bus introspection successful | Maintainer-operated local integration and headless verification |
| `gmki91`, native KWin X11 | Desktop 16 entries: Konsole slot 1 registered, RDP slot 2 failed with **verified cleanup**, Konsole slot 3 registered; initial stack `SUCCEEDED` | Remote endpoint intentionally not usable; observed failure reason `child_identity_rejected` after child exit |
| `q552u01`, Plasma Wayland | `loginctl ... -p Type` returned `Type=wayland`; same desktop-16 **success → clean failure → success**; initial stack `SUCCEEDED` | Code used Stage 3 continuation path despite local CLI BUILD label `1.0.16` vs `gmki91` `1.0.17` |
| Both native tests | `completed [2], failed [1], skipped [0]`, overall `2/3 ... (failed)` and command returned to Bash | Correct incomplete-status accounting, not a 3/3 claim |
| Earlier adverse/diagnostic test | A localhost/invalid RDP target produced an unresolved stop (`completed [1], failed [1], skipped [1]`); a separate Dolphin SFTP bad-host run launched and placed `3/3` | The unresolved run did **not** prove known-clean continuation; Dolphin KIO failure is application usability, not managed-placement failure |

## Native X11 operator evidence: `gmki91`

Configured effective `rdp_registration_timeout_ms=5000` for the native failure test. `vnc_viewer_ready_timeout_ms=300000` remained its default. Three desktop-16 entries were Konsole `btop`, `sdl-freerdp`, Konsole `btop`. Final successful run was executed directly (`./joetoo-kwin -vv -o -f ...`), without a `tee` pipeline.

```text
Launching desktop [16] slot [1]
Registered [win-005] UUID [8e6f417d-87ef-44c0-b8fc-031ddc78c5cc]
Launching desktop [16] slot [2]
Starting owned SDL RDP viewer; remote authentication remains unverified
RDP local outcome (selected fields):
  cleanup.broker_terminal=true
  cleanup.child_reaped=true
  cleanup.resources_released=true
  cleanup.eligible=true
  cleanup_confirmed=true
  continuation_eligible=true
  state=failed; phase=registration; reason=child_exited
  cleanup.terminal.state=failed; cleanup.terminal.reason=child_identity_rejected
Window failed; layout is incomplete
Owned pending mission ended cleanly; continuing incomplete serial plan
Launching desktop [16] slot [3]
Registered [win-006] UUID [85ee3454-5a87-42b3-abe0-c1c8d5588856]
Desktop [16] initial stacking/focus result: (completed)
Initial layout: state=SUCCEEDED, stacking=verified
  order=[8e6f417d-87ef-44c0-b8fc-031ddc78c5cc,
         85ee3454-5a87-42b3-abe0-c1c8d5588856]
  observed_order matches order
Entries: completed [2], failed [1], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [2/3] windows completed ... (failed)
```

The maintainer supplied a screenshot showing the two Konsole windows on desktop 16 without a retained RDP viewer. A prior `ps` output after an interrupted, unresolved attempt showed no `joetoo_kwin_rdp_launch.py` or `sdl-freerdp` processes, but that is not substituted for the successful test's positive broker/worker cleanup receipt.

## Native Wayland operator evidence: `q552u01`

The maintainer pulled the Stage 3 candidate to the laptop and ran:

```text
$ loginctl show-session "$XDG_SESSION_ID" -p Type
Type=wayland
$ ./joetoo-kwin -c -f task_step1.5/layers-examples/stage3-clean-failure-test.conf
Validating configured launch intent result: (completed)
DRY RUN: [3] windows; planner launches no applications
```

Then the confirmed `-o` launch yielded:

```text
Launching desktop [16] slot [1]
Registered [win-001] UUID [967a8cbf-aade-4934-bf6d-b20fe79c1e17]
Launching desktop [16] slot [2]
Starting owned SDL RDP viewer; remote authentication remains unverified
RDP local outcome (selected fields):
  cleanup.broker_terminal=true
  cleanup.child_reaped=true
  cleanup.resources_released=true
  cleanup.eligible=true
  cleanup_confirmed=true
  continuation_eligible=true
  state=failed; phase=registration; reason=child_exited
  cleanup.terminal.state=failed; cleanup.terminal.reason=child_identity_rejected
Window failed; layout is incomplete
Owned pending mission ended cleanly; continuing incomplete serial plan
Launching desktop [16] slot [3]
Registered [win-002] UUID [bfe427b9-f286-433e-97e6-d76b2e5dd14d]
Desktop [16] initial stacking/focus result: (completed)
Initial layout: state=SUCCEEDED, stacking=verified
  order=[967a8cbf-aade-4934-bf6d-b20fe79c1e17,
         bfe427b9-f286-433e-97e6-d76b2e5dd14d]
  observed_order matches order
Entries: completed [2], failed [1], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [2/3] windows completed ... (failed)
```

The maintainer-supplied Wayland screenshot shows the two Konsole windows without an RDP viewer. The local `BUILD=1.0.16` label differs from the X11 host's `BUILD=1.0.17`; this is recorded as a label difference, not evidence of different Stage 3 behavior.

## Provenance, limits and closeout

- The two desktop screenshots and full terminal outputs were provided directly in the maintainer–ChatGPT conversation on November 10–11, 2026. The excerpts above omit connection hostnames, nonessential process IDs and broker nonces. **Screenshots are not embedded in this public-repository document**; retain the supplied originals separately if a binary evidence archive is desired.
- The complete headless run also includes an operator-supplied `restart_joetoo-kwind t` transcript showing 869 Python and 161 JavaScript tests passing. The short test recipe is [`layers-examples/stage3-clean-failure-test.conf`](layers-examples/stage3-clean-failure-test.conf); it intentionally uses a failing target and should never be treated as a production profile.
- A failed/unreachable remote endpoint is not, by itself, proof of cleanup. In both accepted native tests, continuation was specifically authorized by positive terminal broker and worker evidence. A prior *unresolved* attempt stopped as designed.
- **Accepted**: Stage 3's five-minute defaults, bounded override, safe known-clean continuation, fail-closed uncertainty, successful-only cohort ordering, and incomplete overall result on both native X11 and Wayland.
- **Not claimed**: every possible failure path proved natively, all remote auth/server behaviors, complete VNC/RDP implementation symmetry, release/merge to official repositories, or Stage 4 loader behavior.
