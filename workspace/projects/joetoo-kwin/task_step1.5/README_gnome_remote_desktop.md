# GNOME Remote Desktop on Ubuntu 26.04.1 (Raspberry Pi 4)

**Investigation and reproducibility report — 2026-11-03**  
**Server:** `raspiubuntu401` (Ubuntu 26.04.1, Raspberry Pi 4)  
**Primary client:** `gmki91` (Gentoo/joetoo, KDE Plasma)  
**Destination in joetoo-ai:** `workspace/projects/joetoo-kwin/task_step1.5/`  
**Scope:** GNOME Remote Desktop (GRD) RDP Remote Login and Desktop Sharing; FreeRDP, KRDC, and Remmina clients; connection lifecycle, authentication, certificates, display scaling, and integration implications.

> **Evidence convention.** “Verified” means observed in commands, journals, or screenshots during this exploration. “Likely” denotes a causal inference supported by observations but not independently instrumented. “Not established” records an open question. This report deliberately distinguishes an RDP viewer disconnect from logging out of GNOME. Screenshot filenames are relative to this Markdown file and are included under `screenshots/`.

## Executive summary

**All six server-mode/client combinations eventually worked.** No replacement RDP server (`xrdp`) was required. GNOME Remote Desktop provides two separately configured RDP services:

| Mode | Listener actually observed | Service scope | Required session state | Result |
|---|---|---|---|---|
| **Remote Login** | `raspiubuntu401:3389/TCP` | System-level GRD, coordinated with GDM | `joe` must not have a competing local graphical session; disconnected remote sessions may persist | Verified: GDM greeter, authentication, full GNOME desktop |
| **Desktop Sharing** | `raspiubuntu401:3390/TCP` | `joe`'s user-level GRD | Existing local graphical GNOME session, **unlocked** | Verified: same local desktop, remote input, clipboard |

| Gentoo client | Remote Login 3389 | Desktop Sharing 3390 | Comments |
|---|---|---|---|
| **FreeRDP 3.32.1** (`xfreerdp`) | **Verified** | **Verified** | Most useful command-line diagnostic baseline |
| **KRDC 26.04.3** (`krdc`) | **Verified** | **Verified** | Worked after adjusting security-level configuration; use full screen or scaling |
| **Remmina 1.4.43** (`remmina`) | **Verified** | **Verified** | Saved GUI profiles; reliable with default TLS level; scaling choices matter |

**Two root causes in the early tests were different:**

1. System-level Remote Login listened on 3389 but rejected clients with **`[RDP] Credentials are not set, denying client`**. Credentials were set using `sudo grdctl --system rdp set-credentials`; a system-service restart was performed before the verified successful connection.
2. User-level Desktop Sharing authentication failed until **separate user-level credentials** were set using `grdctl rdp set-credentials` **without** `sudo` or `--system`, followed by a restart of the user service. Subsequent sharing attempts against a *locked* desktop were denied with **`Session creation inhibited`**; unlocking locally allowed the connection.

**Operational limitation:** In this setup a screen lock blocks or disconnects Desktop Sharing. One later Remmina shared-desktop viewer disappeared with the Gentoo Plasma “explode” close animation. It was **likely** caused by the unattended Ubuntu screen locking on the inactivity timer, but no simultaneous server log was captured for that particular later event. Do not misclassify the animated window closure as an RDP graphics crash.

---

## 1. Server configuration and observed state

### 1.1 GRD architecture

The server has **two independent RDP credential contexts and two independent TLS certificate/key pairs**:

- **System-level Remote Login**: `sudo grdctl --system ...`, systemd **system** service `/usr/libexec/gnome-remote-desktop-daemon --system`, GDM graphical login.
- **User-level Desktop Sharing**: `grdctl ...` as `joe`, systemd **user** service `/usr/libexec/gnome-remote-desktop-daemon`, GNOME Shell/Mutter screencast of the existing user session.

These are distinct even when the RDP username happens to be `joe` in both. The RDP password is an initial transport/gateway credential, **not necessarily the Linux account password**. Remote Login subsequently displays GDM and requires a normal graphical user login. Keep the passwords out of this repository.

The relevant installed services were seen as active:

