# Step 1.5c.5d Increment 1 — Gate C1: unrelated SDL viewer coexistence

**Native observation date:** 2026-11-07, local America/New_York  
**Operator:** Maintainer, three local Konsoles A/B/C on `q552u01` (Gentoo, KWin Plasma native Wayland)  
**Scope:** Existing *unmanaged* SDL FreeRDP viewer A remains open while development launcher registers distinct viewer B, **without placement**  
**Disposition:** **PASS for C1 unrelated-viewer identity and lifecycle isolation**, not full Increment 1 acceptance.

## Why this test matters

Both viewers use `com.freerdp.client.sdl3`. The broker may register **only the one it launched and positively identified**, not whichever same-class SDL viewer already exists. The test additionally checks that stopping B does not close A and that B's own registered UUID becomes a historical `missing` record, rather than being retargeted to A.

## Preflight interruption: completed `mw` move transaction

An *earlier, abandoned* C1 preflight produced `placement_transaction={"id":"1b6e2c032b9449c29c9a1f2b5b300686","state":"OK"}`, with no managed windows or SDL process. The maintainer identified recent `mw r` and `mw l` Konsole-window repositioning. Source inspection showed that broker placement retains a completed `OK` result, while the **development launcher** requires exactly `{"id":null,"state":"IDLE"}` in its own preflight. This is a launcher-preflight limitation/possible follow-up design improvement, **not** a failed viewer-isolation run and not justification for midtest restarts.

Original preflight evidence was retained under `/tmp/joetoo-gateC.BttmIFBw` and `/tmp/joetoo-gateC.Ic6PpMob`. No viewer was launched in those attempts.

With **no SDL viewer running**, the maintainer then ran `./tools/restart_joetoo-kwind notest` as **preparation only**. Installation/check and service start succeeded. The wrapper's immediate D-Bus introspection printed `Service 'org.joetoo.KWinBridge' does not exist` at that instant; direct broker queries immediately afterward succeeded. Treat the immediate-introspection failure as an unresolved wrapper/service-readiness issue, not proof of daemon absence or C1 failure. **There was no restart after the following C1 baseline.** No `mw` move was used during active C1.

## Actual C1 baseline

Evidence directory `/tmp/joetoo-gateC.GKCfVn5d`.

- Session `wayland`; OpenRC user service `started`.
- Synchronized inventory, observation source `1794030392638-uhwrbnhy27vazpm5rqx9r7`, revision **13**, observed count **5**.
- `placement_transaction={"id":null,"state":"IDLE"}`; no active layout; no cleanup uncertainty.
- Zero pending/running requests and `request_count=0`; `managed_count=0`, `ListManaged` empty.
- No SDL FreeRDP process running before Viewer A.
- Automated preflight said `PASS: Gate C broker baseline ready` and `PASS: Desktop 1, slot 2 available`.

## Viewer A: manually launched, never registered

**Konsole A:**

```bash
SDL_VIDEO_DRIVER=wayland sdl-freerdp \
    /v:raspiubuntu401.brendler:3389 \
    /u:joe \
    /network:auto \
    /dynamic-resolution \
    /cert:deny
# End of commands

```

Viewer A reached a visible Ubuntu graphical GDM login screen. Konsole C independently observed:

| Property | Viewer A |
| --- | --- |
| PID | `945458` |
| KWin UUID | `87a676e9-5061-4f12-a839-e8041fa429f3` |
| Caption | `FreeRDP: raspiubuntu401.brendler` |
| Class / desktop file | `com.freerdp.client.sdl3` |
| Managed registry after A launch | `count=0` |

This was an **ordinary** SDL instance with no `joetoo-rdp-…` marker. The `-cert:deny` command is independent supporting evidence of a usable client connection with strict certificate refusal; it does **not** prove the managed launcher B uses that same flag.

## Viewer B: launcher-owned, positively registered

**Konsole B, while Viewer A remained open:**

```bash
python3 tools/joetoo-sdl-registration-launch.py \
    raspiubuntu401.brendler joe \
    --desktop 1 \
    --slot 2 \
    --rdp-registration-timeout-ms 300000
# End of commands

```

Observed launcher output:

