# Step 1.5d — Maintainer native acceptance and regression evidence (2026-11-12)

**Decision: Step 1.5d ACCEPTED by the maintainer on 2026-11-12.** This is acceptance of the delivered `-L`/`-l` functionality, **not** a claim that the feature branch has already been merged. The maintainer explicitly requested one additional, narrowly scoped isolated-XCB-test-fixture correction **before publication, PR and merge**. The acceptance decision does not authorize any actor to push, open a PR, merge, or perform native host operations.

## Scope accepted

- `joetoo-kwin -L DESKTOP PROGRAM MODE TARGET [over]`: one managed window; omitted and explicit `over` work. Explicit `panel`/`under` fail before launch with `not implemented yet`. Existing `-o` defaults and layers remain unchanged.
- Select a collision-free logical slot, respecting the broker's managed reservations; confirm before effects; register and place by exact UUID; execute one-shot raise above existing normal windows with broker verification, **without reflow/movement/resizing of existing peers**.
- `joetoo-kwin -l`: read-only, sorted, fixed-column managed inventory including full UUID and retained reservations.
- No expansion into `-L` panel/under support, reflow, managed-ID geometry transactions, or deferred steps 1.6–1.9.

## Native X11 — gmki91

The maintainer operated a Gentoo/KWin X11 session and reported successful `-L` SDL FreeRDP launches, including multiple viewers on the same desktop, `-l` inventory, and unsupported-layer preflight. Source test outputs were pasted into the maintainer conversation on 2026-11-12.

Representative launch (omitted layer):

```text
./joetoo-kwin -L 11 sdl-freerdp rdp rdp://joe@opi6plus01
Desktop  Slot  Program      Mode  Target                Layer  X   Y   Width  Height
11       3     sdl-freerdp  rdp   rdp://joe@opi6plus01  over   96  32  1804   972
Launching desktop [11] slot [3]
Desktop [11] initial stacking/focus result: (completed) [ ✅ ]
Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [1/1] windows completed ... (completed) [ ✅ ]
```

Representative inventory following this launch:

```text
MANAGED_ID  DESKTOP  SLOT  PRESENCE  PLACEMENT  WINDOW_UUID
win-001     3        1     present   succeeded  be76bdd2-3b58-479f-a5de-a08bbb3ddc0c
win-002     11       1     present   succeeded  3214422c-166d-4ffe-973d-12add3e34ef9
win-003     11       2     present   succeeded  e86e4edb-2237-4e8b-9451-8ffb751ea93a
win-004     11       3     present   succeeded  4113da47-b5d5-44a3-92f2-7ac52e19bbb3
```

Further successful **explicit** `over` launches on desktop 12 selected slots **1 and 2**, both reported `1/1` completion and successful initial stacking/focus. The earlier desktop-11 slot-4 attempt failed cleanly at SDL authentication/registration (not at one-shot raise); an additional intentional incorrect-password experiment reproduced the same CLI failure pattern. Both `-L ... under` and `-L ... panel` were rejected with the expected prelaunch message:

```text
joetoo-kwin: -L: layer 'under' is not implemented yet; use 'over' or omit LAYER
joetoo-kwin: -L: layer 'panel' is not implemented yet; use 'over' or omit LAYER
```

The maintainer inspected the broker after an earlier failed attempt:

```json
{
  "initial_layout_active": false,
  "initial_layout_protocol": 1,
  "managed_count": 6,
  "presence_counts": {"missing": 0, "present": 6, "uncertain": 0},
  "request_counts": {"ambiguous": 0, "failed": 1, "pending": 0, "running": 0, "succeeded": 6, "timeout": 0},
  "single_raise_protocol": 1,
  "viewer_cleanup_uncertain": false
}
```

The **actual SDL FreeRDP private log** for `aerlqr1_` included:

```text
[08:37:11:681] [ERROR][com.freerdp.core] - [nla_recv_pdu]: ERRCONNECT_LOGON_FAILURE [0x00020014]
[08:37:11:684] [ERROR][com.freerdp.client.SDL] - [handleShow]: ERRCONNECT_LOGON_FAILURE [0x00020014]
Logon failed.
```