```text
systemctl status gnome-remote-desktop.service
  Active: active (running)
  Exec: /usr/libexec/gnome-remote-desktop-daemon --system

systemctl status gdm.service
  Active: active (running)

systemctl --user status gnome-remote-desktop.service
  user-level GNOME Remote Desktop daemon active
```

`gdm.service` was shown as **active**, although its unit was reported **disabled**. Do not infer from “disabled” that GDM was not operating; investigate its activation arrangement separately before changing it.

### 1.2 Actual port allocation

GRD status reported port 3389 in both configurations, but the user-level service had **`Negotiate port: yes`**, and live sockets showed the actual allocation:

```text
LISTEN ... *:3389 ... gnome-remote-desktop-daemon (system)
LISTEN ... *:3390 ... gnome-remote-desktop-daemon (user)
```

Therefore: **use 3389 for Remote Login and 3390 for Desktop Sharing on this machine**, while verifying listeners with `sudo ss -ltnp` after upgrades or reconfiguration. `grdctl status`'s user-level preferred port of 3389 does **not** mean Desktop Sharing was bound to 3389.

Recheck:

```bash
sudo grdctl --system status       # system Remote Login
              grdctl status       # joe's Desktop Sharing
sudo ss -ltnp | grep -E ':(3389|3390)\b'
```

### 1.3 Credential configuration — the decisive intervention

On `raspiubuntu401`, **system-level Remote Login**:

```bash
sudo grdctl --system rdp set-credentials
# Username: joe
# Password: [entered interactively; not stored in this report]
sudo grdctl --system status
sudo systemctl restart gnome-remote-desktop.service
```

On `raspiubuntu401`, **user-level Desktop Sharing** (as logged-in `joe`):

```bash
grdctl rdp set-credentials
# Username: joe
# Password: [separately entered interactively]
grdctl status
systemctl --user restart gnome-remote-desktop.service
```

**Do not substitute** `sudo grdctl --system rdp set-credentials` for `grdctl rdp set-credentials` when fixing Desktop Sharing. That mistake was actually made during this investigation and initially prolonged the user-level authentication failures.

The system service was restarted before Remote Login first worked. The user service was restarted before Desktop Sharing passed authentication. It was **not established** whether each restart is always required or whether the credentials would be dynamically reloaded under other circumstances.

The GNOME graphical Settings panels had enabled the modes, but the original system journal proved the Remote Login credentials had not become usable. We **did not prove** whether an omitted Save action, a Settings bug, or some other persistence issue caused it. The CLI commands above are the confirmed working remedy, not proof of a specific Settings UI defect.

Systemd occasionally emitted:

```text
Warning: The unit file, source configuration file or drop-ins ... changed on disk.
Run 'systemctl daemon-reload' ...
```

For a system-level unit use `sudo systemctl daemon-reload`; for a user-level unit use `systemctl --user daemon-reload`. These warnings are **separate from** the GRD credential failures.

### 1.4 TLS certificates and existing private PKI

GNOME generated **self-signed**, independent certificates on the Pi, not certificates from the user's PKI. Both identified `Subject: CN = GNOME, C = US` and `Issuer: CN = GNOME, C = US` and produced name-mismatch/self-signed warnings when contacted as `raspiubuntu401`.

| Mode | Certificate path | SHA-256 fingerprint observed |
|---|---|---|
| Remote Login | `/var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/certificates/rdp-tls.crt` | `ee:a7:3c:a3:3b:a9:ec:f5:25:8f:df:76:bb:05:32:8c:15:73:bd:50:57:76:0d:c5:69:c7:69:08:2d:58:93:d9` |
| Desktop Sharing | `/home/joe/.local/share/gnome-remote-desktop/certificates/rdp-tls.crt` | `41:a3:aa:66:f9:f4:e0:16:40:84:ec:f0:6b:87:e6:ae:31:90:fe:dd:7e:c9:fd:95:66:bd:0f:98:c2:c4:05:fd` |

Corresponding key files are `rdp-tls.key` in the same respective directories. **Never commit the private keys.** These fingerprints describe only the observed installation, not a universal Ubuntu default; they can change if regenerated.

On the Pi, compare the live certificate before trusting a client prompt:

```bash
sudo openssl x509 \
  -in /var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/certificates/rdp-tls.crt \
  -noout -subject -issuer -dates -fingerprint -sha256
```

