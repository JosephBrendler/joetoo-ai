# Step 1.5c.5d supporting evidence — private-PKI certificate for Ubuntu GNOME Remote Login

**Work observed/reported:** 2026-11-06–07 (America/New_York)  
**RDP server:** `raspiubuntu401` / `raspiubuntu401.brendler`, Ubuntu 26.04.1 Raspberry Pi 4  
**Client verification:** Gentoo hosts `gmki91` and `q552u01`  
**Scope:** **system-level GNOME Remote Desktop Remote Login, TCP/3389 only**. User-level Desktop Sharing on TCP/3390 is a separate service/configuration and is **not claimed updated**.

## Purpose and separation of concerns

The earlier GRD feasibility study documented the system and user GRD listeners with independently generated **self-signed** certificates. This later PKI excursion replaced the **system Remote Login** TLS certificate with a certificate signed by the maintainer's existing private CA chain, then verified server-name/trust behavior on Gentoo clients. It is independent of the SSH host keys regenerated when the Pi was rebuilt and independent of KWin viewer registration. A certificate issued and installed correctly does **not** automatically mean the future configured `joetoo-kwin -o` RDP recipe has a settled production verification policy.

## Certificate issuance and identity

The maintainer reported the following workflow and checked values:

- End-entity **RSA 4096-bit** key generated on `katahdin`; certificate signed using the Brendler Consulting LLC Intermediate CA on `tahawus`. The private CA root/intermediate were already trusted by the relevant Gentoo clients.
- Leaf filename: `raspiubuntu401.brendler.crt`; private key filename: `raspiubuntu401.brendler.key`. **Do not add the private key, CSR private inputs or CA material to the repository.**
- Subject alternative names (SAN): `DNS:raspiubuntu401.brendler` and `DNS:raspiubuntu401`.
- Reported validity: **2026-11-07 through 2030-11-06**.
- Matching public-key SHA-256 digest for leaf certificate and corresponding key: `94a07e1e002a482c80c0f235f2179fefa41e497f314528bd9ec71e3509204070`. This is a **public-key digest**, not a fingerprint of the private key bytes.
- Intermediate issuer reported: **Brendler Consulting LLC Intermediate**.

Exact private-CA key-generation/signing CLI output was **not retained in the reviewed task transcript**. The above issuance hosts, algorithms and extensions are maintainer-reported facts, not an independently re-executed CA audit.

## Deployment on the Ubuntu server

Installed system GRD certificate and key under:

```text
/var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/pki/raspiubuntu401.brendler.crt
/var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/pki/raspiubuntu401.brendler.key
```

The files were owned by the **`gnome-remote-desktop`** service account. Reported modes: certificate **0644**, private key **0600**, private PKI directory **0700**. System GRD was pointed at these paths using:

```bash
sudo grdctl --system rdp set-tls-cert /var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/pki/raspiubuntu401.brendler.crt
sudo grdctl --system rdp set-tls-key /var/lib/gnome-remote-desktop/.local/share/gnome-remote-desktop/pki/raspiubuntu401.brendler.key
sudo systemctl restart gnome-remote-desktop.service
# End of commands

```

These commands are a **description of commands previously used**, not instructions to rerun them during an SDL acceptance gate. The system daemon returned active; logs included `RDP server started`; the expected TCP/3389 service was available.

The configured certificate's observed SHA-256 fingerprint reported by system GRD was:

```text
83:4c:0f:5f:a1:f7:56:23:52:4e:c2:55:db:a3:7f:2a:26:85:cf:f7:19:1b:98:ed:68:66:95:eb:f1:29:79:d8
```

This fingerprint is for the **RDP TLS certificate**. It is not the SSH ED25519 host-key fingerprint, nor the public-key digest given above.

## Client verification — evidence actually observed

1. **gmki91:** OpenSSL verification of the leaf against `/etc/ssl/certs/ca-certificates.crt`, with `-purpose sslserver -verify_hostname raspiubuntu401.brendler`, returned **OK**.
2. **q552u01:** The Gate A transcript independently records `openssl verify ... -purpose sslserver -verify_hostname raspiubuntu401.brendler` returning `/tmp/raspiubuntu401.brendler.crt: OK`. This is a file/chain and hostname preflight, *not* by itself proof of the live certificate presented on a subsequent connection.
3. **gmki91 FreeRDP:**

   ```bash
   xfreerdp /v:raspiubuntu401.brendler:3389 /u:joe \
       /network:auto /dynamic-resolution /cert:deny
   # End of commands

   ```

   The maintainer reached a usable GDM Remote Login screen **without a TLS certificate warning/prompt**. With `/cert:deny`, a certificate-verification failure should be refused instead of interactively ignored; this is direct client interoperability evidence for that invocation.
4. **q552u01 native SDL FreeRDP during Gate C1:** the *independent, manually started Viewer A* used `SDL_VIDEO_DRIVER=wayland sdl-freerdp /v:raspiubuntu401.brendler:3389 /u:joe /network:auto /dynamic-resolution /cert:deny` and reached a graphical GDM screen. This supports client certificate-path interoperability in the specific manual invocation, not an assertion about the development launcher B's unapproved flags.

## Still unverified / out of scope

- **User-level Desktop Sharing (3390):** no CA-signed replacement or `/cert:deny` validation is claimed; the two GRD credential and certificate contexts are separate.
- **Development SDL launcher:** it does not select a final production TLS/NLA/CA/pinning recipe; its output `remote_session=unverified` and broker `connection=not_attempted` are *not* cryptographic measurements. Gate A's OpenSSL result does not substitute for a production launcher security test.
- **Negotiated cryptographic properties:** TLS protocol/cipher, server-side logs for exact session and downgrade behavior, revocation handling, and future recipe behavior were not independently recorded as complete production acceptance checks.
- **SSH key warning:** the `raspiubuntu401` rebuild generated different SSH host keys, explaining the prior changed-host-key warning during `scp`; it is a separate trust domain from RDP TLS. Do not treat the RDP certificate as authenticating SSH.

## Relation to other documentation

This is the **later targeted update** to the original feasibility `README_gnome_remote_desktop.md`, whose earlier statements about self-signed GRD certificates should be interpreted at their historical observation dates. The README's November 4 screenshots are still useful historical evidence. Do not silently replace those images or change the separate user-level 3390 conclusions. This focused report documents the *system 3389 change* without rewriting historical research.

Related records: [Gate A live identity report](step1.5c5d-native-wayland-sdl-gateA-identity-evidence-2026-11-06.md) and [Gate C1 live two-viewer report](step1.5c5d-native-wayland-sdl-gateC1-unrelated-viewer-coexistence-evidence-2026-11-07.md).
