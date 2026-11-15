# Increment 5 — production native X11/Wayland RDP and security observations (2026-11-11)

**Provenance:** Maintainer-run native commands, screen observations and screenshots supplied in the 2026-11-11 conversation. No commands were executed by the preparer; outputs below are selected verbatim excerpts or explicitly labeled summaries. This record **supplements**, rather than silently rewrites, [Codex's earlier closure candidate](step1.5c5d-increment5-security-native-closure-candidate.md), which classified these checks as pending before the maintainer performed them. Source branch: `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. The precise new branch HEAD and client package version were not independently recorded in this conversation.

## Maintainer disposition and scope

- **Accepted as native production interoperability evidence:** `gmki91` Plasma X11 and `q552u01` Plasma Wayland each ran `./joetoo-kwin -v -o` with a one-entry `rdp://joe@raspiubuntu401.brendler:3389` private plan; exact-UUID registration, placement, and one-window stacking succeeded; GNOME GDM greeter appeared in the placed viewer. Both used desktop 18, slot 1. No certificate warning was observed on either host. A client NLA credentials prompt was explicitly observed and completed on `gmki91`; the `q552u01` screenshot shows GDM, but independent prompt details were not supplied.
- **Security policy decision, authorized for bounded Codex implementation (2026-11-11):** expose `rdp_security_protocol=nla|negotiate` and `rdp_certificate_policy=strict|prompt`, with **built-in defaults `nla` and `strict`**. The former maps `nla` to exclusive `/sec:nla`, `negotiate` to omission of `/sec:`. The latter maps `strict` to `/cert:deny`, `prompt` to omission of `/cert:`. No `/tls:enforce:1.3` default. Documentation must explain all mappings, explicitly that `negotiate` is NOT `/sec:rdp` and that `/sec:nla` is NOT `/sec:nla:on`. All inputs validated; no arbitrary FreeRDP switch injection. This is an agreed intended behavior, **not implemented or natively retested** in these observations.
- **Not yet demonstrated:** strict production-path certificate rejection with the new mapping, client-side proof of certificate-chain validation uncontaminated by cached exceptions, actual negotiated TLS version/cipher and explicit wire security mode. The last three must remain labeled unobserved unless stronger evidence arises; they need not become open-ended forensic work. Local `remote_session=unverified` remains truthful even after GDM appearance.
- **Separate later packaging item:** replace the current misleading `BUILD` lookup from installed `joetoolkit` with an ebuild-installed `/etc/joetoo-kwin/BUILD` containing `BUILD="${PVR}"` at packaging time; source-checkout fallback remains appropriate. Do not fold this into Increment 5.

## A. Native X11 — gmki91

Session: logged in on `tty1`, X11 started with `startx`; `~/.xinitrc` contains `exec dbus-launch --exit-with-session startplasma-x11`. Thus `loginctl ... Type=tty` and `XDG_SESSION_TYPE=tty` describe the underlying login session, not a failure of native X11. `DISPLAY=:0`, `WAYLAND_DISPLAY=`; actual launcher registration profile `sdl-x11-a1c-v1`.

Initially existing broker windows: `win-001` desktop 3 slot 1, `win-002` desktop 3 slot 2, both present. Test plan used `screen_width=1920`, `screen_height=1080`, target `rdp://joe@raspiubuntu401.brendler:3389`, desktop 18 slot 1, layer `panel`. Dry run `./joetoo-kwin -c -f "$RDP_SECURITY_PLAN"`: one RDP window; planned frame `19,54 1440x918` with terminal-width configuration 75%. The maintainer confirmed `y` at the production `-v -o` prompt.

Selected observed production output:

```text
* Desktop  Slot  Program      Mode  Target                                  Layer  X   Y   Width  Height
* 18       1     sdl-freerdp  rdp   rdp://joe@raspiubuntu401.brendler:3389  panel  19  54  1440   918
* RDP local outcome (remote login unverified): ... "state": "completed" ...
  "placement": {"managed_id": "win-003", "placement": "succeeded", "reason": "verified",
    "window_uuid": "f490d341-0292-4f98-b855-052c5eeb1f3e"}
  "registration": {"profile": "sdl-x11-a1c-v1", "state": "registered",
    "window_uuid": "f490d341-0292-4f98-b855-052c5eeb1f3e"}
  "remote_session": "unverified"
* Desktop [18] initial stacking/focus result: (completed) [ ✅ ]
* Initial layout: ... "state": "SUCCEEDED", "stacking": "verified" ...
* Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
* Configured layout: [1/1] windows completed ... (completed) [ ✅ ]
```

`ListManaged` afterward showed `win-001`, `win-002`, and the new `win-003`; all `presence=present`, with `win-003` intended desktop 18 slot 1, `placement=succeeded`, same exact UUID. The maintainer saw an NLA credential window on desktop 1, entered the RDP password, then saw the Ubuntu GNOME login greeter in the placed desktop-18 SDL viewer (supplied screenshot). **No certificate warning or connection error observed.** GDM screenshot is observational remote-connectivity evidence, not a broker assertion of remote-session authentication.

## B. Native Wayland — q552u01

`XDG_SESSION_TYPE=wayland`, `WAYLAND_DISPLAY=wayland-0`, `DISPLAY=:1`; `kscreen-doctor -o` reported `eDP-1`, `Geometry: 0,0 1920x1080`, scale 1. Prior `ListManaged` contained `win-001` desktop 16 slot 1, `win-002` desktop 16 slot 3, both present. The maintainer ran `git pull --ff-only` before testing; no exact commit hash was provided. The launcher banner showed `joetoo-kwin-1.0.16` because the CLI currently sources the **installed `joetoolkit` BUILD** value, not the `joetoo-kwin` package/source version; this banner is not evidence of an outdated implementation.

The one-entry private plan used the same target and desktop/slot as X11, confirmed matching 1920x1080 resolution, and produced:

```text
* Desktop  Slot  Program      Mode  Target                                  Layer  X   Y   Width  Height
* 18       1     sdl-freerdp  rdp   rdp://joe@raspiubuntu401.brendler:3389  panel  19  54  1670   918
* RDP local outcome (remote login unverified): ... "state": "completed" ...
  "placement": {"managed_id": "win-003", "placement": "succeeded", "reason": "verified",
    "window_uuid": "3676fc92-ce91-40b3-a132-3fc2953888ff"}
  "registration": {"state": "registered", "window_uuid": "3676fc92-ce91-40b3-a132-3fc2953888ff"}
  "remote_session": "unverified"
* Desktop [18] initial stacking/focus result: (completed) [ ✅ ]
* Initial layout: ... "state": "SUCCEEDED", "stacking": "verified" ...
* Entries: completed [1], failed [0], skipped [0]; incomplete desktop cohorts [0]
* Configured layout: [1/1] windows completed ... (completed) [ ✅ ]
```

Afterward `ListManaged` showed `win-001` and `win-002` **still present** on desktop 16, and `win-003` present and placed on desktop 18 slot 1 with UUID `3676fc92-ce91-40b3-a132-3fc2953888ff`. The supplied desktop-18 screenshot showed the Ubuntu GNOME greeter; desktop-16 screenshot showed the two previously arranged managed Konsole windows. The maintainer explicitly reported **no certificate warning**. The `-o` confirmation prompt initially received pasted shell text and then `y`; launch completed successfully, so no failure is attributed to the stray confirmation input.

## C. GNOME Remote Desktop private-PKI server inspection

`raspiubuntu401` Ubuntu system-level Remote Login (not user Desktop Sharing), `sudo grdctl --system status`:

```text
Overall:
        Unit status: active
RDP:
        Status: enabled
        Port: 3389
        Authentication methods: credentials
        TLS certificate: /var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/pki/raspiubuntu401.brendler.crt
        TLS fingerprint: 83:4c:0f:5f:a1:f7:56:23:52:4e:c2:55:db:a3:7f:2a:26:85:cf:f7:19:1b:98:ed:68:66:95:eb:f1:29:79:d8
```

Certificate inspection via `sudo openssl x509 ... -noout -subject -issuer -dates -ext subjectAltName -fingerprint -sha256`: subject `CN=raspiubuntu401.brendler`; issuer `Brendler Consulting LLC Intermediate Certificate`; SANs `DNS:raspiubuntu401.brendler`, `DNS:raspiubuntu401`; validity `Nov 7 2026` through `Nov 6 2030`; SHA-256 fingerprint matches the GRD status above and the [2026-11-07 PKI evidence](step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md). Server-side verification:

```text
sudo openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt \
  -purpose sslserver -verify_hostname raspiubuntu401.brendler \
  /var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/pki/raspiubuntu401.brendler.crt
...raspiubuntu401.brendler.crt: OK
```

Earlier placeholder-path and permission-denied attempts were corrected by the successful command above. This is **server-local** chain/name verification, not proof of the live client trust decision. The maintainer's `gmki91` search under `~/.config/freerdp` and `~/.local/share/freerdp` found no matching cert/known-host file at the tested depth; this does not exclude every FreeRDP exception store. Earlier separately recorded manual `/cert:deny` checks on both Gentoo clients reached GDM, but the current production `-o` launch did **not** supply `/cert:deny` before the new policy change.

## D. Available negotiated-security diagnostics

Initial `q552u01` search under `$XDG_RUNTIME_DIR` found no `stdout.log` because the production source creates **two** different private locations: worker/control `joetoo-rdp-*` under `XDG_RUNTIME_DIR`, and SDL child `/tmp/joetoo-sdl-registration-*/stdout.log` (0700 dir / 0600 file). The corrected `find` found the current file:

```text
2026-11-11 11:27:54.0178595260 /tmp/joetoo-sdl-registration-1_t_2kuf/stdout.log
```

A targeted `grep -Ein 'negotiat|hybrid|nla|tls|security|cipher|certif'` gave selected lines:

```text
[WARN][com.freerdp.core.nego] - [nego_enable_aad]: This build does not support AAD security, disabling.
[WARN][com.freerdp.core.nego] - [nego_enable_aad]: This build does not support AAD security, disabling.
[INFO][com.freerdp.core.redirection] - [rdp_recv_server_redirection_pdu]: ...
  LB_LOAD_BALANCE_INFO|LB_USERNAME|LB_PASSWORD|LB_PASSWORD_IS_PK_ENCRYPTED|
  LB_REDIRECTION_GUID|LB_TARGET_CERTIFICATE ...
```

These demonstrate AAD unsupported and receipt of a server redirection PDU, **not** the exact negotiated security mode, TLS version or cipher. Redirection flags describe fields; they do not establish plaintext password disclosure. Treat raw logs as potentially sensitive. The server's time-bounded negotiation-log grep returned no matching lines. A separate earlier journal excerpt mentioned `Sending server redirection`, `BIO_read retries exceeded` and `ERRCONNECT_CONNECT_TRANSPORT_FAILED` on a timestamped connection; attribution to either successful run was not established and it does not overturn the observed GDM success. No additional logging changes or extra diagnostic runs are authorized on this evidence alone.

## E. Security-policy interpretation and remaining acceptance

| Config variable | Allowed value | Exact FreeRDP mapping |
| --- | --- | --- |
| `rdp_security_protocol` | `nla` (**default**) | `/sec:nla` (exclusive mode selection; **not** `/sec:nla:on`) |
| `rdp_security_protocol` | `negotiate` | No `/sec:` argument; FreeRDP default negotiation (**not** `/sec:rdp`) |
| `rdp_certificate_policy` | `strict` (**default**) | `/cert:deny` (automatic refusal if verification fails) |
| `rdp_certificate_policy` | `prompt` | No `/cert:` argument; FreeRDP default interactive/known-host behavior |

NLA (`/sec:nla`) uses TLS internally; disabling the *alternative* `/sec:tls` RDP mode does not disable TLS within NLA. `/tls:*` configures the TLS machinery, rather than the negotiated RDP security mode; **do not** include `/tls:enforce:1.3` in this Increment 5 default. The default-change decision is explicit but implementation pending. FreeRDP trust exceptions/credential handling must not be misrepresented as security-policy enforcement while the code still uses default options.

**Next bounded Codex task:** implement the two settings through the already accepted Stage 4 configuration layering, output, validation, reference/template and fixed argv mapping, with focused + full regression. No general RDP architecture, remote auth, broker, renderer, placement, or per-target policy redesign. Following code review, run one strict success against the trusted private-CA FQDN and one safe strict certificate-mismatch failure, with exact observed lifecycle recorded. **Important:** SDL may register and be placed before TLS verification fails, so do NOT require zero registration/placement as the only valid negative outcome; require that failure doesn't falsely claim remote authentication, that ownership/cleanup is consistent and no unowned child or unexpected second window is adopted. If a mismatch would require entering secrets or contacting an unverified host, stop and report the prerequisite. Maintainer acceptance and final Step 1.5c.5d closure remain pending these focused checks. Step 1.5d and ebuild work remain separate.

## Source context

- [Increment 5 closure candidate](step1.5c5d-increment5-security-native-closure-candidate.md)
- [Prior GNOME Remote Login PKI evidence](step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md)
- [Increment 4 Stage 4 accepted evidence](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md)
- [Active HANDOFF](HANDOFF.md) and [task index](README.md)