FreeRDP prompted `Do you trust the above certificate? (Y/T/N)`: **Y** to accept and persist, **T** temporarily, **N** reject. Certificates presented on both ports matched their respective `grdctl` fingerprints. Certificate trust was established by out-of-band fingerprint comparison, **not** by PKI validation. A future improvement is to issue properly named certificates with SANs from the existing PKI, configure the matching cert/key through the appropriate system/user `grdctl rdp set-tls-cert` and `set-tls-key` commands, ensure accessible key permissions, and test each mode independently. This PKI migration was **not performed**.

The Pi logged:

```text
Init TPM credentials failed because No TPM device found,
using GKeyFile as fallback.
```

The absence of TPM hardware did not prevent either service from working.

### 1.5 Other server log observations

On the Pi 4, user-level GRD sometimes reported:

```text
Cannot load libcuda.so.1
Cannot load libnvidia-encode.so.1
[HWAccel.Vulkan] Initialization of Vulkan was successful
RDP server started
```

CUDA/NVENC messages were nonfatal; there is no NVIDIA hardware in this test. Do not confuse them with authentication or session-state errors. SSH to `raspiubuntu401` from `gmki91` worked independently throughout the investigation.

---

## 2. FreeRDP on Gentoo — known-good baseline

**Installed:** `net-misc/freerdp-3.32.1`, with USE `client`, `X`, etc., and **`-aad`**. Despite being version 3, the installed executable on `gmki91` is **`/usr/bin/xfreerdp`**, not `xfreerdp3`.

**Remote Login (3389):**

```bash
xfreerdp /v:raspiubuntu401:3389 /u:joe /network:auto /dynamic-resolution
```

**Desktop Sharing (3390):**

```bash
xfreerdp /v:raspiubuntu401:3390 /u:joe /network:auto /dynamic-resolution
```

At interactive prompts: **Domain = blank** (press Enter); **Password = the credentials for the selected GRD mode**. The local DNS suffix `.brendler` is **not** an RDP authentication domain. `joe@raspiubuntu401` belongs in a URI that supports embedded user information; FreeRDP's `/v:` accepts a **host**, so `xfreerdp /v:joe@raspiubuntu401:3389 ...` failed DNS lookup. Specify `/u:joe` separately.

**What `-aad` means here:** Microsoft Azure Active Directory / Entra ID support is unnecessary for this GNOME local-credential/NLA configuration. The warning below does **not** warrant rebuilding FreeRDP with USE `aad`:

```text
[nego_enable_aad]: This build does not support AAD security, disabling.
```

Additional nonfatal warnings included unmapped XKB keycodes `0x08` and `ZEHA 0x5d`, self-signed certificate/name mismatch, and clipboard format response failures (`CB_RESPONSE_FAIL`). Keyboard function was not exhaustively tested, but none of these warnings prevented a working remote GNOME session. Plain-text clipboard **worked both directions** in both Remote Login and Desktop Sharing; that does not establish support for every MIME format or file-copy operation.

**Evidence — FreeRDP remotely logged in:**

![FreeRDP remote GNOME login session](screenshots/02-freerdp-remote-login-session.png)

**Evidence — FreeRDP sharing the existing local desktop:**

![FreeRDP existing desktop sharing, with local session and terminal](screenshots/03-freerdp-desktop-sharing.png)

---

## 3. KRDC on Gentoo — two modes verified

**Installed:** `kde-apps/krdc-26.04.3`, Gentoo USE `rdp`, `ssh`, `vnc`, `wayland`; the `krdc_rdpplugin.so` existed and loaded. `kde-plasma/krdp` was also installed, but **KRDP is a KDE RDP server component, not the client used in these tests**.

Working commands (launch from Konsole):

```bash
krdc 'rdp://joe@raspiubuntu401:3389'  # Remote Login
krdc 'rdp://joe@raspiubuntu401:3390'  # Desktop Sharing
```

In KRDC's dropdown/address workflow, avoid inserting a redundant URL scheme into a field that expects `username@host[:port]`; the first attempt produced **Malformed URL**. A subsequent field showed the `rdp://` prefix percent-encoded inside the address (`rdp%3A%2F%2Fjoe@...`), so we standardized on the explicit, quoted command-line URI above.

### 3.1 Working Host Configuration

