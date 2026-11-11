# Step 1.5c.5d — Increment 3 native X11 operator-controlled SDL RDP placement (2026-11-09)

**Status during the original native X11 tests: `software` AND `auto` EXACT-UUID PLACEMENT PASSED; INCREMENT 3 NOT YET FORMALLY ACCEPTED.** This file preserves the original test results, the *pre-fix* sequential-launch failure and the size discrepancy. **The sequential-launch defect was subsequently fixed and accepted natively**, as documented in the [2026-11-09 sequential-regression closeout](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md); native Wayland placement and the size question remained outstanding.

**Project:** `workspace/projects/joetoo-kwin/`  
**Task:** `task_step1.5/`  
**Repository/branch:** `JosephBrendler/joetoo-ai` / `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Implementation candidate reviewed and pushed:** [`e7f63ce2a9bbb0ed09f7f7465099e360ecd88fa1`](https://github.com/JosephBrendler/joetoo-ai/commit/e7f63ce2a9bbb0ed09f7f7465099e360ecd88fa1) (five files: `joetoo-kwin-resident.js`, `libexec/joetoo-kwind`, `tools/joetoo-sdl-release-placement.py`, `tests/test_rdp_placement.py`, `tests/test_rdp_placement.js`).  
**Host:** `gmki91`, native Plasma/KWin X11; remote RDP endpoint `opi6plus01.brendler`, Ubuntu GNOME Remote Login, with GDM greeter visible in the viewer.  
**Evidence provenance:** maintainer-pasted terminal output and two before/after native screenshots in the November 9 conversation. This document records the supplied data, not an independently rerun graphical test. Screenshot images remain in the conversation and are not copied into the repository, to avoid unrelated desktop-content disclosure.

## 1. Implementation and headless verification

The implementation adds a deliberately separate operator placement action: `SubmitSdlPlacement`, `TakeSdlPlacement`, `PollSdlPlacement`, `CancelSdlPlacement`, and `tools/joetoo-sdl-release-placement.py`. It targets a registered managed ID, resolves the broker-owned exact KWin UUID, checks the original owner/child/source and current observation, and reuses KWin's existing geometry verification. It does **not** automatically place a window during SDL registration, infer remote login status, relocate prompts, or establish a full configured `-o` RDP recipe.

An initial `./tools/restart_joetoo-kwind test` installed the updated files, restarted the service and displayed all four new methods by D-Bus introspection, but the Python suite reported **two errors** because the Gentoo host had no `node` executable. The JavaScript suite also could not start (`node: command not found`). These were missing test prerequisites, not demonstrated implementation failures. After Node.js was available, the maintainer supplied:

```text
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_rdp_broker test_rdp_launch test_rdp_development_launcher test_rdp_placement
Ran 191 tests in 1.505s
OK

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
Ran 676 tests in 91.367s
OK

$ node --test --test-isolation=none tests/test_*.js
ℹ tests 158
ℹ pass 158
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0

$ git diff --check
# No diagnostic output
```

Those are native-host *headless* regressions, not live KWin-placement proof. The installation/check and D-Bus interface discovery also passed. See previous [Increment 2 registration-only evidence](step1.5c5d-increment2-native-x11-registration-2026-11-08.md) for the earlier 644/145 baseline; the 676/158 figures here supersede it for this implementation candidate.

## 2. Initial rejected placement with no current registration — correct fail-closed behavior

After the service restart, `ListManaged` returned `{"count":0,"windows":[]}`. A placement attempt for historical `win-001`, before a new SDL registration in this broker lifetime, returned:

```text
$ python3 tools/joetoo-sdl-release-placement.py win-001 --confirm --desktop 1 --slot 2 --x 0 --y 0 --width 800 --height 600
SDL placement FAILED: SubmitSdlPlacement failed: org.joetoo.KWinBridge.InvalidRequest
```

This is expected: managed IDs are broker-lifetime identifiers; a previously closed/restarted viewer cannot be adopted from an old session.

## 3. Native `software` renderer — successful placement and retained lifecycle

The maintainer started the development launcher and left the supervisor and viewer open:

```bash
python3 tools/joetoo-sdl-registration-launch.py \
    opi6plus01.brendler joe \
    --desktop 1 --slot 2 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer software \
    --rdp-x11-identity-settle-ms 500
```

Registration evidence: `managed_id=win-001`, registered child PID `4107789`, registration request `e73aafdd2e474a4399814973c617cee7`, exact UUID `4480282f-c283-4edb-bd92-75f98b080240`, `presence=present`, `placement=not_requested`, intended `desktop=1`, `slot=2`.

The independent operator placed that viewer:

```bash
python3 tools/joetoo-sdl-release-placement.py win-001 \
    --confirm --desktop 1 --slot 2 \
    --x 0 --y 0 --width 800 --height 600
