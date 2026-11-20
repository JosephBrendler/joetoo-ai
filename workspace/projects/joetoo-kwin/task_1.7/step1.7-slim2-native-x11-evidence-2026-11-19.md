# Step 1.7 — slim2 native X11 recovery/snapshot acceptance evidence

**Date:** 2026-11-19. **Host:** `slim2`, local Plasma X11, display `:0`,
1366×768, KWin X11 6.7.6. **Operator:** maintainer.
**Exact candidate:** `33bbbee03a5effbf1c4c31b5600254ab28374510`,
`task/joetoo-kwin-step1.7-recovery-snapshot`. Git fetch/switch verified HEAD
matched the pushed `origin/` task branch and the worktree was clean. The six
new Step 1.7 files were present. The operator performed deployment and native
tests from local `slim2` Konsole.

**Complete terminal transcripts (only trailing terminal whitespace/blank lines normalized):**

- [Initial clean baseline, disposable launch and protected duplicate-launch refusal](step1.7-slim2-initial-native-console-2026-11-19.txt)
- [Snapshot history, broker restart, retained missing record, clean sweep and fresh restore](step1.7-slim2-recovery-native-console-2026-11-19.txt)

For provenance, the original attached X11 console SHA-256 hashes (before
trailing-whitespace normalization) were `1f2188f366413d0e35c64d82b23d98b495759212678c66224bcf1cdc026bd05a`
(initial) and `2976fb2c11b21e0d3a40aaaee22673e1bef37106f9fedb8b2277b59abde1094a`
(recovery). No command/result lines were omitted.

Additional diagnostics and GUI session context were pasted by the maintainer
in the conversation. This file summarizes them without claiming tests that the
available logs do not demonstrate.

## Setup and observed readiness

- An initial attempt from SSH had `XDG_SESSION_TYPE=tty`, empty `DISPLAY`, and
  no usable graphical bus address for OpenRC. Its service restart failed.
  After moving to local X11 Konsole, the graphical bus address, `DISPLAY=:0`
  and `kwin_x11` were present. The 14-component development update/check passed.
- A restart helper's **immediate** introspection said `Service
  'org.joetoo.KWinBridge' does not exist`, while a later query successfully
  exposed all 41 bridge methods. A manual foreground invocation printed
  `Ready on session bus: org.joetoo.KWinBridge /org/joetoo/KWinBridge` and
  `KWin resident reused: joetoo-bridge`; that invocation runs a long-lived
  server until interrupted. Two GLib deprecation warnings were non-fatal.
- After normal OpenRC start and settling, the supervised Python broker was
  running with `DBUS_SESSION_BUS_ADDRESS` equal to the graphical Konsole's
  address; `RegistryStatus` reported `recovery: ready`, `managed_count: 0`,
  and `observation.synchronized: true`. This was the clean baseline, not an
  implementation blocker. Treat immediate post-start D-Bus failures as a
  readiness/timing UX issue; a bounded readiness probe is preferable.

## Native results

| Check | Evidence and outcome |
| --- | --- |
| Plan validation | `-c -f` accepted two desktop-3 recipes, 1366×768 display, no launch; PASS |
| Configured launch | Confirmed `-o` launched Konsole and Dolphin; two of two registrations and placements succeeded; PASS |
| Repeat launch with occupied slots | Second `-o` refused `managed desktop/slot conflict [win-001]`; no duplicate launch; PASS |
| Initial live inventory | `win-001` and `win-002` were present, both placement `succeeded`, `recovery: ready`; PASS |
| Timestamped saves | Three `-S` invocations produced three distinct filenames; an additional repeat also did so; PASS |
| Depth-2 retention | Two `0600` history files remained in `0700` directory; latest relative symlink pointed at newest; PASS |
| Snapshot protocol | Protocol 2, 47 common settings and two entries, `konsole`/`dolphin` on desktop 3 slots 1/2; PASS |
| Same-KWin broker restart | Bounded poll printed `PASS: broker recovery ready`, synchronized 2 present; `diff -u` of IDs/UUIDs/reservations emitted no differences; KWin D-Bus owner unchanged; PASS |
| Exact managed close | Confirmed `-d win-001` reported `backend: x11`, `state: closed`, `registration_retained: true`; PASS |
| Missing observation across restart | `GetManaged` before/after restart comparison emitted no differences; `win-001` stayed missing and `win-002` stayed present; PASS |
| Failed save | Incomplete `-S` refused twice; last-good latest symlink was unchanged; PASS |
| Progressive sweep | `-x` retired the missing `win-001` and closed present X11 `win-002`; no retained reservations; PASS |
| Restore | `-r` read saved plan, confirmed `y`, launched two fresh windows (`win-003`, `win-004`) successfully on desktop 3; PASS |

### Selected condensed console excerpts (see verbatim transcripts)

```text
✨ Configured layout: [2/2] windows completed ... (completed) [ ✅ ]
MANAGED_ID  DESKTOP  SLOT  PRESENCE  PLACEMENT  WINDOW_UUID
win-001     3        1     present   succeeded  7ab74f31-9a74-4d9e-b931-d195cfbfcb2a
win-002     3        2     present   succeeded  2e977cb3-393a-484c-a016-f7d325dcffcd