| KRDC tab | Tested settings / observation |
|---|---|
| **General** | Resolution **Current Window Size**; acceleration **Use Best Available**; desktop/device scale **Auto**; keyboard **US English**; audio **On This Computer**. `Share Media` displayed `file:///media` (not shown to be a valid redirect target). The “Remember password” checkbox was shown checked in screenshots; KDE Wallet earlier emitted an error, but a causal role was **not established**. |
| **Security** | **NLA enabled**, **TLS enabled**, **RDP enabled**, **Ext disabled** was reported working. **TLS security level 192 bit** was the key observed configuration difference from earlier failures at 256 bit. **NLA alone** at 192 bit also worked. Authentication Package List blank. |
| **Proxy** | Default HTTP dropdown, **server/credentials blank**; no proxy configured. |
| **Gateway** | Transport Auto, **server/domain/credentials blank**; no RDP gateway configured. |
| **SSH tunnel** | **Connect via SSH tunnel unchecked**. |

![KRDC General settings](screenshots/05-krdc-general-settings.png)

![KRDC Security settings from the working-configuration investigation](screenshots/06-krdc-security-settings.png)

**Screenshot qualification:** The Security screenshot was captured when **all four** security boxes were checked, while the final reported working selection was **NLA + TLS + RDP, Ext off**. The later all-four-checkbox screenshot is evidence of the 192-bit setting, **not** an exact image of the final four checkboxes. Do not blindly replicate the image instead of the table.

### 3.2 NLA and TLS: what was actually learned

- GNOME refused **TLS-only with NLA unchecked**. The debug log included `ERRCONNECT_HYBRID_REQUIRED_BY_SERVER`: the server required NLA.
- **NLA-only** worked at the 192-bit KRDC setting. This **does not mean unencrypted RDP**: CredSSP/NLA uses TLS. KRDC's GUI “192 bit” is a security-level configuration, **not proof of the actual negotiated TLS cipher/key size**.
- NLA + TLS + RDP worked at 192 bit. Earlier 256-bit attempts had failed; the tests **suggest** the TLS-level setting mattered but do not establish a precise cryptographic cause or a version-specific defect.
- Do **not** enable legacy RDP security or reduce security requirements outside this isolated troubleshooting experiment without understanding what the client actually negotiates. NLA remains required for the demonstrated server.

Earlier, the debug log also included `QtKeychain read error: Process org.kde.kwalletd6 exited with status 255`, and a default redirect warning for nonexistent `file:///media`. Neither was proven to be the root cause after the 192-bit setting yielded working connections.

**Evidence — KRDC Remote Login (GDM):**

![KRDC presenting the Ubuntu GDM greeter](screenshots/04-krdc-remote-login.png)

**Evidence — KRDC Desktop Sharing (3390):**

![KRDC sharing the Ubuntu local desktop](screenshots/07-krdc-desktop-sharing.png)

**Display usability:** The shared physical desktop was about **1920×1080**, often too large inside KRDC's own toolbar/sidebar. Use KRDC **Full Screen** for practical 1:1 use, or scale the remote display rather than scrolling around an unscaled oversized desktop. These are **viewer presentation** choices, not GNOME authentication controls.

---

## 4. Remmina on Gentoo — both modes verified

**Installed:** `net-misc/remmina-1.4.43`, with RDP support enabled. The working interface differed from KRDC: create/edit a saved connection profile with **`+`** and use **Save and Connect**; saved rows can subsequently be opened from the Remmina main window (including via right-click **Connect**). A profile is not a shell command and does not require a KRDC-style green launch arrow.

### 4.1 Saved profiles

| Field | Remote Login | Desktop Sharing |
|---|---|---|
| Name | `Quick Connect - raspiubuntu401 remote login` (later renamed) | `Quick Connect - raspiubuntu401 shared desktop` (later renamed) |
| Protocol | RDP | RDP |
| Server | `raspiubuntu401:3389` | `raspiubuntu401:3390` |
| Username | `joe` | `joe` |
| Password | System-level GRD RDP password | User-level GRD sharing password |
| Domain | **blank** | **blank** |
| Share folder | blank | blank |
| Security protocol negotiation | **Automatic negotiation** | **Automatic negotiation** |
| TLS Security Level | **Default** | **Default** |
| Quality | Initially Poor/Fastest; later tried Best | Later **Good** |
| Audio output mode | Off | Off |
| SSH tunnel | Not enabled | Not enabled |