```

```json
{"managed_id":"win-001","placement":"succeeded","protocol":1,"reason":"verified","registration":"registered","remote_session":"unverified","window_uuid":"4480282f-c283-4edb-bd92-75f98b080240"}
```

The shown native window moved to the upper-left corner. Subsequent `GetManaged` and `ListObserved` independently reported the **same UUID**, `placement=succeeded`, `presence=present`, `desktops=[1]`, `on_all_desktops=false`, but observed frame geometry **`x=0,y=0,width=1032,height=804`**, rather than requested 800×600.

After clicking the viewer's titlebar X, the maintainer supplied a `GetManaged win-001` record retaining:

```json
{
  "state": "FOUND",
  "window": {
    "managed_id": "win-001",
    "window_uuid": "4480282f-c283-4edb-bd92-75f98b080240",
    "intended": {"desktop": 1, "slot": 2},
    "placement": "succeeded",
    "presence": "missing",
    "observation": {
      "geometry": {"x": 0, "y": 0, "width": 1032, "height": 804},
      "desktops": [1],
      "on_all_desktops": false,
      "pid": 4107789,
      "resource_class": "com.freerdp.client.sdl3"
    }
  }
}
```

The retained observation is historical after close, **not** proof that the process remains alive. Trying placement on the missing `win-001` returned `org.joetoo.KWinBridge.InvalidRequest`; the broker did not substitute another window. This is a **PASS** for exact-UUID placement, missing-state retention and closed-window rejection.

## 4. Sequential registration blocked by stale development-launcher preflight — confirmed defect

A subsequent `auto` registration was attempted with `desktop=1,slot=3`, after the prior `software` viewer had closed. The development launcher returned:

```text
SDL development launcher FAILED: Broker is busy
```

The maintainer's concurrent `RegistryStatus` proved the previous placement was **terminal**, not active:

```json
{
  "initial_layout_active": false,
  "managed_count": 1,
  "observation": {"synchronized": true},
  "placement_transaction": {
    "id": "4d0e192ef14c4592bcde27686c53279a",
    "state": "OK"
  },
  "presence_counts": {"missing": 1, "present": 0, "uncertain": 0},
  "request_counts": {
    "ambiguous": 0,
    "failed": 0,
    "pending": 0,
    "running": 0,
    "succeeded": 1,
    "timeout": 0
  },
  "viewer_cleanup_uncertain": false
}
```

**Root cause, verified by reading the pushed source:** `tools/joetoo-sdl-registration-launch.py` insists that `placement_transaction == {"id":null,"state":"IDLE"}` both in its initial preflight and its pending-registration guard. That rejects previous terminal `OK` and `ERROR` statuses even when there are no active requests and cleanup is certain. The existing configured-launch preflight accepts `IDLE|OK|ERROR`. This is **not** a slot 2 versus slot 3 collision; a distinct slot was requested. It is a **real sequential-reuse defect** and must be fixed/tested before Increment 3 is declared complete or Increment 4 serial integration begins.

The maintainer used `./tools/restart_joetoo-kwind notest` to clear the prior transaction, confirmed `{"count":0,"windows":[]}`, and continued the isolated `auto` test. This restart was a test workaround, **not** an acceptable per-viewer operational procedure.

## 5. Native `auto` renderer — successful placement, repeated geometry and closure

After that restart, the maintainer launched:

```bash
python3 tools/joetoo-sdl-registration-launch.py \
    opi6plus01.brendler joe \
    --desktop 1 --slot 3 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer auto \
    --rdp-x11-identity-settle-ms 500
```

New `win-001`: registration request `56fcc46aac9b4f34827f577d62020174`, PID `4152504`, exact UUID **`2482a3db-ae8f-488a-a752-02de3ed52711`**; intended `desktop=1,slot=3`, `presence=present`, `placement=not_requested`.

```bash
python3 tools/joetoo-sdl-release-placement.py win-001 \
    --confirm --desktop 1 --slot 3 \
    --x 120 --y 90 --width 800 --height 600
