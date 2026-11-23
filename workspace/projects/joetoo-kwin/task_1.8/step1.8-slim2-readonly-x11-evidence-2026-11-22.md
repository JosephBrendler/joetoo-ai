# Step 1.8 — slim2 native X11 evidence for read-only `-s` / `-i`

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-22. **Host:** `slim2`, local Plasma **X11** (`XDG_SESSION_TYPE=x11`, `DISPLAY=:0`), KWin **6.7.6** and `kwin-x11` **6.7.6** installed. **Operator:** maintainer. **Task branch:** `task/joetoo-kwin-step1.8-cli-completion`; source at `f3fef58` for the initial tests, with subsequent test-only repair published as **`cadf992`**.

**Provenance:** Relevant selected console excerpts supplied by the maintainer. This is **not a full unabridged test transcript**: the full 1,089-test Python dot-progress, the failing assertion's embedded complete CLI source dump, and individual lines for all 163 JavaScript checks are intentionally not duplicated. Counts and failure names reproduce the supplied run summary; do not reinterpret a failed full suite as a pass.

## Git and session setup

The maintainer fetched `origin`, created a local tracking branch from the remote Step 1.8 branch, fast-forwarded local `main` to `7fdd2cf`, then deleted the closed local Step 1.6/1.7 branches with `git branch -d` after checking that they were merged. The working tree was clean and the Step 1.8 branch initially tracked `f3fef58`.

Early commands reported `XDG_SESSION_TYPE=tty`, and `-s`/`-l` reported an unavailable broker. A later inspection from the actual graphical shell established:

```text
XDG_SESSION_TYPE=[x11]
DISPLAY=[:0]
XDG_RUNTIME_DIR=[/run/user/1000]
DBUS_SESSION_BUS_ADDRESS=[session address present; omitted here]
 * status: stopped
  23776 tty8     /usr/bin/kwin_x11
-rwxr-xr-x 1 joe joe   3526 Nov 19 16:24 /home/joe/.config/rc/init.d/joetoo-kwind
-rwxr-xr-x 1 joe joe 167079 Nov 19 16:24 /home/joe/.local/libexec/joetoo-kwind
```

The stopped user-level broker explains the initial `RegistryStatus`/`ListManaged` errors; they were **not** demonstrated CLI defects. The maintainer explicitly ran `./tools/restart_joetoo-kwind`, whose operator-controlled workflow stopped the user service, updated the 14 POC components, unloaded the `joetoo-bridge` resident script, started the service, ran Python/JavaScript suites and checked the installation. The console reported successful stop/update/unload/start, a successful installed-file `--check`, and successful D-Bus introspection including `GetManaged`, `ListManaged` and `RegistryStatus`.

## Lint and test results during restart

```text
$ validate_scripts ./joetoo-kwin -l
 ✨ looking for shellcheck ... (found)                                                            [ ✅ ]
---[ slim2 validate_scripts-1.0.17 ]---------------------------------------------------------------------
⌚Real: 0m21.976s  User: 0m11.906s  Sys: 0m0.820s (57.00%)
✨ done; result: (Ok ✅)                                                                         [ ✅ ]
✨ validate_scripts complete. Total elapsed time (DD:HH:MM:SS:mmm): [00:00:00:22:190]

$ ./tools/restart_joetoo-kwind
[service stop, POC update, resident unload, and service start all reported success]
[Python suite result]
FAIL: test_fixture_keeps_ordinary_open_flag_unimplemented (test_step1_4d_cli.TestMultiLaunchFixtureTests.test_fixture_keeps_ordinary_open_flag_unimplemented)
AssertionError: 'not yet integrated' not found in [current joetoo-kwin source]
----------------------------------------------------------------------
Ran 1089 tests in 266.498s

FAILED (failures=1)
 ✨ python tests done; result: (error!)                                          [ ❌ ]
[JavaScript suite summary]
ℹ tests 163
ℹ suites 0
ℹ pass 163
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 1299.565924
 ✨ javascript tests done; result: (success!)                                    [ ✅ ]
```

