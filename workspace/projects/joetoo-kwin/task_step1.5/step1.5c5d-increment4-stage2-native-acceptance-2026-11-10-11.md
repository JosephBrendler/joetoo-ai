# Step 1.5c.5d / Increment 4 Stage 2 -- native acceptance (2026-11-10--11)

**Disposition: MAINTAINER ACCEPTED for the defined Stage 2 scope.**
This is a durable evidence record, not permission to implement Stage 3 or to
modify a production repository. Operator-supplied terminal transcripts and
screenshots support the observations summarized below. Quoted output is
selective; target machine names/connection arguments are omitted where not
necessary for the behavior being established. No credentials are recorded.

## Source and validation baseline

- joetoo-ai project: `workspace/projects/joetoo-kwin/`
- Branch: `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`
- Accepted Stage 2 implementation: `caba9f4d3ae62b48c6d5f602af36e43fb2d4d25b` (`joetoo-kwin: Increment 4 Stage 2 native test candidate`). Maintainer signed and published the candidate; signed status should be independently verified if required for publication policy.
- Later published branch baseline: `2d2917d5843ca0e6fbcdb6803cbc3262dd70569b` (adds the maintainer's Wayland testing example only). This later commit does not change Stage 2 implementation code.
- Codex regression at corrected Stage 2 candidate: **850 Python / 161 JavaScript**, zero JavaScript skips, plus Bash/Python syntax, ShellCheck and `git diff --check` PASS. On `gmki91`, maintainer earlier independently verified **844 Python / 161 JavaScript** after lifecycle correction; Codex reported 850 after the repeated-preflight fix. Later q552u01 test-run evidence also reported 850 / 161 PASS. These claims are not a fresh CI run by this document's author.
- Native host backends: `gmki91` = KWin X11 (`Operation Mode: X11`); `q552u01` = KWin Wayland (`Operation Mode: Wayland`).
- Runtime viewer completion is independent of GDM, TLS/NLA/server identity, and successful remote user login; every SDL outcome appropriately retained `remote_session=unverified`.

## Acceptance matrix

| Host / compositor | Test / desktop | Operator result | Evidence |
| --- | --- | --- | --- |
| `gmki91`, X11 | Single RDP on desktop 2 | Registration and exact-UUID placement succeeded; later serial entry failed due to repeated preflight (pre-fix) | Window displayed Ubuntu GDM; `managed_slot_reserved_including_missing_history` on revisit |
| `gmki91`, X11 | VNC `under` + Dolphin `panel`, desktop 3 (control) | `2/2`; `SubmitInitialLayout` SUCCEEDED, verified stack | VNC `win-002`, Dolphin `win-003` |
| `gmki91`, X11 | RDP `under` + Konsole `panel`, desktop 12 | **2/2 PASS** | RDP `win-004`, Konsole `win-005`; layout `SUCCEEDED`, order and observed_order equal |
| `gmki91`, X11 | RDP `under` + three Konsole `panel` entries, desktop 13 | **4/4 PASS** | RDP `win-006`, Konsole `win-007`--`win-009`; exact stacking matched |
| `gmki91`, X11 | Two RDP viewers, two free slots | **2/2 PASS** per operator report and screenshot | Two distinct live GDM viewers; `win-010` and `win-011` reported in test context; full console output not included in this record |
| `q552u01`, Wayland | Single RDP viewer, desktop 14 | **1/1 PASS** | `win-001`, UUID `03268e69-8cfd-45fd-bcbe-6e9d6010b096`, presence present, placement succeeded |
| `q552u01`, Wayland | Konsole `panel` + RDP viewer, desktop 13 | **2/2 PASS** | `win-002` and `win-003`, present and placed; screenshot shows terminal and GDM viewer |
| `q552u01`, Wayland | Attempt four-window plan on occupied desktop 13 | **Correctly rejected before launch** | `managed desktop/slot conflict [win-002]`; no unauthorized slot takeover |
| `q552u01`, Wayland | Three Konsoles `panel`, then RDP `under`, desktop 12 | **4/4 PASS** | `win-004`--`win-007`, cohort order corrected by layer rather than launch order |
| `q552u01`, Wayland | Two RDP viewers, desktop 11 | **2/2 PASS** | `win-008` and `win-009`; independent worker PIDs, registered UUIDs, verified stacking |
| `q552u01`, Wayland | Normal titlebar close of desktop-14 viewer | **PASS** | Worker 96618 and direct SDL child 96619 exited; `win-001` retained as `presence=missing`, original slot and UUID retained |

All successful initial-layout results reported `geometry=unchanged` after individually
verified placement; `stacking=verified`, and the recorded `order` equalled
`observed_order`. The tested target desktop was inactive during several
finalizations (`focus_attempted=false`), so this does **not** prove an active-
desktop activation/focus transaction. Screenshots demonstrate appearance, not
broker identity by themselves; the broker output supplies identity evidence.

## Selected operator output (faithful relevant fields; nonessential targets redacted)

### X11: corrected RDP -> Konsole, desktop 12

```text
Launching desktop [12] slot [1]
RDP local outcome: state=completed; registration=registered; placement=succeeded
  managed_id=win-004
  window_uuid=597623bc-dc25-47f5-97ab-371549484f58
  worker_pid=2940326
Launching desktop [12] slot [2]
Registered [win-005] UUID [03398680-dcfe-46fa-baf9-b9eab006958e]
Desktop [12] initial stacking/focus result: (completed)
Initial layout: state=SUCCEEDED, geometry=unchanged, stacking=verified
  order=[597623bc-dc25-47f5-97ab-371549484f58,
         03398680-dcfe-46fa-baf9-b9eab006958e]
  observed_order matches order; focus_attempted=false
Configured layout: [2/2] windows completed ... (completed)
```

### X11: RDP + three Konsole panels, desktop 13

```text
Planned desktop [13] slot [1]: 96,32 1804x972      RDP under
Planned desktop [13] slot [2]: 19,54 531x918       Konsole panel
Planned desktop [13] slot [3]: 588,54 531x918      Konsole panel
Planned desktop [13] slot [4]: 1157,54 531x918     Konsole panel
RDP: win-006, UUID f34643c2-a756-4803-b31a-1585a4272c41
Konsole: win-007, UUID 32c96b36-24a2-4ecf-b1d9-38af314325dd
Konsole: win-008, UUID 9c2466b0-e0ac-4710-8f3a-731c5167973c
Konsole: win-009, UUID e70f9be2-c722-423b-841b-f77d9f899589
Initial layout: state=SUCCEEDED; geometry=unchanged; stacking=verified
  order=[f34643c2-a756-4803-b31a-1585a4272c41,
         32c96b36-24a2-4ecf-b1d9-38af314325dd,
         9c2466b0-e0ac-4710-8f3a-731c5167973c,
         e70f9be2-c722-423b-841b-f77d9f899589]
  observed_order matches order
Configured layout: [4/4] windows completed ... (completed)
```

### Wayland: independently registered single viewer and worker, desktop 14

```text
ListManaged: win-001, desktop=14, slot=1,
  placement=succeeded, presence=present,
  window_uuid=03268e69-8cfd-45fd-bcbe-6e9d6010b096
PID    PPID    PROCESS
96618  1       joetoo_kwin_rdp_launch.py --worker [private runtime directory]
96619  96618   /usr/bin/sdl-freerdp [endpoint and nonsecret arguments omitted]
```

### Wayland: occupied desktop fails closed, then RDP launched *last*

```text
Desktop [13]: planned slots 1..4
joetoo-kwin: managed desktop/slot conflict [win-002]

Desktop [12]: initial stack slots bottom-to-top [4 1 2 3]
Konsole win-004 UUID fa58186a-76f6-431c-a17d-b15bc24aa123
Konsole win-005 UUID 4c8b7db4-4ca5-4890-8f5a-746dea57291c
Konsole win-006 UUID 409e138c-aebb-449d-9ab8-1898adba0942
RDP     win-007 UUID dbf9ea27-a501-4e0b-bbeb-e451048d9ea2
RDP local outcome: state=completed, registration=registered,
  placement=succeeded, remote_session=unverified, worker_pid=111412
Initial layout: state=SUCCEEDED, geometry=unchanged, stacking=verified
  order=[dbf9ea27-a501-4e0b-bbeb-e451048d9ea2,
         fa58186a-76f6-431c-a17d-b15bc24aa123,
         4c8b7db4-4ca5-4890-8f5a-746dea57291c,
         409e138c-aebb-449d-9ab8-1898adba0942]
  observed_order matches order; focus_attempted=false
Configured layout: [4/4] windows completed ... (completed)
```

This establishes layer-based cohort ordering rather than mere launch order:
three Konsole windows launched first, but the last-launched RDP viewer with
`under` layer was verified at the bottom.

### Wayland: two independent RDP viewers, desktop 11

```text
Launching desktop [11] slot [1]
RDP win-008 UUID 08d7180f-d087-4696-9b99-fcf36b42d1a4
  registration=registered; placement=succeeded; worker_pid=115941
Launching desktop [11] slot [2]
RDP win-009 UUID b28b9674-eea4-42c8-a37d-f2446e4289dd
  registration=registered; placement=succeeded; worker_pid=116021
Initial layout: state=SUCCEEDED; geometry=unchanged; stacking=verified
  order=[08d7180f-d087-4696-9b99-fcf36b42d1a4,
         b28b9674-eea4-42c8-a37d-f2446e4289dd]
  observed_order matches order; focus_attempted=false
Configured layout: [2/2] windows completed ... (completed)

ListManaged: win-008 and win-009, both presence=present,
  placement=succeeded, intended=(desktop 11, slots 1 and 2).
PID     PPID    PROCESS
115941  1       joetoo_kwin_rdp_launch.py --worker
115942  115941  /usr/bin/sdl-freerdp
116021  1       joetoo_kwin_rdp_launch.py --worker
116022  116021  /usr/bin/sdl-freerdp
```

### Wayland: natural viewer closure, retained history

Maintainer closed the desktop-14 viewer by its window-manager close button:

```text
$ ps -p 96618,96619 -o pid,ppid,stat,args
    PID    PPID STAT COMMAND

$ qdbus6 org.joetoo.KWinBridge /org/joetoo/KWinBridge \
    org.joetoo.KWinBridge.ListManaged | jq '.windows[] | select(.managed_id == "win-001")'
{
  "intended": {"desktop": 14, "slot": 1},
  "managed_id": "win-001",
  "placement": "succeeded",
  "presence": "missing",
  "request_id": "1565f40f93d34e7bb4151ea5b46c88b5",
  "run_id": null,
  "window_uuid": "03268e69-8cfd-45fd-bcbe-6e9d6010b096"
}
```

`placement=succeeded` here describes the **historical placement transaction**,
not a claim that the window is still present. No automatic slot release or
new-owner adoption occurred. The shell's separate accidental attempt to
execute the bare PID (`96618: command not found`) is unrelated to lifecycle.

## Accepted boundaries and remaining work

**Stage 2 accepted:** serial configured `-o` dispatch, one production SDL
frontend/worker, original D-Bus and child ownership, exact-UUID registration
and verified placement on native X11 and Wayland, shared planner geometry,
per-desktop cohorts including two RDP viewers, and worker lifetime after
frontend return and natural closure. Existing VNC -> Dolphin control succeeded.

**Not established / not included:** remote-user login, TLS/NLA/server identity
security acceptance, active-desktop focus transaction, broker restart
re-adoption, every exceptional cleanup path, or a storage quota on a degraded
supervisor's private log. The degraded supervisor's pidfd `select` may itself
fail; this is a known later-hardening item. Increment 4 Stage 3's finite
five-minute registration/readiness defaults and safe known-clean serial
continuation are **not implemented** in the accepted Stage 2 code; current
defaults remain 120000 ms. Missing-window reservations still block slot reuse.

The maintainer accepted Increment 4 Stage 2 for this scope following these
native checks. The next assignment is separately gated Stage 3; no approval
for source modifications, native execution, commits or deployment is implied
by this evidence file.