```

The placement command returned `placement=succeeded`, `reason=verified`, `registration=registered`, `remote_session=unverified` and the same UUID. The native screenshot showed the window moved to `(120,90)`, with the remote GNOME GDM greeter still visible.

The maintainer then ran four observations at two-second intervals, supplying the following JSON output:

```text
--- Geometry observation 1 ---
{"placement":"succeeded","presence":"present","uuid":"2482a3db-ae8f-488a-a752-02de3ed52711","geometry":{"height":804,"width":1032,"x":120,"y":90},"desktops":[1]}
--- Geometry observation 2 ---
{"placement":"succeeded","presence":"present","uuid":"2482a3db-ae8f-488a-a752-02de3ed52711","geometry":{"height":804,"width":1032,"x":120,"y":90},"desktops":[1]}
--- Geometry observation 3 ---
{"placement":"succeeded","presence":"present","uuid":"2482a3db-ae8f-488a-a752-02de3ed52711","geometry":{"height":804,"width":1032,"x":120,"y":90},"desktops":[1]}
--- Geometry observation 4 ---
{"placement":"succeeded","presence":"present","uuid":"2482a3db-ae8f-488a-a752-02de3ed52711","geometry":{"height":804,"width":1032,"x":120,"y":90},"desktops":[1]}
```

After titlebar-X closure, `GetManaged win-001` returned:

```json
{
  "state": "FOUND",
  "window": {
    "connection": "not_attempted",
    "intended": {"desktop": 1, "slot": 3},
    "managed_id": "win-001",
    "observation": {
      "caption": "joetoo-rdp-371a6ca149454cc569265df16340a92c75fd5180b75e23207be0732d5ba2717d",
      "desktop_file": "",
      "desktops": [1],
      "geometry": {"height": 804, "width": 1032, "x": 120, "y": 90},
      "on_all_desktops": false,
      "pid": 4152504,
      "resource_class": "com.freerdp.client.sdl3"
    },
    "placement": "succeeded",
    "presence": "missing",
    "request_id": "56fcc46aac9b4f34827f577d62020174",
    "run_id": null,
    "window_uuid": "2482a3db-ae8f-488a-a752-02de3ed52711"
  }
}
```

The post-close UUID is unchanged; no replacement adoption was observed. This is a **PASS** for the `auto` exact-UUID placement and closeout lifecycle.

## 6. Geometry discrepancy — reproducible, mechanism not yet proven

| Renderer | Requested frame | Subsequent observed frame | Observed position/desktop | Result |
| --- | --- | --- | --- | --- |
| `software` | 800×600 | **1032×804** | (0,0), desktop 1 | Placement `succeeded`; stable requested size **not** established |
| `auto` | 800×600 | **1032×804**, four successive checks | (120,90), desktop 1 | Placement `succeeded`; stable requested size **not** established |

The shared dimensions are consistent with a 1024×768 RDP client area plus X11 decorations, but the data supplied do **not** prove the exact decoration size, which party initiated any resize, or whether the broker briefly verified 800×600 before a later client resize. The development launcher's `development_argv` currently passes no `/size` option. Treat the FreeRDP-window-sizing explanation as a **hypothesis**, not a proven root cause. The placement result `reason=verified` is a point-in-time check, **not** continuous layout enforcement.

**Do not** add an automatic endless resize/focus correction loop. A focused client-area/frame-size study should establish how intended geometry maps onto SDL FreeRDP's negotiated desktop/window sizing and distinguish what belongs in Increment 3 placement from future Increment 4 plan-derived client launch settings.

## 7. Acceptance status and remaining engineering work

| Item | Status |
| --- | --- |
| Codex Increment 3 candidate pushed | **DONE**, commit `e7f63ce` |
| Python focused/full tests | **PASS**, 191 / 676 |
| JavaScript tests | **PASS**, 158 |
| Native X11 `software` exact-UUID placement and closure | **PASS** |
| Post-close placement rejection | **PASS** |
| Native X11 `auto` exact-UUID placement and closure | **PASS** |
| Multiple sequential registrations in same broker lifetime after `OK` | **FAIL**, confirmed development-launcher guard defect |
| Stable requested 800×600 frame size | **NOT ESTABLISHED**, reproducibly later 1032×804 |
| Native Wayland placement of registered SDL viewer (e.g. `q552u01`) | **NOT YET TESTED** |
| Overall Increment 3 acceptance | **OPEN**, pending focused correction/validation |

**Next engineering steps, in order:** (1) correct and regression-test both development-launcher placement preflight guards so clean terminal `OK`/`ERROR` history permits subsequent registration while active/uncertain work remains blocked; (2) characterize SDL RDP client-area vs KWin decorated-frame sizing without changing the established one-shot placement policy; (3) execute one separately maintainer-authorized native Wayland exact-UUID placement and closure test; (4) rerun focused/full regressions and record any native follow-up evidence, then decide Increment 3 closure. Do not conflate these tasks with Increment 4's already-decided sequential, human-interactive configured `-o` integration or its strict prohibition on killing clients merely because credential entry takes time.

Related: [active HANDOFF](HANDOFF.md), [task README](README.md), [accepted serial-workflow strategy](step1.5c5d-increment3-strategy-decision.md), [Increment 2 native X11 registration](step1.5c5d-increment2-native-x11-registration-2026-11-08.md).

## 8. Subsequent native sequential-registration resolution (2026-11-09)

The `FAIL` and proposed launcher correction in §§4 and 7 are preserved **as historical pre-fix evidence**, not as current blockers. The maintainer signed/pushed [`5a2e152`](https://github.com/JosephBrendler/joetoo-ai/commit/5a2e152ab4f22e21be14c0df2f2cee17e9a6dd8c); on `gmki91` the corrected installation passed 691 Python and 158 JS tests. Viewer A (`software`) registered, placed and closed; viewer B (`auto`) then registered in a different slot **without a broker restart**, with A's original UUID and terminal `OK` transaction retained. The final registry contained two distinct registrations, both missing after closure, zero errors and `observation.synchronized=true`. **Sequential-registration defect CLOSED / NATIVE ACCEPTED.** [Full native A/B transcript](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md). Increment 3 overall remains open for native Wayland placement and the separate SDL/KWin frame-size disposition.
