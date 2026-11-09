# Step 1.5c.5d — Native X11 SDL registration and post-close lifecycle evidence (2026-11-08)

**Status:** Maintainer-supplied native evidence supporting acceptance of the current **registration-only `auto` candidate** on `gmki91`. The maintainer additionally accepts the current Codex implementation candidate for further development. **Not** evidence of managed `software` native acceptance, automatic placement, production TLS/NLA/certificate policy, or universal X11 selector correctness. This record is evidence, **not a new permission to edit, install or execute**; see [HANDOFF](HANDOFF.md).

**Code baseline at evidence handoff:** pushed branch `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`, HEAD `13e532c5d80c5beef69451f77d44dd4b36e1b50d` as verified on 2026-11-08. That push includes the eight Codex/maintainer code/test changes, including the diagnostic test-fixture filename correction and the native-X11 OpenRC environment-guard correction. The native test happened against the locally installed broker; commit SHA identifies the subsequent published code, not a byte-for-byte installed-environment attestation.

## 1. Build and headless test evidence (maintainer output)

The maintainer first corrected the obsolete diagnostic test fixture filename (`rdp_identity-security_proof.sh` -> `rdp_identity-security_proof`). The initial full suite had reported 642 tests with 19 failures and one error, all in that fixture class; the correction yielded **642 tests OK**. After Codex removed the unjustified `XDG_SESSION_TYPE == x11` broker guard, the maintainer ran the project installer/restart/test workflow and supplied these terminal result excerpts:

```text
./tools/restart_joetoo-kwind test
... 
Installed ten user-owned joetoo-kwind files. No service was started.
Update done; result: (success!)
Unloading joetoo-bridge KWin script (true)
Starting joetoo-kwind service
Running python unit tests
----------------------------------------------------------------------
Ran 644 tests in 90.480s

OK
python tests done; result: (success!)
Running javascript unit tests
...
ℹ tests 145
ℹ pass 145
ℹ fail 0
javascript tests done; result: (success!)
...
Checks done; result: (success!)
dbus introspection done; result: (success!)
```

These are **maintainer-pasted terminal excerpts**. The full verbose JavaScript listing and all individual Python test lines are not repeated here. The earlier `validate_scripts` warnings about non-script `.conf`/`.js` files are acknowledged as tool behavior, not defects attributed to the RDP code.

## 2. Earlier native handshake failure and integration correction

The initial `auto` managed launcher attempts printed `evidence_directory` followed by `SDL development launcher FAILED: DBusException`, **before** a `child_pid`, `request_id`, or RDP viewer was reported. Both OpenRC supervisor and broker environments showed `XDG_SESSION_TYPE=tty`, although the desktop itself used native KWin X11. The newly added broker guard incorrectly required `os.environ.get('XDG_SESSION_TYPE') == 'x11'`. It was later removed in Codex's updated code with the comment that OpenRC may inherit a login TTY label; profile selection remains explicit and the **actual bound SDL child/backend** remains strictly verified. Reconfiguring OpenRC to assert `x11` is **not** an accepted prerequisite.

The subsequent successful native launcher command used the intended profile and settings:

```bash
python3 tools/joetoo-sdl-registration-launch.py raspiubuntu401 joe \
    --desktop 1 --slot 2 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer auto \
    --rdp-x11-identity-settle-ms 500
# End of commands

```

`--desktop 1 --slot 2` was free at those launches; a prior **missing** registry record can reserve a slot, so do not assume reuse is always permitted without checking.

## 3. First successful managed registration (screenshot evidence)

The maintainer supplied screenshots of the **actual local SDL FreeRDP viewer** on native Plasma/KWin X11 displaying Ubuntu GDM, then a usable authenticated remote GNOME desktop, with the console visible after moving the window manually. The console visibly reported:

```text
child_pid: 1584992
profile: sdl-x11-a1c-v1
rdp_x11_renderer: auto
rdp_x11_identity_settle_ms: 500
state: registered
reason: registered
managed_id: win-001
window_uuid: b817ee63-c8ba-4d83-b08d-290b3a4961d4
placement: not_requested
remote_session: unverified
```

**Interpretation:** The local broker registered an exact KWin UUID. The visible GNOME desktop is a human visual observation, **not a broker assertion of authentication**; `remote_session=unverified` is intentional. The maintainer manually moved the window, which does not constitute broker-authorized placement. The screenshots are **not included in this public evidence file** because they contain unrelated desktop content. Source material provided in the conversation included `console_output_detail.png`, `image(9).png`, and `image(10).png` (names as mounted for review); do not assume those local chat attachment names are durable Git artifacts.

## 4. Second native run — full registry before/after evidence

The maintainer restarted the native test to capture actual registry state while the viewer was open and again after clicking its titlebar X. These identifiers are **from the second run**, not the first one:

| Field | While viewer open | After titlebar X |
| --- | --- | --- |
| `managed_id` | `win-001` | `win-001` |
| KWin UUID | `0f2cd5ff-2b83-4301-adae-d503b0bba61c` | **same** |
| PID in recorded observation | `1607666` | Same historical observation; not proof process remains alive |
| `presence` | `present` | `missing` |
| `placement` | `not_requested` | `not_requested` |
| Intended desktop / slot | `1` / `2` | `1` / `2` |
| Registry managed count | `1` | `1` |

