# Step 1.5c.5d — Native X11 SDL registration and post-close lifecycle evidence (2026-11-08)

**Status: INCREMENT 2 ACCEPTED by the maintainer** after native X11 managed-registration tests of both `auto` and `software` renderers, including present→missing exact-UUID retention following window closure. This is registration-only acceptance, **not** placement, production TLS/NLA acceptance, a universal X11 role selector or proof of remote-session status. The previously published longer version of this file preserves the full sanitized `auto` registry transcript in Git history; this revision retains its substantive results and adds the final `software` proof.

**Repository/branch:** `JosephBrendler/joetoo-ai`, `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. Code baseline first published at `13e532c5d80c5beef69451f77d44dd4b36e1b50d`, reviewed with subsequent documentation through branch HEAD `ab444365f6a3e33626f5fe47cf17d92adb4355ce`. Native observations are maintainer-provided and do not attest byte-for-byte installed contents.

## 1. Headless and integration evidence

After correcting an obsolete diagnostic fixture reference (`rdp_identity-security_proof.sh` → `rdp_identity-security_proof`) and removing an unjustified broker guard requiring `XDG_SESSION_TYPE=x11`, the maintainer ran `./tools/restart_joetoo-kwind test` on `gmki91`. The full results supplied were **644 Python tests OK; 145 JavaScript tests passed / 0 failed**; installer update/check and expected SDL D-Bus introspection succeeded. The OpenRC service environment may label its originating login as `tty` even when KWin is actually native X11; the SDL child/backend still receives strict independent proof. These are pasted native test excerpts rather than CI attestation, and are not tests of future placement code.

The stock-client profile is `sdl-x11-a1c-v1`, configurable child-local `rdp_x11_renderer=auto|software`, plus `rdp_x11_identity_settle_ms` (tested at 500 ms). Neither profile performs placement. The prior A2 FreeRDP source-patching alternative was abandoned. The known counterexample remains: a positively qualified *temporary* viewer surviving 600 ms can be wrongly registered after a 500 ms dwell; later replacement must never silently be adopted. This is a documented best-effort identity heuristic.

## 2. Native `auto` renderer registration

On native Plasma X11 `gmki91`, the maintainer used:

```bash
python3 tools/joetoo-sdl-registration-launch.py raspiubuntu401 joe \
    --desktop 1 --slot 2 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer auto \
    --rdp-x11-identity-settle-ms 500
# End of commands

```

First successful managed run: `child_pid=1584992`, `managed_id=win-001`, UUID `b817ee63-c8ba-4d83-b08d-290b3a4961d4`, `state=registered`, `placement=not_requested`. Screenshots showed the Ubuntu GDM greeter and later a usable GNOME session. Moving the window manually was not broker placement; the broker reported the remote session as unverified.

A second managed run registered `child_pid=1607666`, `managed_id=win-001`, UUID `0f2cd5ff-2b83-4301-adae-d503b0bba61c`, `placement=not_requested`. While open, `GetManaged` showed `presence=present`, `RegistryStatus` synchronized, one successful registration, `failed=0` and placement `IDLE`. After titlebar-X closure, the **same** managed ID and UUID remained in `GetManaged` and `ListManaged` with `presence=missing`; no successor UUID was enrolled. The foreground launcher's final `child_exit` terminal line was not retained. See the earlier committed revision for the full sanitized command transcript and original screenshot provenance.

## 3. Native `software` renderer registration — final closeout

On **2026-11-08**, using `gmki91` native Plasma X11 and RDP endpoint `opi6plus01.brendler`, the maintainer invoked the same development launcher with:

```bash
python3 tools/joetoo-sdl-registration-launch.py opi6plus01.brendler joe \
    --desktop 1 --slot 2 \
    --profile sdl-x11-a1c-v1 \
    --rdp-x11-renderer software \
    --rdp-x11-identity-settle-ms 500
# End of commands

```

The displayed launcher result and live GNOME desktop established one *managed* `software`-mode registration, not just renderer diagnostic feasibility. The captured values were:

| Field | While viewer open | After clicking titlebar X |
| --- | --- | --- |
| Renderer/profile | `software` / `sdl-x11-a1c-v1` | Same test run |
| `managed_id` | `win-001` | **`win-001`** |
| `window_uuid` | `be27f183-c8a2-4772-a802-1cc5e2fb2f30` | **same UUID** |
| Registered child PID | `2640147` | Historical observation only; not proof process remains running |
| `presence` | `present` | **`missing`** |
| `placement` | `not_requested` | `not_requested` |
| Intended desktop/slot | `1` / `2` | `1` / `2` |
| Registration result | `registered`, one success | `succeeded=1`, `failed=0`, `ambiguous=0`, `timeout=0` |
| Placement transaction | `IDLE` | `IDLE` |
| Observation synchronized | `true` | `true` |

The after-close record was supplied as `temp(8)` in the maintainer conversation. Its `GetManaged win-001` returned `state=FOUND`, the original UUID above, `presence=missing`, `connection=not_attempted` and `placement=not_requested`. Its `RegistryStatus` returned `managed_count=1`, `presence_counts={missing:1,present:0,uncertain:0}`, `request_counts={succeeded:1,failed:0,ambiguous:0,timeout:0,pending:0,running:0}`, `placement_transaction={id:null,state:"IDLE"}`, `observation.synchronized=true`, and `viewer_cleanup_uncertain=false`. The after-close observation retained `pid=2640147`, resource class `com.freerdp.client.sdl3` and the previously recorded geometry/desktop, correctly treated as history rather than a live process assertion. No replacement was adopted.

The launcher console's final `child_exit` line was **not attached**. Do not invent its value, and do not treat that missing line as proof of an incorrect window lifecycle. Screenshots and complete transient terminal attachments are not publicly stored here because they include unrelated desktop contents and ephemeral title/source identifiers. This text contains sufficient sanitized UUID/managed-ID correlation for this acceptance decision.

## 4. Maintainer decision and limits

**Increment 2 is formally ACCEPTED** for the stock-client legacy native-KWin-X11 registration-only implementation with both `auto` and `software` renderer choices, subject to the 500 ms best-effort role-discrimination risk. Native-Wayland Increment 1 remains accepted. This acceptance confirms positive registration and accurate post-close missing-state retention; it does **not** grant automatic viewer placement, configured `-o` integration, safe indefinite human authentication waiting, GNOME-session verification, TLS/NLA production policy or generalization to XWayland-as-native-X11.

The maintainer has separately accepted the engineering sequence: Increment 3 implements exact-UUID operator-controlled placement; Increment 4 introduces sequential human-interactive configured RDP/VNC launches; Increment 5 and Step 1.5d perform security/integrated regression; Phase 2 is reserved for measured optional concurrency/prompt staging. See [active HANDOFF](HANDOFF.md) and [strategy decision](step1.5c5d-increment3-strategy-decision.md). This evidence record is not itself authority for agent edits or native runs.