```json
{"evidence_directory":"/tmp/joetoo-sdl-registration-eyiigxye","placement":"not_requested"}
{"child_pid":947240,"child_start":10666699,"request_id":"77b9da00b5ae4468aded64885c380827","placement":"not_requested","remote_session":"unverified"}
{"managed_id":"win-001","placement":"not_requested","protocol":1,"reason":"registered","remote_session":"unverified","request_id":"77b9da00b5ae4468aded64885c380827","state":"registered","window_uuid":"f5ee581a-4b4b-4948-9721-526e24f3afcd"}
```

| Property | Viewer B |
| --- | --- |
| PID / PPID | `947240` / `947239`, live `sdl-freerdp` |
| KWin UUID | `f5ee581a-4b4b-4948-9721-526e24f3afcd` |
| Broker managed ID | `win-001` |
| Request | `77b9da00b5ae4468aded64885c380827` |
| Exact KWin caption marker | `joetoo-rdp-b3a9f1a19cdf214d20eae564213054932640889c8ca7ff1cfbc82b92280436d2` |
| Application / desktop file | `com.freerdp.client.sdl3` |
| Intended destination | desktop `1`, slot `2` |
| Live record | `state=FOUND`, `presence=present`, `placement=not_requested`, `connection=not_attempted` |
| Live broker observed geometry | x `468.6022985983466`, y `178.67037051189897`, width `1024`, height `796` |

The screenshot captured *both actual windows* simultaneously (A generic title in back, B marked title in front):

![Native Wayland Gate C1: unrelated Viewer A and launch-owned Viewer B](screenshots/26-sdl-native-wayland-gateC1-unrelated-and-managed-2026-11-07.png)

**Konsole C while both live:** two distinct PIDs (`945458`, `947240`) and distinct UUIDs; both `com.freerdp.client.sdl3`, but only B had the exact marker and only B appeared in the managed registry. The scripted comparisons printed `PASS: Viewer A and B have different UUIDs` and `PASS: Broker registered Viewer B correctly`.

At that point `RegistryStatus` showed `managed_count=1`, `succeeded=1`, `pending=running=0`, observation synchronized/source unchanged, revision **119**, `placement_transaction=IDLE`, `viewer_cleanup_uncertain=false`.

## Viewer B closed first; Viewer A survived

The maintainer closed B by its window control, leaving A open. B's launcher returned:

```json
{"child_exit":131,"registration":"registered","remote_session":"unverified","placement":"not_requested"}
```

Launcher process exit status **0**: completed its own *registration/supervision* objective. SDL child exit **131** is a separate FreeRDP termination classification; earlier Gate A log evidence shows a local close request can precede this classification. Do not treat it as remote-login success or failed registration.

After closing B, Konsole C verified:

- PID `945458` (A) **still alive** and UUID `87a676e9-5061-4f12-a839-e8041fa429f3` **still observed in KWin**.
- PID `947240` (B) **gone**.
- `ListManaged` **retained only B's** `win-001`, original UUID `f5ee581a-4b4b-4948-9721-526e24f3afcd`, now `presence=missing`; never retargeted to A.
- Observation remained synchronized with same source and revision **255**; `managed_count=1`, `missing=1`, `succeeded=1`, `pending=running=0`, placement `IDLE`.

After separately closing A, `pgrep -a -u "$USER" -x sdl-freerdp` found **no SDL process**. Final `RegistryStatus`: same source, synchronized, revision **259**, `managed_count=1`, missing=1, succeeded=1, pending=running=0, placement IDLE, cleanup uncertainty false. Final `ListManaged` still held B's original `win-001` UUID.

## Disposition, scope and follow-up

**PASS C1:** No class-only/unrelated-viewer adoption; correct launch-owned PID/UUID; marker and managed identity distinguished; no placement; no unrelated-child termination; retained historical identity of B after close; no leaked SDL process. No C1 repetition indicated by this evidence.

**Not tested here:** Preservation of **a different, previously registered managed record** while a *second* managed viewer registers at another slot. The baseline registry was empty (`managed_count=0`), and Viewer A was deliberately unmanaged. This is the historical-record isolation question discussed in HANDOFF, not a deficiency in the actual C1 result. Current SDL-focused headless tests cover slot collision, duplicate UUID, unrelated preexisting viewer, and missing-on-exit; they do not appear to supply a single integrated two-successful-registrations history test. Recommend a focused headless regression review/addition **before** deciding whether one more native case is justified.

Unredacted child logs under `/tmp/joetoo-sdl-registration-eyiigxye` remain private and outside Git; no server credentials are recorded here. No source, placement, production-security or X11 implementation changes are authorized by this report.