💥 joetoo-kwin: managed desktop/slot conflict [win-001]
```

```text
First:  snapshot-20261119T234913.484583580Z-47f167b891d84561c63df475a9ffcb39.conf
Second: snapshot-20261119T234914.612246356Z-b29823b63f20e2e8e9acbc3a5f02fbd4.conf
Third:  snapshot-20261119T234915.712534614Z-965c78ef5aa868269cfba5b51e855244.conf
last-session.conf -> snapshot-20261119T234915.712534614Z-965c78ef5aa868269cfba5b51e855244.conf
"protocol": 2
"settings_count": 47
```

```text
PASS: broker recovery ready
"recovery": "ready",
"managed_count": 2,
"presence_counts": {"missing": 0, "present": 2, "uncertain": 0},
"observation": {"synchronized": true}
PASS: same KWin process ownership
```

After the close and broker restart:

```text
MANAGED_ID  DESKTOP  SLOT  PRESENCE  PLACEMENT  WINDOW_UUID
win-001     3        1     missing   succeeded  7ab74f31-9a74-4d9e-b931-d195cfbfcb2a
win-002     3        2     present   succeeded  2e977cb3-393a-484c-a016-f7d325dcffcd
PASS: incomplete arrangement refused
PASS: last-good snapshot preserved
```

The confirmed `-x` cleared both records. Confirmed `-r` subsequently launched
new `win-003` (UUID `2bd87084-0ce2-4367-8718-f95c6d02fc8f`) and `win-004`
(UUID `c8b8414b-5de7-4b35-9290-946ec18c57d5`), both with successful
placement; the old managed UUIDs were not reused.

## Outstanding distinctions (do not misreport)

- **Declined `-r` not shown in this refined X11 transcript.** The operator
  answered `y` and demonstrated successful confirmation. The earlier pre-refinement
  Wayland sequence included a declined restore, and `-r` follows the existing
  confirmed planner path. The absent X11 decline is a minor coverage gap, not
  evidence of a defect; the maintainer may accept without repeating it.
- The native effect's four-method introspection and owner-match check was not
  completed in the displayed X11 test sequence (the first pasted command was
  interrupted). Nevertheless, exact native X11 managed close succeeded, with
  `backend: x11`; do not claim the four-method introspection separately passed.
- A foreground broker invocation ran until interrupted; that is normal for a
  persistent server. A user-reported Ctrl+C in a prior pasted sequence cannot
  identify a source-code deadlock from the available transcript. Avoid treating
  it as proof of either an implementation failure or an entirely successful
  uninterrupted sequence.
- A Dolphin `kf.config.core` warning about a Downloads desktop file appeared
  during restore, but placement and registration succeeded. There is no
  observed failure tied to that warning.
- No fresh compositor/reboot test, RDP/VNC matrix, or separate CLI `-L` test
  was performed in this X11 run. The combined Step 1.7 scope is same-KWin
  broker recovery and recipe-based new-instance restore, not adopting old
  identities after a new session. Previous milestones cover broader behaviors.
- At transcript end two **new** test windows were launched. No later cleanup
  is evidenced; the maintainer can close those disposable records separately
  when appropriate.

## Acceptance assessment

**No demonstrated Step 1.7 code defect blocks acceptance.** Combined with the
[Wayland evidence](step1.7-q552u01-native-evidence-2026-11-19.md), the native
X11 evidence covers both recovery modes and the refined snapshot history,
backward compatibility and fail-closed selection. The maintainer still owns
explicit milestone acceptance, any choice to waive/perform the small untested
X11 declined-restore path, and subsequent documentation/PR/merge gates.