The Advanced tab's **Gateway transport type: HTTP** was a dropdown/default with **no gateway server configured**; it does **not** mean the actual direct RDP connection used an HTTP proxy or RD Gateway.

![Remmina Basic profile settings](screenshots/08-remmina-profile-basic.png)

![Remmina Advanced profile settings](screenshots/09-remmina-profile-advanced.png)

![Remmina saved Remote Login and Desktop Sharing profiles](screenshots/13-remmina-saved-profiles.png)

**Do not transfer KRDC's 192-bit setting to Remmina.** Remmina worked with its **Default** TLS Security Level; altering it is not necessary or justified by the observations.

### 4.2 Connections, certificate prompt, and visuals

Remmina Remote Login connected after an initial white/blank delay of about ten seconds, then showed the graphical login and usable GNOME desktop. The user deliberately disconnected **without logging out**, later reconnected to Remote Login, and resumed the existing session. This was direct evidence of remote-session persistence.

![Remmina Remote Login, active GNOME session](screenshots/10-remmina-remote-login.png)

Remmina Desktop Sharing prompted for its **different port-3390 certificate**, whose fingerprint exactly matched the user-level certificate above:

![Remmina certificate acceptance for user-level GRD](screenshots/11-remmina-cert-3390.png)

An attempted Desktop Sharing connection while a persistent Remote Login session was still running failed/retried:

![Remmina reconnect screen when sharing was unavailable](screenshots/12-remmina-connection-retry.png)

After an explicit GNOME **Log Out** from Remote Login, KVM-switching to Ubuntu and logging in **locally**, then switching back to Gentoo, Remmina Desktop Sharing worked immediately:

![Remmina window showing shared physical GNOME desktop](screenshots/14-remmina-desktop-sharing-window.png)

![Remmina scaled-to-window presentation](screenshots/15-remmina-desktop-sharing-scaled.png)

**Scaling:** Sharing inherits the existing local desktop resolution (about 1920×1080). In a smaller window it may crop and show scrollbars; choose Remmina's **scaled mode** or **full-screen**. Scaling a 1920×1080 image to a small viewer makes text small. Remote Login can use the RDP client's virtual display size and is more flexible. Good/Best quality selections were tried, but no comparative bandwidth/latency benchmark was collected; don't label one faster based on this session alone.

---

## 5. GNOME session lifecycle and operational limits

### 5.1 The critical state machine

**Do not confuse these operations:**

- **Close/disconnect viewer:** stops this RDP network connection; **Remote Login's GNOME session can remain running** for later reconnection. This was explicitly verified with Remmina.
- **Log Out inside GNOME:** ends the actual `joe` graphical user session; when sharing that session, the RDP viewer is disconnected because its target vanishes.
- **Lock GNOME's local desktop:** Desktop Sharing is blocked/disconnected. Unlock **at the local console** to permit new sharing connections in the tested environment.
- **Remote Login as `joe` while another `joe` graphical session exists:** GDM may show **Session Already Running** and offer **Cancel** or **Force Stop**. Force Stop terminates the existing graphical session/processes and risks unsaved work.

Operational procedures:

**To switch Remote Login → Desktop Sharing**

1. In the remote GNOME desktop, save work and select **Log Out** (not just close the client window).
2. Use the KVM/physical console to log in locally as `joe`; leave GNOME **unlocked**.
3. From Gentoo, connect to **port 3390** with sharing credentials.

**To switch Desktop Sharing → Remote Login**

1. Save work in the shared physical GNOME session; explicitly **Log Out** within GNOME if ready to abandon that local session.
2. Connect to **port 3389** with system-level RDP credentials, then log in at GDM.
3. Expect a possible several-second dark/charcoal or blank screen during graphical-session initialization. In this investigation one attempt remained dark after Force Stop and was closed; a later attempt reached a usable desktop after ~10 seconds. A persistent dark screen is **not** proof of successful login.

**To temporarily disconnect a Remote Login client while preserving work:** close/disconnect the RDP viewer **without** choosing GNOME Log Out, and reconnect later to **3389**. The continued GNOME login may prevent local `joe` login in the meantime.

### 5.2 Evidence of lock-related sharing denial

One early Desktop Sharing attempt **passed RDP authentication and graphics-channel setup**, then immediately terminated with client:

```text
ERRINFO_LOGOFF_BY_USER (0x0000000C)
```

The **server log at the same time** was more diagnostic:

```text
Nov 03 20:50:23 ... Failed to start remote desktop session:
GDBus.Error:org.freedesktop.DBus.Error.Failed: Session creation inhibited
... ERRINFO_RPC_INITIATED_DISCONNECT [0x00010001]
```

After the user returned to Ubuntu via the KVM, **unlocked the local GNOME desktop**, switched back, and repeated the 3390 connection, sharing succeeded. Taken together, this strongly supports the local screen lock as the reason session creation was inhibited. The exact locking-event log was not shown, so the explanation is **high-confidence inference** rather than direct proof of an exact lock timestamp.

**Later Remmina event:** The shared desktop viewer spontaneously “exploded” (the configured Plasma window-close animation). A timed GNOME screen lock was **likely**, and the behavior is consistent with the earlier verified lock limitation; there is **no matching journal captured for this later occurrence**. Preserve that distinction if investigating a possible Remmina crash.

### 5.3 logind is authoritative, not window-counting

At one point `loginctl list-sessions` showed:

```text
10  joe  ... SSH session
3   joe  ... systemd-user manager
34  gdm-greeter-2 ... systemd-user manager
36  joe  ... remote Wayland graphical user session
c9  gdm-greeter-2 ... local GDM greeter (tty1)
```

`loginctl show-session 36` reported `Service=gdm-password`, `Type=wayland`, `Remote=yes`, `RemoteHost=192.168.62.137`, `State=active`. That snapshot had **one active `joe` graphical user session**, **not two**. An SSH TTY, systemd user manager, greeter and remote GNOME session must not be casually counted as multiple conflicting graphical logins.

Another later local-session snapshot showed `joe` at `seat0` on `tty2` and the user manager, consistent with a local session available for sharing. Session IDs change; never hardcode IDs such as 36 or 37 into automation.

Read-only inspection commands:

```bash
loginctl list-sessions
loginctl show-session SESSION_ID \
  -p Name -p Type -p Class -p Service -p Remote -p RemoteHost -p State -p Active -p TTY -p Leader
who -a
systemd-inhibit --list
ps -eo pid,ppid,user,tty,stat,etime,args --forest | \
  grep -E 'gnome-shell|gnome-session|gdm|gnome-remote-desktop|Xwayland|sshd|systemd --user'
```

A reboot was once reportedly refused with other-session warnings. The subsequently captured `systemd-inhibit --list` included normal sleep inhibitors and an unattended-upgrades shutdown inhibitor; **the precise cause of that earlier reboot refusal was not established**. Avoid indiscriminate `loginctl terminate-user joe`, Force Stop, or forced reboot while work may be unsaved.

![Remote Login detects another existing joe session](screenshots/16-freerdp-session-already-running.png)

---

## 6. What did **not** work / misleading diagnostics

