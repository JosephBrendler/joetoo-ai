# Step 1.5c.5d Increment 3 — Native Wayland placement timing and geometry evidence (2026-11-09)

**Status:** Maintainer-run native diagnostic **completed**. This is evidence of a failing placement transaction, **not** Increment 3 placement acceptance. The accepted native Wayland/X11 viewer-registration results and accepted native X11 placement results remain separate. Next reviewed development direction: **Option C — serial RDP placement consolidation**. Option D (concurrent launches and shared RDP/VNC lifecycle) remains future scope.

## Provenance and scope

- **Development repository/branch:** `JosephBrendler/joetoo-ai`, `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`.
- **Documented baseline:** `51ceda403bb81afeb959b5bc143b543445914cd8` updated architecture and active handoff; `6516a31` (`test(joetoo-kwin): trace native Wayland RDP placement lifecycle`) added diagnostic-only source/tests and was signed/pushed by the maintainer. `6516a31` is the implementation revision under test; its full 40-character SHA is not reproduced here because only the short ID was provided.
- **Native execution:** maintainer on `q552u01`, Gentoo, Plasma/KWin **native Wayland**. Separate development host `gmki91` used to publish `6516a31`. Remote RDP endpoint and credential prompts are not needed in this public evidence record.
- **Updated service:** `./tools/restart_joetoo-kwind t` installed the candidate, ran tests, checked consistency and introspection. Subsequently, the maintainer restored private stderr logging and restarted the OpenRC user service. Broker D-Bus PID was `1953662`; `/proc/1953662/fd/2` resolved to the intended user-private stderr log. `ListManaged` initially reported `{ "count": 0, "windows": [] }`.
- **Regression results (maintainer attached transcript):** `Ran 763 tests in 93.331s` — `OK`; JavaScript `tests 161`, `pass 161`, `fail 0`. Installer, service start, and introspection reported success. Expected diagnostic messages added visible stderr noise to the Python test run; test-harness redirection may be tidied without disabling production logging.
- **Capture:** one newly registered viewer and **one** placement attempt with the new diagnostics. Additional earlier informal attempts are not substitutes for this controlled trace.

## Registration and pre-request frame (read-only D-Bus observation)

```json
{
  "managed_id": "win-001",
  "uuid": "e73838fd-5596-49f8-9a4c-33d5c4b3d659",
  "presence": "present",
  "placement": "not_requested",
  "desktops": [1],
  "geometry": {"height":796,"width":1024,"x":448,"y":119}
}
```

- Reservation: desktop **1**, slot **1**.
- Placement requested **once**: desktop **1**, slot **1**, position **(300,160)**, frame **800×600**.
- Placement transaction ID: `05bdfa9c129d482180739eadb5a008ad`; the original managed UUID above was never replaced in the recorded result.
- Operator stderr recorded `shortcut_dispatch` at **7 ms** and `shortcut_returned` at **8 ms** (operator-local monotonic clock). These timestamps are not directly comparable to broker monotonic elapsed time without a shared start offset.

## Broker diagnostic trace — relevant output supplied by maintainer

The following JSON rows transcribe the **broker's fixed-stage diagnostic fields**. Reformatting removes the line wrapping introduced by the terminal/paste; values, request ID, UUID and elapsed times are retained. The original broker lines had prefix `joetoo-kwind: SDL placement diagnostic `.

```jsonl
{"phase":"UNARMED","receipt_elapsed_ms":2,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"operator_authenticated","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"desktop_match":true,"desktops":[1],"frame_available":true,"geometry":{"height":796,"width":1024,"x":448,"y":119},"geometry_match":false,"on_all_desktops":false,"receipt_elapsed_ms":2,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"initial_frame","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"phase":"PENDING","receipt_elapsed_ms":2,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"armed","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"phase":"PENDING","receipt_elapsed_ms":3,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"take_received","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"phase":"RUNNING","receipt_elapsed_ms":4,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"take_accepted","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"after_terminal":false,"phase":"RUNNING","receipt_elapsed_ms":4,"request_id":"05bdfa9c129d482180739eadb5a008ad","result":"VERIFY","sender_matches":true,"stage":"complete_received","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"after_terminal":false,"receipt_elapsed_ms":5,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"resident_uuid_selected","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"after_terminal":false,"receipt_elapsed_ms":5,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"resident_assignment_attempt","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"after_terminal":false,"receipt_elapsed_ms":5,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"resident_assignment_returned","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"receipt_elapsed_ms":5,"request_id":"05bdfa9c129d482180739eadb5a008ad","result":"VERIFY","stage":"complete_accepted","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"phase":"VERIFYING","receipt_elapsed_ms":5,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"verifying_entered","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"deadline_expired":true,"desktop_match":true,"desktops":[1],"frame_available":true,"geometry":{"height":796,"width":1024,"x":448,"y":119},"geometry_match":false,"guard":"guard_deadline","guard_failed":true,"identity_continuity":true,"on_all_desktops":false,"phase":"VERIFYING","receipt_elapsed_ms":15001,"request_id":"05bdfa9c129d482180739eadb5a008ad","requested_outcome":"failed","source_match":true,"stage":"terminal_begin","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"cleanup_uncertain":false,"deadline_expired":true,"desktop_match":true,"desktops":[1],"frame_available":true,"geometry":{"height":796,"width":1024,"x":448,"y":119},"geometry_match":false,"guard":"guard_deadline","guard_failed":true,"on_all_desktops":false,"outcome":"failed","phase":"VERIFYING","receipt_elapsed_ms":15002,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"terminal","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
{"after_terminal":true,"causality":"unproven","desktop_match":true,"desktops":[1],"frame_available":true,"geometry":{"height":796,"width":1024,"x":300,"y":160},"geometry_match":false,"on_all_desktops":false,"present":true,"receipt_elapsed_ms":54343,"request_id":"05bdfa9c129d482180739eadb5a008ad","stage":"post_observation","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
```

