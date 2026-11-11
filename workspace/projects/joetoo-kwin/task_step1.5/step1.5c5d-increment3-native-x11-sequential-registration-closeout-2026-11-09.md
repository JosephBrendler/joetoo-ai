# Step 1.5c.5d — Increment 3 native X11 sequential-registration fix: acceptance evidence (2026-11-09)

**Decision: NATIVE X11 SEQUENTIAL-REGISTRATION DEFECT CLOSED / ACCEPTED.** This documents the corrected development launcher after the [original X11 placement tests and pre-fix Busy failure](step1.5c5d-increment3-native-x11-placement-2026-11-09.md). **Overall Increment 3 is not yet formally accepted**; native Wayland placement and a frame-sizing disposition remain.

**Repository:** `JosephBrendler/joetoo-ai`, branch `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. **Fix:** maintainer-signed/pushed [`5a2e152ab4f22e21be14c0df2f2cee17e9a6dd8c`](https://github.com/JosephBrendler/joetoo-ai/commit/5a2e152ab4f22e21be14c0df2f2cee17e9a6dd8c). **Host:** `gmki91`, Linux `6.18.62-gentoo-dist-hardened-joetoo`, native Plasma X11. **Endpoint:** `opi6plus01.brendler`, user `joe`. Source: maintainer-provided terminal transcript and two native screenshots on November 9; screenshots remain in conversation, not in the public repository.

## 1. Correction, publication and tests

The earlier failure was caused by two `joetoo-sdl-registration-launch.py` guards that demanded `placement_transaction == {"id":null,"state":"IDLE"}`. They incorrectly classified a completed placement with terminal `OK` and retained ID as busy. Codex's reviewed correction adds shared `placement_available()` used by both guards and permits clean terminal `IDLE`, `OK`, `ERROR` states. Active/unknown state is rejected; `BeginSdlRegistration` retains authoritative SDL cleanup, ownership and slot checks. The fix touched only three files: development launcher, `test_rdp_development_launcher.py`, and `test_rdp_placement.py` (262 insertions, 4 deletions). No broker, resident, geometry or timeout policy changed.

Codex reported 206 focused Python, 691 full Python, 158 JavaScript passes. After signing and pushing `5a2e152`, the maintainer independently ran `./tools/restart_joetoo-kwind t` and supplied this output:

```text
[task/joetoo-kwin-step1.5c5d-managed-rdp-implementation 5a2e152] fix(joetoo-kwin): permit SDL registration after terminal placement
 3 files changed, 262 insertions(+), 4 deletions(-)
# git push: 604109f..5a2e152 task/joetoo-kwin-step1.5c5d-managed-rdp-implementation -> task/joetoo-kwin-step1.5c5d-managed-rdp-implementation
$ ./tools/restart_joetoo-kwind t
Ran 691 tests in 83.932s
OK
ℹ tests 158
ℹ pass 158
ℹ fail 0
# user service stop/reinstall/start: PASS
# installer --check: PASS
# D-Bus introspection: PASS
$ qdbus6 "$bus" "$path" "$bus.ListManaged" | jq .
{"count":0,"windows":[]}
```

No subsequent restart/reload occurred between viewer A and viewer B.

## 2. Viewer A — `software`, desktop 1 slot 2

```bash
python3 tools/joetoo-sdl-registration-launch.py \
    opi6plus01.brendler joe \
    --desktop 1 --slot 2 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer software \
    --rdp-x11-identity-settle-ms 500
```

`ListManaged` while A was open, before placement:

```json
{
  "count": 1,
  "windows": [{
    "connection": "not_attempted",
    "intended": {"desktop":1,"slot":2},
    "managed_id":"win-001","placement":"not_requested","presence":"present",
    "request_id":"26b7779e43bd4a819762f25a26f2c59c","run_id":null,
    "window_uuid":"2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2"
  }]
}
```

```bash
python3 tools/joetoo-sdl-release-placement.py win-001 \
    --confirm --desktop 1 --slot 2 --x 0 --y 0 --width 800 --height 600