Before closure, `RegistryStatus` reported `observation.synchronized=true`, `placement_transaction.state=IDLE`, `request_counts.succeeded=1`, `failed=0`, `ambiguous=0`, `timeout=0`, `presence_counts.present=1`, `missing=0`, `uncertain=0`, `viewer_cleanup_uncertain=false`. Post-closure `GetManaged` and `ListManaged` retained the same managed ID and UUID with `presence=missing`. **No alternate UUID was adopted.** The screenshot shows a registered viewer and the open remote desktop. The terminal output that would confirm the launcher process's final exit code after closure was **not provided**; do not manufacture one.

**Sanitized transcript from the attached `temp` file follows.** The original attached source file's SHA-256 is `6596e5a14457824fa145242374c1ce8947a9129ee32906dc52f4919a035fab90`; the `caption` title token and observer source string are redacted from this public-ready reproduction. Other identifier fields are retained to support before/after UUID correlation.

```text
gmki91$ qdbus6 "$bus" "$path" "$bus.ListManaged" | jq .
{
  "count": 1,
  "windows": [
    {
      "connection": "not_attempted",
      "intended": {
        "desktop": 1,
        "slot": 2
      },
      "managed_id": "win-001",
      "placement": "not_requested",
      "presence": "present",
      "request_id": "d55a7f5ebd544b53a301361e9e643ae4",
      "run_id": null,
      "window_uuid": "0f2cd5ff-2b83-4301-adae-d503b0bba61c"
    }
  ]
}
gmki91$ qdbus6 "$bus" "$path" "$bus.GetManaged" win-001 | jq .
{
  "state": "FOUND",
  "window": {
    "connection": "not_attempted",
    "intended": {
      "desktop": 1,
      "slot": 2
    },
    "managed_id": "win-001",
    "observation": {
      "caption": "<redacted ephemeral title marker>",
      "desktop_file": "",
      "desktops": [
        1
      ],
      "geometry": {
        "height": 804,
        "width": 1032,
        "x": 86,
        "y": 0
      },
      "on_all_desktops": false,
      "pid": 1607666,
      "resource_class": "com.freerdp.client.sdl3"
    },
    "placement": "not_requested",
    "presence": "present",
    "request_id": "d55a7f5ebd544b53a301361e9e643ae4",
    "run_id": null,
    "window_uuid": "0f2cd5ff-2b83-4301-adae-d503b0bba61c"
  }
}
gmki91$ qdbus6 "$bus" "$path" "$bus.RegistryStatus" | jq .
{
  "initial_layout_active": false,
  "initial_layout_protocol": 1,
  "managed_count": 1,
  "observation": {
    "observed_count": 27,
    "revision": 176,
    "source": "<redacted observation source>",
    "synchronized": true
  },
  "placement_transaction": {
    "id": null,
    "state": "IDLE"
  },
  "presence_counts": {
    "missing": 0,
    "present": 1,
    "uncertain": 0
  },
  "request_count": 1,
  "request_counts": {
    "ambiguous": 0,
    "failed": 0,
    "pending": 0,
    "running": 0,
    "succeeded": 1,
    "timeout": 0
  },
  "viewer_cleanup_uncertain": false,
  "viewer_protocol": 1
}
gmki91$ # window closed with titlebar X
gmki91$ qdbus6 "$bus" "$path" "$bus.ListManaged" | jq .
{
  "count": 1,
  "windows": [
    {
      "connection": "not_attempted",
      "intended": {
        "desktop": 1,
        "slot": 2
      },
      "managed_id": "win-001",
      "placement": "not_requested",
      "presence": "missing",
      "request_id": "d55a7f5ebd544b53a301361e9e643ae4",
      "run_id": null,
      "window_uuid": "0f2cd5ff-2b83-4301-adae-d503b0bba61c"
    }
  ]
}
gmki91$ qdbus6 "$bus" "$path" "$bus.GetManaged" win-001 | jq .
{
  "state": "FOUND",
  "window": {
    "connection": "not_attempted",
    "intended": {
      "desktop": 1,
      "slot": 2
    },
    "managed_id": "win-001",
    "observation": {
      "caption": "<redacted ephemeral title marker>",
      "desktop_file": "",
      "desktops": [
        1
      ],
      "geometry": {
        "height": 804,
        "width": 1032,
        "x": 86,
        "y": 0
      },
      "on_all_desktops": false,
      "pid": 1607666,
      "resource_class": "com.freerdp.client.sdl3"
    },
    "placement": "not_requested",
    "presence": "missing",
    "request_id": "d55a7f5ebd544b53a301361e9e643ae4",
    "run_id": null,
    "window_uuid": "0f2cd5ff-2b83-4301-adae-d503b0bba61c"
  }
}
gmki91$
```

## 5. Decision, limitations and next verification

**Accepted for forward development:** Native X11 stock FreeRDP managed UUID registration with `auto` and the 500 ms heuristic has now worked in **two observed launches**, with detailed before/after registry retention established for the second. The entire regression suite subsequently passed. It is reasonable to **accept the code candidate and advance development** rather than repeat renderer feasibility analysis.

**Not yet fully accepted:** Managed native X11 `software` mode has headless coverage and earlier **diagnostic** feasibility, but no matching managed-registration native before/after acceptance transcript. An independent maintainer-operated registration-only software-mode run remains needed before closing Increment 2 across both renderer choices. Repeatability and performance were not measured statistically. A marked temporary X11 viewer could remain live for 600 ms and be wrongly registered at the 500 ms threshold; the implementation intentionally never reassigns a registered UUID. This is a documented **best-effort legacy heuristic**, not a proof of renderer-completion or universal viewer role.

**Next code step:** Explicit **operator-authorized release of a previously registered UUID for placement**, with separate headless implementation and native approval. No automatic placement or configured `-o -f` is implied. Refer to [active HANDOFF](HANDOFF.md).