This establishes a remote NLA logon failure **for that log**, rather than a single-raise failure. The exact association of this private log with the original failed `-L` command and the cause of the remote rejection (e.g. wrong password) were not conclusively established. The deliberately wrong-password run's CLI failure was confirmed, but a final independent log-to-command mapping was not furnished. Avoid a categorical claim that the original attempt was a bad password. The remote-session field remained appropriately `unverified`; local registration/placement must not be confused with remote authentication proof.

## Native Wayland — iota01

The maintainer used a **LattePanda Iota, Intel N150**, Gentoo hardened kernel `6.18.62-gentoo-dist-hardened-joetoo`, KDE Plasma **6.7.5**, KWin **Wayland**, with built-in **1024×600** and external **1920×1080** displays. The selected per-user plan was `~/.config/joetoo-kwin/joetoo-kwin.conf`; the system defaults files were absent and not required. The first run used explicit **1920×1080** geometry; a subsequent plan adjustment used **1024×600**, confirming the settings are explicit rather than autodetected.

First native single-window launch:

```text
./joetoo-kwin -L 4 konsole ssh nuthuvia
Desktop  Slot  Program  Mode  Target    Layer  X   Y   Width  Height
4        1     konsole  ssh   nuthuvia  over   96  32  1804   972
Registered [win-001] UUID [26fa1d11-20b0-41c1-9a1d-cdcf947f7a91]
OK launch: ... before=[1] (151,10) 722x533 after=[4] (96,32) 1804x972 ...
Desktop [4] initial stacking/focus result: (completed) [ ✅ ]
Configured layout: [1/1] windows completed ... (completed) [ ✅ ]
```

Second launch after changing the selected configuration to **1024×600**:

```text
./joetoo-kwin -L 3 konsole ssh nuthuvia
Configured display: [1024x600] (not autodetected)
Desktop  Slot  Program  Mode  Target    Layer  X   Y   Width  Height
3        1     konsole  ssh   nuthuvia  over   51  18  962    540
[20261112-11:16:00] Launching desktop [3] slot [1]
Registered [win-002] UUID [2fdffbc0-020b-4e3e-9b53-9f0b11a59dab]
OK launch: ... before=[1] (0,0) 1024x554 after=[3] (51,18) 962x540 ...
Desktop [3] initial stacking/focus result: (completed) [ ✅ ]
Configured layout: [1/1] windows completed ... (completed) [ ✅ ]
```

At that point `-l` showed `win-002` desktop 3 slot 1 before `win-001` desktop 4 slot 1, consistent with sorted read-only output.

**Critical one-shot-raise test:** while `win-002` was present on desktop 3, the maintainer launched a second `konsole ssh nuthuvia` there:

```text
./joetoo-kwin -L 3 konsole ssh nuthuvia
Desktop  Slot  Program  Mode  Target    Layer  X   Y   Width  Height
3        2     konsole  ssh   nuthuvia  over   51  18  962    540
[20261112-11:28:15] Launching desktop [3] slot [2]
Armed managed launch [1ad961349251460bb2c83f2c3b88b12f], placement [29449934fec743a7a4cc1526ae65c671]
Registered [win-003] UUID [8ede6197-81b6-4d4c-bfcd-3ef3b83cf443]
OK launch: ... before=[1] (31,7) 962x540 after=[3] (51,18) 962x540 ...
Desktop [3] initial stacking/focus result: (completed) [ ✅ ]
Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [1/1] windows completed ... (completed) [ ✅ ]
```

The maintainer supplied a screenshot showing the new Konsole in front of the previous Konsole on desktop 3. This is visual plus broker-reported evidence for the new window's one-shot raise. No before/after independent geometry recording was supplied for the older window; the transaction's successful verified broker result is the geometry-preservation evidence. SSH interactive prompt content and unrelated remote authentication are not part of this acceptance claim.

## Headless regressions and the isolated XCB fixture

The candidate previously reported **938 Python and 163 JavaScript PASS** on `gmki91` (maintainer rerun matching Codex count). Following the narrow timestamp/diagnostic changes, the `iota01` run included **949 Python and 163 JavaScript** tests. An earlier `iota01` test attempt had three `FileNotFoundError: node` errors and could not run JavaScript because Node.js was not installed; that was a test-dependency issue, subsequently resolved.