```

```json
{
  "managed_id":"win-001","placement":"succeeded","protocol":1,
  "reason":"verified","registration":"registered","remote_session":"unverified",
  "request_id":"c32cddcc7d6848759890ad9210047f5e",
  "window_uuid":"2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2"
}
```

The window visibly moved to the upper left. `RegistryStatus` after placement:

```json
{
  "initial_layout_active":false,"initial_layout_protocol":1,"managed_count":1,
  "observation":{"observed_count":5,"revision":166,"source":"1794246010428-413my7pf1kxj6bufcyx3b4","synchronized":true},
  "placement_transaction":{"id":"c32cddcc7d6848759890ad9210047f5e","state":"OK"},
  "presence_counts":{"missing":0,"present":1,"uncertain":0},"request_count":1,
  "request_counts":{"ambiguous":0,"failed":0,"pending":0,"running":0,"succeeded":1,"timeout":0},
  "viewer_cleanup_uncertain":false,"viewer_protocol":1
}
```

After clicking A's titlebar X, `GetManaged win-001`:

```json
{
  "state":"FOUND","window":{
    "connection":"not_attempted","intended":{"desktop":1,"slot":2},
    "managed_id":"win-001",
    "observation":{
      "caption":"joetoo-rdp-9b1ce5891445651ac2559b866ec5276491707c14b846f319288e775637cc095c",
      "desktop_file":"","desktops":[1],
      "geometry":{"height":804,"width":1032,"x":0,"y":0},
      "on_all_desktops":false,"pid":78277,
      "resource_class":"com.freerdp.client.sdl3"
    },
    "placement":"succeeded","presence":"missing",
    "request_id":"26b7779e43bd4a819762f25a26f2c59c","run_id":null,
    "window_uuid":"2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2"
  }
}
```

`RegistryStatus` after A closed: `initial_layout_active=false`, `managed_count=1`; observation `observed_count=4`, `revision=168`, same `source=1794246010428-413my7pf1kxj6bufcyx3b4`, `synchronized=true`; `placement_transaction` retained `{"id":"c32cddcc7d6848759890ad9210047f5e","state":"OK"}`; `presence_counts={missing:1,present:0,uncertain:0}`, `request_counts={succeeded:1,failed:0,pending:0,running:0,ambiguous:0,timeout:0}`, `viewer_cleanup_uncertain=false`.

## 3. Viewer B — `auto`, desktop 1 slot 3, **same broker**

```bash
python3 tools/joetoo-sdl-registration-launch.py \
    opi6plus01.brendler joe \
    --desktop 1 --slot 3 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer auto \
    --rdp-x11-identity-settle-ms 500
```

This registration **succeeded without a `Broker is busy` rejection and with no broker restart**, while A's terminal `OK` transaction and original managed record were retained.

`ListManaged` while B was open:

```json
{
  "count":2,
  "windows":[
    {"connection":"not_attempted","intended":{"desktop":1,"slot":2},
     "managed_id":"win-001","placement":"succeeded","presence":"missing",
     "request_id":"26b7779e43bd4a819762f25a26f2c59c","run_id":null,
     "window_uuid":"2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2"},
    {"connection":"not_attempted","intended":{"desktop":1,"slot":3},
     "managed_id":"win-002","placement":"not_requested","presence":"present",
     "request_id":"b711c06c658b44d980019bb7dfa08626","run_id":null,
     "window_uuid":"5a893ce2-5cec-4b20-b7d0-01626385df42"}
  ]
}
```

`RegistryStatus` while B was present:

```json
{
  "initial_layout_active":false,"initial_layout_protocol":1,"managed_count":2,
  "observation":{"observed_count":5,"revision":302,"source":"1794246010428-413my7pf1kxj6bufcyx3b4","synchronized":true},
  "placement_transaction":{"id":"c32cddcc7d6848759890ad9210047f5e","state":"OK"},
  "presence_counts":{"missing":1,"present":1,"uncertain":0},"request_count":2,
  "request_counts":{"ambiguous":0,"failed":0,"pending":0,"running":0,"succeeded":2,"timeout":0},
  "viewer_cleanup_uncertain":false,"viewer_protocol":1
}
```

## 4. Viewer B closed — final registry and decision

After clicking B's titlebar X, the final `ListManaged` output was:

```json
{
  "count":2,
  "windows":[
    {"connection":"not_attempted","intended":{"desktop":1,"slot":2},
     "managed_id":"win-001","placement":"succeeded","presence":"missing",
     "request_id":"26b7779e43bd4a819762f25a26f2c59c","run_id":null,
     "window_uuid":"2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2"},
    {"connection":"not_attempted","intended":{"desktop":1,"slot":3},
     "managed_id":"win-002","placement":"not_requested","presence":"missing",
     "request_id":"b711c06c658b44d980019bb7dfa08626","run_id":null,
     "window_uuid":"5a893ce2-5cec-4b20-b7d0-01626385df42"}
  ]
}
```

Final `RegistryStatus`:

```json
{
  "initial_layout_active":false,"initial_layout_protocol":1,"managed_count":2,
  "observation":{"observed_count":4,"revision":304,"source":"1794246010428-413my7pf1kxj6bufcyx3b4","synchronized":true},
  "placement_transaction":{"id":"c32cddcc7d6848759890ad9210047f5e","state":"OK"},
  "presence_counts":{"missing":2,"present":0,"uncertain":0},"request_count":2,
  "request_counts":{"ambiguous":0,"failed":0,"pending":0,"running":0,"succeeded":2,"timeout":0},
  "viewer_cleanup_uncertain":false,"viewer_protocol":1
}
```

**Conclusion: NATIVE ACCEPTANCE PASS; original `Broker is busy` defect CLOSED.** A and B have distinct managed IDs, request IDs and exact UUIDs; original A placement remains `succeeded` with historical `OK` while B successfully registered then closed without placement. Both records retain `presence=missing`; no successor UUID adopted. B's `placement=not_requested` is correct and does not claim that B was placed. A's later frame 1032×804 despite requested 800×600 remains a separate *unresolved geometry issue*. Full Increment 3 closure also requires native Wayland placement.

**Next:** safely sync `q552u01`, validate native-Wayland KWin, run exact-UUID operator placement/closure **without X11-specific flags**, and separately decide the correct SDL client-size/decorated-frame contract. See [HANDOFF](HANDOFF.md) for procedure; keep Increment 4's approved sequential, human-interactive configured `-o` workflow separate.