| Observation | Actual diagnosis or outcome |
|---|---|
| `xfreerdp3: command not found` | Gentoo FreeRDP 3.32.1 packaged its X11 client as `xfreerdp`. |
| Initial TCP reset on **3389** despite `grdctl --system status` showing RDP enabled | System journal explicitly reported **`Credentials are not set, denying client`**. Setting system GRD credentials and restarting the system service preceded success. |
| Testing `/u:rdplogin` after configuring username `joe` | Wrong example username suggested during troubleshooting. Use the **username actually configured**, `joe`. |
| `/v:joe@raspiubuntu401:3389` | FreeRDP treated `joe@raspiubuntu401` as hostname and DNS resolution failed; separate `/v:host:port` and `/u:joe`. |
| GNOME self-signed certificate warning | Expected for default generated certs; explicitly compare fingerprint; no PKI integration yet. |
| Desktop Sharing first failed with `ERRCONNECT_LOGON_FAILURE` and server NTLM `MIC verification failed` | User-level GRD credentials had not been correctly reset; using `sudo ... --system` changed the **wrong credential scope**. Use plain `grdctl` as joe. |
| Repeating Desktop Sharing after accepted credentials made viewer briefly appear then disappear | Server said **`Session creation inhibited`**; unlocking physical GNOME session immediately permitted sharing. |
| Entering `.brendler` as RDP Domain | `.brendler` is DNS namespace, not authentication domain. Leave Domain blank. |
| KRDC malformed URL from GUI | Use a correctly parsed address or command-line `krdc 'rdp://joe@host:port'`; avoid double-encoding URI scheme. |
| KRDC TLS-only / NLA disabled | Server rejected negotiation, including **`ERRCONNECT_HYBRID_REQUIRED_BY_SERVER`**; GNOME required NLA. |
| KRDC early 256-bit TLS security-level configuration | Connection failed; at **192-bit level** and NLA selected, both modes worked. Precise cause/cipher **not determined**. |
| KRDC QtKeychain/KWallet and `file:///media` warnings | Observed but not demonstrated to cause failure. Avoid treating them as established root causes. |
| Remmina shared desktop while disconnected Remote Login session still existed | Black screen/reconnection attempts; a persistent `joe` remote graphical session can block starting a local shareable session. Explicit GNOME logout cleared the workflow. |
| Remmina brief white screen before Remote Login | Connection completed after roughly 10 seconds; a transient blank screen alone did not imply failure. |
| Desktop 1920×1080 inside GUI viewer | Oversized/cropped image in nonfullscreen window; use full-screen or scaling, especially for local Desktop Sharing. |
| FreeRDP `-aad` warning | `aad` USE flag unnecessary for local NLA/GNOME credentials; no need to rebuild to remove informational warning. |
| FreeRDP XKB warnings or clipboard `CB_RESPONSE_FAIL` | Nonfatal in these tests. Bidirectional **plain-text** clipboard verified in both modes. |
| FreeRDP `ERRINFO_LOGOFF_BY_USER` | A protocol reason from server; does **not** prove a human clicked Log Out. Investigate GNOME/logind/journal for why it was sent. |

---

## 7. Troubleshooting reference: start with the *right* service

From Ubuntu (`raspiubuntu401`):

```bash
# Shared environment and listeners
sudo ss -ltnp | grep -E ':(3389|3390)\b'
sudo grdctl --system status
grdctl status

# Remote Login: system service
systemctl status gnome-remote-desktop.service --no-pager -l
sudo journalctl -b -u gnome-remote-desktop.service -n 60 --no-pager -l

# Desktop Sharing: user service
systemctl --user status gnome-remote-desktop.service --no-pager -l
journalctl --user -b -u gnome-remote-desktop.service -n 60 --no-pager -l

# GDM and session state
systemctl status gdm.service --no-pager -l
loginctl list-sessions
```

For a specific failure, bracket timestamps, for example:

```bash
journalctl --user -b -u gnome-remote-desktop.service \
  --since '2026-11-03 20:50:00' --until '2026-11-03 20:51:00' \
  --no-pager -l
```

From Gentoo (`gmki91`), start with `xfreerdp` for clearer client logs. When debugging graphical clients, **do not change server credentials, client TLS/security settings, display mode, and login state all at once**. One variable at a time produced the successful diagnosis here.

---

## 8. Relevance to `joetoo-kwin` task_step1.5

This investigation provides a **known-good, non-SSH graphical remote-access baseline** from Gentoo Plasma (`gmki91`) to Ubuntu GNOME (`raspiubuntu401`). For the joetoo-kwin work, retain these distinctions:

1. **RDP connection state ≠ graphical login-session state.** Closing a FreeRDP/KRDC/Remmina window may leave an active Remote Login session and processes behind. A wrapper/window-placement tool must not assume disconnect implies logout or safe process termination.
2. **Graphical session selection matters.** The remote GNOME user can be logged in through GDM as a Wayland session while the physical console is on a separate GDM greeter; Desktop Sharing targets an *existing* local desktop, not an arbitrary detached headless session.
3. **Authentication has layers.** For Remote Login there is RDP NLA credentials, server certificate trust, then GDM Linux-account authentication. For Desktop Sharing there are separate user-scoped RDP credentials and the unlocked local desktop requirement.
4. **Do not infer process ownership from visible windows.** Use `loginctl`, `RemoteHost`, `Service`, `Type`, `Class`, `Leader` and user/system GRD journals. Keep shell/SSH sessions distinct from graphical sessions.
5. **Display behavior differs by mode.** Desktop Sharing mirrors an existing 1920×1080 display, with client-side clipping/scaling/full-screen tradeoffs; Remote Login can use a virtual display and dynamic resolution.
6. **Locked-session behavior needs explicit policy.** A local GNOME lock may expel a Desktop Sharing viewer. Treat this as expected unless server evidence suggests otherwise. Do not automatically disable screen locking or force-stop sessions in automation.
7. **Client failure reasons must remain visible.** Preserve CLI and server journal logs when abstracting FreeRDP/KRDC/Remmina into automation. A Plasma “explode” effect is only the local presentation of a closing viewer window.
8. **Security and secrets.** Do not hardcode RDP credentials into scripts or Git. The two live self-signed certificate fingerprints can be used for provenance but should eventually be replaced with the user’s PKI, with appropriate SANs and trust distribution.