The placement command reported the following terminal response after about 15 seconds:

```json
{"managed_id":"win-001","placement":"failed","protocol":1,"reason":"Placement identity/source/owner lost or expired","registration":"registered","remote_session":"unverified","request_id":"05bdfa9c129d482180739eadb5a008ad","window_uuid":"e73838fd-5596-49f8-9a4c-33d5c4b3d659"}
```

## Final read-only broker output

`GetManaged win-001` retained `state=FOUND`, `presence=present`, original UUID, intended desktop 1 / slot 1, `placement=failed`, desktops `[1]`, actual geometry **(300,160) 1024×796**; resource class and desktop file were `com.freerdp.client.sdl3`. The full public output also contained a random generated title marker; it is intentionally omitted from this committed record because it is not needed to establish the result.

`RegistryStatus` reported synchronized observations, `observed_count=6`, `revision=69`, managed count 1, presence counts `{present:1,missing:0,uncertain:0}`, placement transaction `{id:"05bdfa9c129d482180739eadb5a008ad",state:"ERROR"}`, `initial_layout_active=false`, `viewer_cleanup_uncertain=false`. `request_counts.succeeded=1` describes the **registration request**, not successful placement; placement was `failed`.

| Measure | Pre-request | At broker failure (15.002 s) | Post-terminal observation (54.343 s) |
| --- | --- | --- | --- |
| Desktop | `[1]` | `[1]` | `[1]` |
| Position | `(448,119)` | `(448,119)` | `(300,160)` |
| Frame size | `1024×796` | `1024×796` | `1024×796` |
| Requested full frame | `(300,160) 800×600` | not verified | not verified |
| Transaction | not requested | `failed`, `guard_deadline` | remains `failed` |

## Established findings versus unresolved mechanics

**Established by the trace:** The correct registered UUID was claimed and selected, KWin resident recorded an assignment attempt and return, the broker accepted `Complete(VERIFY)`, and the shared transaction entered `VERIFYING` in approximately 5 ms. The terminal failure was **the outer deadline**, `guard_deadline`, at 15.001–15.002 s. The trace positively records `identity_continuity=true`, `source_match=true`, and `cleanup_uncertain=false` at termination. Therefore, the public combined "identity/source/owner lost or expired" reason obscured a **timeout**, not evidence of owner or identity loss in this run.

**Established post-terminal observation:** The same still-present UUID was reported at the requested **position** around 54.343 s after the trace origin, about **39.3 s after the broker had already reported failure**. The size remained `1024×796`, not the requested `800×600`. Passive observation did **not** revive the failed transaction, and no retry was issued during the controlled trace.

**Not established:** The exact time of physical on-screen movement versus time of KWin observation delivery; whether a Wayland configure/commit delay, scheduling delay, client size policy or other mechanism caused the late observation; whether the viewer ever temporarily had the requested frame size; whether movement was directly caused by the recorded assignment rather than other unobserved behavior. The pre-request rectangle makes the change real, but the diagnostic correctly labels causality `unproven`. No authenticated RDP desktop or validated server identity is inferred.

**Related source-design finding, not a separately verified native cause:** The current placement wrapper has an outer 15-second deadline beginning before asynchronous authorization, while the common geometry verifier starts its own 15-second window at submission. The outer guard evaluates first and can mask geometry non-convergence as a generic identity/source/owner-or-expiry failure. The native trace confirms outer deadline expiry during `VERIFYING`; exact late geometry mechanics remain open.

## Disposition and next gate

The maintainer **accepted this controlled diagnostic as sufficient evidence to proceed to Option C design/implementation review**, without another diagnostic-only native reproduction. The accepted RDP viewer selector should be preserved. Option C will consolidate serial placement around established broker/KWin managed-window machinery, with coherent deadline ownership, terminal reporting, and distinct position/size results. The agreed **Option D** goal—multiple pending launches with out-of-order authentication, and common RDP/VNC lifecycle management—remains future work. Do not change the working TigerVNC implementation in Option C.

The next authorized engineering assignment, if separately granted to Codex, is described by the current [HANDOFF](HANDOFF.md). No claim of native placement success or final Increment 3 acceptance is made here.
