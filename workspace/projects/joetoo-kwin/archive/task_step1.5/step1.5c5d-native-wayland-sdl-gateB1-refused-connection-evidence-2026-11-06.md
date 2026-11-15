# Step 1.5c.5d Increment 1 — Gate B1: refused RDP connection

**Date:** 2026-11-06 (local, America/New_York)  
**Operator:** Maintainer, running locally as `joe` on `q552u01`  
**Platform:** Gentoo/OpenRC, Plasma/KWin native Wayland  
**Scope:** One controlled negative native-SDL registration test, **without placement**  
**Disposition:** **PASS for Gate B1**, based on the maintainer's actual terminal transcript. **Not** full Increment 1 acceptance.

## Test objective and boundary

Demonstrate that an SDL FreeRDP child which encounters a refused connection does not become a managed viewer, does not leave an active registration request or leaked SDL child, and does not change KWin observation ownership or request window placement.

The endpoint was **`127.0.0.1:65001` on q552u01**; it was deliberately *not* `raspiubuntu401`. No remote RDP authentication, server certificate or GNOME session was involved. The operator checked the refusal immediately beforehand.

## Preconditions — actual observations

- `XDG_SESSION_TYPE=wayland`.
- `rc-service -U joetoo-kwind status`: `started`.
- `./tools/joetoo-kwind-install-poc --check`: ten installed components `Current`; OpenRC allowlist correct.
- Local Python TCP probe to `127.0.0.1:65001`: `PASS: Connection refused on port 65001.`
- `ListManaged` before test: `{"count":0,"windows":[]}`.
- No `sdl-freerdp` process in the before snapshot.
- Broker baseline:

```json
{
  "initial_layout_active": false,
  "managed_count": 0,
  "observation": {
    "observed_count": 4,
    "revision": 11,
    "source": "1794025069336-hu5g1wk8drn1ubm71osf9",
    "synchronized": true
  },
  "placement_transaction": {"id": null, "state": "IDLE"},
  "request_count": 0,
  "request_counts": {
    "ambiguous": 0, "failed": 0, "pending": 0,
    "running": 0, "succeeded": 0, "timeout": 0
  },
  "viewer_cleanup_uncertain": false
}
```

## Native invocation

```bash
python3 tools/joetoo-sdl-registration-launch.py     127.0.0.1 joe     --port 65001     --desktop 1     --slot 1     --rdp-registration-timeout-ms 15000
# End of commands

```

### Actual launcher output

```text
{"evidence_directory": "/tmp/joetoo-sdl-registration-6u3h34lu", "placement": "not_requested"}
{"child_pid": 927671, "child_start": 10107572, "request_id": "5db38e1e418d42d2acd095f4c4f25017", "placement": "not_requested", "remote_session": "unverified"}
{"placement": "not_requested", "protocol": 1, "reason": "child_identity_rejected", "remote_session": "unverified", "request_id": "5db38e1e418d42d2acd095f4c4f25017", "state": "failed"}
SDL development launcher FAILED: Child exited before registration
===== GATE B1 LAUNCHER EXIT STATUS: 1 =====
```

The **failed transaction and launcher exit 1 are expected** for a deliberately refused endpoint. The observed child exited before a qualifying window was registered. This evidence does not establish why FreeRDP selected its own numerical exit status, which was not separately printed here.

## Final independent checks — actual observations

- `RegistryStatus`: `request_count=1`, `failed=1`, `pending=0`, `running=0`, `succeeded=0`, `ambiguous=0`, `timeout=0`.
- `managed_count=0`; `ListManaged`: `{"count":0,"windows":[]}`.
- `viewer_cleanup_uncertain=false`; `placement_transaction={"id":null,"state":"IDLE"}`.
- Observation stayed `synchronized=true`; **source and revision unchanged** (`1794025069336-hu5g1wk8drn1ubm71osf9`, `11`), `observed_count=4`.
- `pgrep -a -u "$USER" -x sdl-freerdp`: no child found.
- `ps -o pid,ppid,stat,comm -p 927671`: header only; test child PID absent.
- Private evidence directory retained locally at `/tmp/joetoo-sdl-registration-6u3h34lu`. No raw log included in this report.

| Gate B1 acceptance property | Result |
| --- | --- |
| Verified non-listening local endpoint | **PASS** |
| No false positive viewer registration | **PASS** |
| Terminal failed request; no pending/running requests | **PASS** |
| No test child remaining | **PASS** |
| Observation source/revision preserved | **PASS** |
| Synchronized KWin inventory | **PASS** |
| Placement remained IDLE and not requested | **PASS** |
| No cleanup uncertainty | **PASS** |

## Scope qualifications and cross-test continuity

This B1 run began with **an empty managed registry**. It therefore proves non-creation of a managed viewer, **not** preservation of an earlier `win-001` historical record. That different property belongs to the planned coexistence/isolation gate.

The maintainer subsequently indicated a **broker restart between B1 and B2**. As a result, uninterrupted state continuity **across those two tests** is not established. This **does not invalidate or require repeating B1**: the before and after B1 observations were recorded within the same B1 test.

B2 was a distinct, operator-initiated Ctrl+C test at an NLA dialog. The operator reports that the dialog disappeared approximately **1.5–2 seconds after Ctrl+C**. That visual observation alone is *not* yet a complete B2 acceptance record; the B2 launcher output, post-exit registry state and child PID check must be reviewed independently. Do not infer B2 PASS from B1.

## Record management

This report is a focused native evidence artifact for `task_step1.5/`. Link it from current `HANDOFF.md`; keep detailed evidence out of the short dispatcher. Keep the private `stdout.log` out of Git. No source change, RDP security-policy decision, X11 registration, window placement or further native authorization follows from this PASS.