This report concerns **GNOME's server on Ubuntu and clients running on Gentoo**, not KDE's `krdpserver` or the separate joetoo-kwin SSH/Konsole placement proof of concept. The session-lifecycle observations are potentially transferable; the specific GNOME/GDM semantics should not be assumed to describe KWin or SDDM without testing.

## 9. Remaining work / limitations of the evidence

- Verify each mode and listener after a **fresh Raspberry Pi reboot**, including initial Remote Login before any user opens a local desktop. This was not yet reported as a complete post-reboot test.
- Optionally inspect which TLS cipher was negotiated under KRDC's 192-bit security-level setting rather than interpreting the UI label as cipher strength.
- Replace both self-signed GRD certificates with appropriate certificates issued by the existing **private PKI**, after separately testing system and user service identity/trust/permissions. Not yet performed.
- Check client behavior under **GNOME inactivity auto-lock** with synchronized log timestamps. One early failure was diagnosed strongly from `Session creation inhibited` plus unlock/retry; the later spontaneous Remmina expulsion remains inferred.
- Consider connection-quality benchmarks (CPU usage on Pi 4, latency, dynamic-resolution behavior, clipboard formats, audio redirection). No quantitative comparison was performed.
- Verify Remmina/KRDC options after upgrades; screen-grab versions captured here are **26.04.3 KRDC / 1.4.43 Remmina / 3.32.1 FreeRDP**.
- Windows 11 Microsoft Remote Desktop was contemplated but **not tested**.
- Firewall constraints were discussed, but no firewall rule change was documented. RDP should remain limited to trusted LAN/VPN, not exposed directly to the Internet.

## 10. Screenshot index

All screenshots are from the investigation and are bundled in the sibling `screenshots/` directory. Some show interim troubleshooting values; the **written final working configurations above take precedence**.

| File | Evidence |
|---|---|
| `01-freerdp-remote-login-gdm.png` | Initial FreeRDP/GDM login view |
| `02-freerdp-remote-login-session.png` | FreeRDP GNOME Remote Login desktop |
| `03-freerdp-desktop-sharing.png` | FreeRDP active Desktop Sharing |
| `04-krdc-remote-login.png` | KRDC GDM login |
| `05-krdc-general-settings.png` | KRDC General settings |
| `06-krdc-security-settings.png` | KRDC 192-bit security configuration (all four checkboxes in captured interim state) |
| `07-krdc-desktop-sharing.png` | KRDC sharing existing GNOME desktop |
| `08-remmina-profile-basic.png` | Remmina Basic profile |
| `09-remmina-profile-advanced.png` | Remmina Advanced profile |
| `10-remmina-remote-login.png` | Remmina Remote Login |
| `11-remmina-cert-3390.png` | Remmina Desktop Sharing certificate acceptance |
| `12-remmina-connection-retry.png` | Remmina failed sharing attempt/reconnection |
| `13-remmina-saved-profiles.png` | Two distinct Remmina saved connection profiles |
| `14-remmina-desktop-sharing-window.png` | Remmina full-resolution shared display in window |
| `15-remmina-desktop-sharing-scaled.png` | Remmina scaled view |
| `16-freerdp-session-already-running.png` | GDM session conflict and Force Stop warning |
| `17-krdc-initial-malformed-url.png` | Initial KRDC URI parsing failure |

---

**Result:** GRD itself, the two independent credential scopes, both TLS endpoints, both session modes, all three Gentoo clients, and plain-text clipboard in both directions were verified. The most important operational lesson for `joetoo-kwin` is that **viewer lifecycle, authentication, GNOME desktop state, display topology, and actual logind session lifetime are distinct layers**.