Latest `iota01` full results:

```text
FAIL: test_real_libxcb_receives_isolated_server_event
 (test_vnc_identity.IdentityPrototypeTests.test_real_libxcb_receives_isolated_server_event)
AssertionError: Lists differ: [] != [('desktop', 123)]
Ran 949 tests in 152.234s
FAILED (failures=1)
...
JavaScript: tests 163; pass 163; fail 0
...
joetoo-kwind-install-poc --check ... success
D-Bus introspection ... success
```

The test is **an isolated native libxcb ABI fixture over `socket.socketpair()`**, with a tiny simulated server thread, not a live X server or the Wayland launch path. The test calls `observer.drain(16)` immediately after constructing the observer; production `NativeObserver.drain()` uses nonblocking `xcb_poll_for_event()`. The server's event delivery is not explicitly synchronized with that assertion. A scheduling race is a **strong, source-grounded hypothesis**, not yet a proved root cause.

The maintainer reran the exact test once with `-v`, then ten times with `-q`, all PASS:

```text
python3 -m unittest tests.test_vnc_identity.IdentityPrototypeTests.test_real_libxcb_receives_isolated_server_event -v
Ran 1 test in 0.005s — OK

for n in {1..10}; do
    python3 -m unittest tests.test_vnc_identity.IdentityPrototypeTests.test_real_libxcb_receives_isolated_server_event -q || break
done
# 10 consecutive runs: Ran 1 test ... OK (each)
```

Therefore: **11/11 standalone reruns PASS**, but the earlier full Python run still must be recorded truthfully as **948/949 pass, 1 failure**, not retroactively converted to a full-suite pass.

The maintainer wants Codex to harden **only the fixture synchronization** (bounded deterministic handoff/receipt rather than sleeps), preserve production nonblocking XCB semantics and event/ownership checks, then rerun focused and full regressions. The native Step 1.5d acceptance decision stands during this test-only closeout.

## Locale and environment observations (nonblocking)

- `iota01` has joetoo's deliberate system baseline `LANG=en_US.UTF-8`, `LC_COLLATE=C`, `LC_CTYPE=C` in `/etc/env.d/02locale`. `joetoo-locale-verify` reported system baseline and noninteractive-shell policy PASS, but the intended interactive Bash override to `LC_CTYPE=en_US.UTF-8` FAIL.
- Qt/qdbus6 printed repeated ASCII-locale warnings until the maintainer temporarily exported `LC_CTYPE=en_US.UTF-8`; thereafter `./joetoo-kwin -l` displayed the inventory without warnings. Neither policy nor environment was modified permanently for this acceptance.
- No evidence connects that locale change causally to the isolated XCB failure; its event content is binary and the fixture has an independent possible scheduling race. Do not change joetoo's Gentoo build-time baseline as part of the Step 1.5d work.

## Acceptance and next actions

1. **ACCEPTED (2026-11-12):** Step 1.5d functionality, based on the maintainer's native X11/Wayland evidence and the listed headless results. No product defect observed in `-L`/`-l`.
2. **Next bounded Codex work:** harden `test_real_libxcb_receives_isolated_server_event` synchronization only, add focused evidence as justified; do not change production XCB poll semantics or unrelated implementation.
3. **Post-fix:** inspect diff and full Python/JavaScript results on the final revision, then maintainer explicitly authorizes commit/push, PR and merge in separate steps. Until then, branch remains unmerged. No implicit publication authority.
4. **Separate backlog:** interactive Bash locale override investigation, future packaging and the deferred Step 1.6+ features. Neither is a 1.5d acceptance blocker.

**Source/provenance:** maintainer command transcripts, screenshot and verbal acceptance in the ChatGPT conversation on 2026-11-12. The shorter excerpts above omit lengthy benign SDL and Qt output; they are not synthetic test results or a complete raw transcript archive. Record a precise final commit SHA and any subsequent full regression under a follow-up evidence entry once the fixture fix is completed.
