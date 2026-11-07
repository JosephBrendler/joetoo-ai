# Step 1.5c.5d Increment 1 — Gate B2: operator Ctrl+C while NLA dialog is visible

**Native observation date:** 2026-11-06, local America/New_York  
**Operator:** Maintainer on `q552u01` (Gentoo/Plasma native Wayland)  
**Test:** Stop the registration-owning launcher, rather than clicking Cancel in the NLA dialog  
**Disposition:** **PASS, bounded cancellation and cleanup**. Not full Increment 1 acceptance.

## Baseline

A maintainer-initiated `restart_joetoo-kwind` happened **before** this test's baseline. This cleared B1's historical failed request; it does not invalidate either test but prevents claiming uninterrupted registry history *between* B1 and B2.

Immediately before B2, `RegistryStatus` showed:

```json
{"observation":{"observed_count":4,"revision":12,"source":"1794025502561-e37c3mhdkzoo","synchronized":true},"placement_transaction":{"id":null,"state":"IDLE"},"managed_count":0,"request_counts":{"ambiguous":0,"failed":0,"pending":0,"running":0,"succeeded":0,"timeout":0}}
```

`ListManaged` returned `{"count":0,"windows":[]}`.

## Invocation and observed cancellation

The maintainer used a local, non-root Konsole:

```bash
python3 tools/joetoo-sdl-registration-launch.py \
    raspiubuntu401.brendler joe \
    --desktop 1 \
    --slot 2 \
    --rdp-registration-timeout-ms 120000
# End of commands

```

Actual development-launcher output (no credentials are recorded):

```text
{"evidence_directory": "/tmp/joetoo-sdl-registration-dqsva5ht", "placement": "not_requested"}
{"child_pid": 928382, "child_start": 10136244, "request_id": "281720675dc34bc7a6c3046880b4c515", "placement": "not_requested", "remote_session": "unverified"}
^C{"placement": "not_requested", "protocol": 1, "reason": "cancelled", "remote_session": "unverified", "request_id": "281720675dc34bc7a6c3046880b4c515", "state": "failed"}
SDL development launcher FAILED: Operator cancellation
Launcher exit status: 1
```

The operator pressed **Ctrl+C in the launcher Konsole** while the NLA credentials dialog was visible, without entering credentials. The dialog disappeared approximately **1.5–2 seconds** later. This is a human-observed duration, **not** an instrumented timing benchmark.

## After the cancellation

- `RegistryStatus`: `failed=1`, `pending=0`, `running=0`, `succeeded=0`, `managed_count=0`, `placement_transaction=IDLE`.
- `ListManaged`: `{"count":0,"windows":[]}`.
- Observation source **unchanged** (`1794025502561-e37c3mhdkzoo`), synchronized throughout; revision advanced from **12 to 16** with window lifecycle activity.
- `pgrep -a -u "$USER" -x sdl-freerdp`: **no process found** after launcher returned.
- `reason=cancelled`, `state=failed`, and launcher exit code **1** are the **expected** negative-test result, not a failed acceptance gate.

**Accepted result:** User interruption did not falsely register an NLA dialog, orphan the owned SDL child, leave active work, or request placement. No B2 repetition is indicated by the recorded evidence. The raw private FreeRDP log remains outside Git. This test does not address historical managed-record preservation across a restart.
