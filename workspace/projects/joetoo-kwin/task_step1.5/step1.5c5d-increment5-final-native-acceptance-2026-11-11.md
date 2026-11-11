# Step 1.5c.5d Increment 5 — final strict-security native acceptance (2026-11-11)

**Maintainer disposition (2026-11-11): ACCEPT Increment 5; CLOSE Step 1.5c.5d.** This is the final security-policy acceptance supplement to [the earlier production X11/Wayland observations](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md), [Codex's initial closure assessment](step1.5c5d-increment5-security-native-closure-candidate.md) and [Stage 4 acceptance](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md). The earlier files document the state *before* the strict-policy correction; their historical pending statements are superseded by this dated maintainer acceptance, not retrospectively changed.

## Implementation and test provenance

- Branch: `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. Codex reported starting and ending source HEAD `94d4bea747c1dda618da76a842ac9cfeb3c651f4`, before the 12-file candidate was published. Maintainer subsequently reported pushing the updated files; exact post-push commit SHA was not supplied in the conversation. Check actual Git history for final commit IDs.
- Codex's bounded implementation changed **12 tracked files**, no new files: CLI/configuration display, planner defaults/validation, shared RDP launch argv, RDP target settings/validator, both config templates, configuration reference, and five focused test files. Built-in defaults `rdp_security_protocol=nla` -> **one `/sec:nla`** and `rdp_certificate_policy=strict` -> **one `/cert:deny`**. `negotiate` and `prompt` omit the respective option, not `/sec:rdp`, `-nego`, `/sec:nla:on`, `/cert:ignore`, or arbitrary switches. No TLS version enforcement introduced.
- Headless verification **reported by Codex**, not independently rerun by this document preparer: 185 focused Python PASS; 919 full Python discovery PASS; 161 JavaScript PASS; Bash/Python syntax, targeted ShellCheck and `git diff --check` PASS. Native experiments below were executed by the maintainer, not Codex. No new implementation defect was identified.
- `gmki91` graphical context: Plasma native X11 started via `startx` (`exec dbus-launch --exit-with-session startplasma-x11`). `loginctl Type=tty` refers to underlying text login. Existing registry was emptied as part of maintainer-run service reinstallation/restart before the latest tests; prior historical records should not be conflated with the fresh `win-001`.
- GNOME Remote Desktop server: Ubuntu `raspiubuntu401.brendler:3389` **system-level Remote Login**, certificate issued by Brendler Consulting LLC Intermediate, DNS SAN `raspiubuntu401.brendler`, `raspiubuntu401`; SHA-256 fingerprint `83:4C:0F:5F:A1:F7:56:23:52:4E:C2:55:DB:A3:7F:2A:26:85:CF:F7:19:1B:98:ED:68:66:95:EB:F1:29:79:D8`. GRD `grdctl --system status` and OpenSSL chain/hostname checks had passed earlier. User-level Desktop Sharing on 3390 not part of this test.

## Positive native test — approved hostname, strict policy, gmki91 X11

The maintainer installed/checked the accepted broker via `./tools/restart_joetoo-kwind n` (successful install/check/service restart and D-Bus introspection); `ListManaged` initially `count=0`, registry synchronized, no pending/failed/uncertain operations. A private one-entry plan targeted desktop **19**, slot **1**, layer `panel`, `rdp://joe@raspiubuntu401.brendler:3389`, 1920×1080 display.

`./joetoo-kwin -vc -f "$RDP_STRICT_PLAN"` completed its dry run and showed:

```text
* rdp_security_protocol ........: [ nla ]
* rdp_certificate_policy .......: [ strict ]
* 19  1  sdl-freerdp  rdp  rdp://joe@raspiubuntu401.brendler:3389  panel  19  54  1440  918
```

`./joetoo-kwin -v -o -f "$RDP_STRICT_PLAN"` reported the following selected fields (condensed from maintainer console output; not a single verbatim JSON line):

```text
registration: state=registered, profile=sdl-x11-a1c-v1
placement: managed_id=win-001, placement=succeeded, reason=verified
window_uuid=255d1e14-7890-439d-8a96-fe1bd24266ce
remote_session=unverified
Initial layout: state=SUCCEEDED, stacking=verified
Entries: completed [1], failed [0], skipped [0]
Configured layout: [1/1] windows completed ... (completed)
```

`ListManaged` reported `win-001`, desktop 19 slot 1, `placement=succeeded`, `presence=present`, same UUID. `pgrep -af '/usr/bin/sdl-freerdp'` showed the actual running child PID **2213642** with these material arguments:

```text
/usr/bin/sdl-freerdp /v:raspiubuntu401.brendler:3389 /u:joe
/t:joetoo-rdp-941bbc4c7aca09ce0018f9883f3b0781c104831b7976b5a42f9c9b3faab87e48
/log-level:INFO /log-filters:com.freerdp.client.SDL:DEBUG
/sec:nla /cert:deny /size:1024x768 /smart-sizing:800x600
```

Maintainer screenshot at **2026-11-11 18:13 local time** shows the Ubuntu GDM greeter in the managed viewer on desktop 19. **PASS:** actual strict flags, positive registration/placement, and interoperability with the configured trusted endpoint. KWin still correctly reports `remote_session=unverified`, distinguishing broker observation from remote login authentication.

## Negative native test — IP identity mismatch, automatic certificate refusal

The approved server hostname resolved on gmki91 to **192.168.62.171**. Its previously verified certificate SAN lists the two DNS names above, not this IP. The maintainer first submitted an unexpanded `REPLACE_WITH_VERIFIED_IP` placeholder, correctly rejected by offline plan validation; this was a test-input error, not a negative TLS observation. A corrected private plan targeted **desktop 20, slot 1**, `rdp://joe@192.168.62.171:3389`, `rdp_security_protocol=nla`, `rdp_certificate_policy=strict`. `-vc` validated it and displayed the intended IP target and both strict policy values.

`./joetoo-kwin -v -o -f "$RDP_REFUSAL_PLAN"` reported (selected exact values from the JSON reply):

```text
state=failed; phase=registration; reason=child_exited
failure_reason=child_exited; remote_session=unverified
cleanup_confirmed=true; continuation_eligible=true
cleanup.broker_terminal=true
cleanup.child_reaped=true
cleanup.resources_released=true
cleanup.eligible=true; cleanup.natural_exit=true
cleanup.terminal.state=failed
cleanup.terminal.reason=child_identity_rejected
cleanup.terminal.placement=not_requested
request_id=8ee46cd942594e30830b1b4e9f3e3667
Entries: completed [0], failed [1], skipped [0]
Configured layout: [0/1] windows completed ... (failed)
```

The child's retained private FreeRDP log was located at `/tmp/joetoo-sdl-registration-p817zujg/stdout.log` with timestamp **18:20:13** and PID **2225775**. Critical log excerpts supplied by the maintainer:

```text
WARNING: CERTIFICATE NAME MISMATCH!
The hostname used for this connection (192.168.62.171:3389)
does not match any of the names given in the certificate:
  raspiubuntu401.brendler
  raspiubuntu401
Host key for 192.168.62.171 has changed and you have requested strict (auto-deny) checking.
Host key verification failed.
certificate not trusted, aborting.
ERRCONNECT_TLS_CONNECT_FAILED [0x00020008]
The connection failed at TLS connect.
No certificate stored, automatically denying.
```

The log also included `BIO_new failed for certificate` and a `REMOTE HOST IDENTIFICATION HAS CHANGED` warning for this IP. **Do not interpret the latter as proof of an actual attack or infer a specific prior stored-host entry.** The independently logged name mismatch, strict auto-deny message, TLS rejection and matching fingerprint establish the intended native negative outcome. No operator exception was accepted and the RDP handshake was aborted before a remote authenticated session.

After the negative run, `ListManaged` contained **only** the successful `win-001` desktop 19 viewer; no new desktop 20 registration occurred. `RegistryStatus`: synchronized, `managed_count=1`, `request_count=2`, succeeded=1, failed=1, pending=0, running=0, ambiguous=0, timeout=0, `viewer_cleanup_uncertain=false`, `presence_counts` present=1/uncertain=0, and placement transaction still terminal `OK` for the earlier positive request. `pgrep` still showed the positive trusted SDL child PID 2213642, not the failed child. **PASS:** automatic certificate rejection, owned failure cleanup, known-clean continuation eligibility, and non-disruption of the existing successful viewer. `child_identity_rejected` is the *broker's terminal classification*, **not** the FreeRDP certificate error; the client log separately proves the certificate mismatch.

## Acceptance matrix and boundaries

| Increment 5 criterion | Disposition | Evidence |
| --- | --- | --- |
| Layered selectable security settings and readable mappings | **PASS** | Codex patch, config manual/templates and 185/919/161 reported test outcomes |
| Exclusive NLA + automatic deny in real production argv | **PASS** | Native positive child `/sec:nla /cert:deny` |
| Valid trusted FQDN under strict policy | **PASS** | GDM screenshot, `win-001`, UUID/placement, client args |
| Wrong certificate identity fails closed without exception | **PASS** | FreeRDP `CERTIFICATE NAME MISMATCH`, `strict (auto-deny)`, `ERRCONNECT_TLS_CONNECT_FAILED` |
| Failed child/broker cleanup and continuing trusted viewer | **PASS** | `cleanup_confirmed=true`, no uncertain resources, existing `win-001` remains |
| Earlier native X11/Wayland registration, placement and stacking | **ACCEPTED previously** | Prior Increment 1–4 and pre-policy Increment 5 native evidence |

**Accepted limits, not new blockers:** no universal certificate-error-type coverage, no independently captured TLS version/cipher, no claim that KWin validates GNOME remote login authentication, and no retest of every backend after the policy change. The private client log and credential entries should stay private; publish only sanitized excerpts. Existing X11 500-ms temporary-window heuristic limit and `remote_session=unverified` remain. `joetoo-kwin` build banner currently takes `joetoolkit` BUILD; separate future ebuild must install `/etc/joetoo-kwin/BUILD` sourced from `$PVR`. No `/tls:enforce:1.3`, user Desktop Sharing 3390, alternate clients, broader integration or packaging accepted here.

**Final maintainer decision:** On **2026-11-11**, maintainer explicitly stated: “I accept Increment 5 and closing Step 1.5c.5d.” No further implementation or native acceptance work is pending for this milestone. Next work is branch PR/merge review into `main`, then **Step 1.5d integrated regression / remaining Step 1.5 scope** through a separately authorized task. Official Gentoo packaging is separate, later work in the protected `joetoo`/`joetoo-upstream` repositories and is reserved for the human maintainer under their applicable policies.