The bracketed descriptions above mark deliberate condensation of the very long console output. The sole Python failure was the **stale Step 1.4d test** checking that ordinary `-o` remained unimplemented; `-o` is already implemented and accepted. No product regression was demonstrated by this assertion. The maintainer replaced that test method to verify that `test-multi-launch` remains distinct from `-o`, validated the new test on slim2 (reported, full console output not supplied), and pushed the test-only change as `cadf992`. Q552u01 fast-forwarded and independently showed **3/3 focused Step 1.4d tests PASS**. **The complete 1,089-test Python suite was not shown rerunning after this repair.**

## Post-restart registry and live CLI results

The operator queried the running broker directly. Relevant output:

```text
$ qdbus6 $bus $path $bus.ListManaged | jq .
{
  "count": 2,
  "windows": [
    {
      "connection": "unknown",
      "intended": {"desktop": 3, "slot": 1},
      "managed_id": "win-003",
      "placement": "succeeded",
      "presence": "present",
      "request_id": "bde35b19f884496ab6a72627fb48f0af",
      "run_id": null,
      "window_uuid": "2bd87084-0ce2-4367-8718-f95c6d02fc8f"
    },
    {
      "connection": "unknown",
      "intended": {"desktop": 3, "slot": 2},
      "managed_id": "win-004",
      "placement": "succeeded",
      "presence": "present",
      "request_id": "7f632f71668946819560d1ec39676194",
      "run_id": null,
      "window_uuid": "c8b8414b-5de7-4b35-9290-946ec18c57d5"
    }
  ]
}

$ ./joetoo-kwin -s
Broker registry status (snapshot; not remote connection health)
State: No reported Busy/uncertain flags
Managed windows: 2 (present=2, missing=0, uncertain=0)
Launch requests: 2 (pending=0, running=0, succeeded=2, failed=0, timeout=0, ambiguous=0)
Observation: synchronized; observed=5; revision=13
Placement transaction: IDLE
Recovery: ready
Capabilities: managed_close=1, snapshot=1, viewer=1, initial_layout=1, single_raise=1

$ ./joetoo-kwin -l
MANAGED_ID  DESKTOP  SLOT  PRESENCE  PLACEMENT  WINDOW_UUID
win-003     3        1     present   succeeded  2bd87084-0ce2-4367-8718-f95c6d02fc8f
win-004     3        2     present   succeeded  c8b8414b-5de7-4b35-9290-946ec18c57d5

$ ./joetoo-kwin -i win-004
Managed window information (broker record; not remote connection health)
MANAGED_ID: win-004
WINDOW_UUID: c8b8414b-5de7-4b35-9290-946ec18c57d5
DESKTOP: 3
SLOT: 2
PRESENCE: present
PLACEMENT: succeeded
OBSERVATION: last-known (not independently verified live)
PID: 163262
RESOURCE_CLASS: dolphin
LAST_KNOWN_FRAME: 68 23 768 558
```

The direct `RegistryStatus | jq .` additionally reported `placement_transaction: {id: null, state: IDLE}`, `managed_count: 2`, `presence_counts: {present: 2, missing: 0, uncertain: 0}`, `request_count: 2`, `observation.synchronized: true`, and `recovery: ready`; the source-tree CLI accurately rendered this information.

These `win-003`/`win-004` UUIDs match the new windows recorded in [accepted Step 1.7 slim2 X11 evidence](../archive/task_step1.7/step1.7-slim2-native-x11-evidence-2026-11-19.md). That supports continuity of those registered identities after the broker restart; this abbreviated Step 1.8 test did **not** repeat all of Step 1.7's recovery-specific assertions or before/after comparisons.

## Assessment and outstanding work

**Observed:** KWin 6.7.6 native X11, POC broker successfully restarted, synchronized and recovered two present managed records; CLI `-s`, `-l`, and `-i` succeeded; extended ShellCheck passed; 163/163 JavaScript tests passed. **Repair completed:** an obsolete Python fixture assertion was updated and published at `cadf992`, then verified by 3/3 focused tests on q552u01. **Still pending:** complete Python-suite rerun after the fixture edit (if needed for final acceptance), installed CLI lookup of the new `joetoo_kwin_readonly.py` helper, and any native `-L under` implementation/proof. See the companion [q552u01 Wayland evidence](step1.8-q552u01-readonly-wayland-evidence-2026-11-22.md).
