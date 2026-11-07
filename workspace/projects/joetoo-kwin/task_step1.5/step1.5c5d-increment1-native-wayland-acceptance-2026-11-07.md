# Step 1.5c.5d — Increment 1 acceptance: native-Wayland SDL registration only

**Decision:** **ACCEPTED by the maintainer, 2026-11-07.** This decision closes only
§5A **Increment 1 — Native-Wayland SDL registration only** of
`Step1.5c5_implementation_scope.md`, not Increment 2, placement, configured
`-o`, production transport security, the entire 1.5c.5d milestone, or `main`
integration.

**Implementation:** Four additive development-only D-Bus operations
(`BeginSdlRegistration`, `BindSdlRegistration`, `PollSdlRegistration`,
`CancelSdlRegistration`) plus the direct-child SDL launcher and broker-owned
exact UUID correlation; no placement. Its accepted scope/trust boundary is the
existing `step1.5c5d-sdl-interface-contract.md` v1, **not** a production endpoint
or TLS/NLA policy. The four-method interface is not yet authorized as a
production API for other clients/backends.

## Acceptance basis

- q552u01, native Plasma Wayland: maintainer Begin/Cancel smoke ACCEPTED;
  successful native registration, actual `wayland` backend, exact child
  PID/application/marker/KWin UUID and private FD evidence; usable remote viewer
  separately observed; registration-only placement remained `not_requested`.
- Gate A: independent live UUID/backend proof, window closure, and missing
  managed-record retention PASS.
- Gate B1: local refused connection failed closed and left no managed window or
  owned child PASS.
- Gate B2: Ctrl+C during NLA dialog cancelled promptly, no child leak or false
  enrollment PASS. Separate earlier NLA-dialog Cancel passed.
- Gate C1: simultaneously visible unrelated SDL viewer and launch-owned viewer
  shared the same application class; only the correct launch-owned PID/UUID was
  registered, and closing it left the unrelated viewer alive PASS.
- Integrated headless regression added by Codex in `tests/test_rdp_broker.py`:
  one broker/source lifetime, first registered viewer closes but retains a
  `missing` record; second viewer registers at another slot; both records,
  request IDs, markers, PIDs, UUIDs, terminal results and no-placement invariants
  remain distinct. No production code was changed in this iteration.
- **Independent maintainer verification on gmki91, 2026-11-07:** 179 focused
  Python PASS, 614 full Python PASS, 99 JavaScript PASS, 81 standalone RDP-broker
  PASS, zero failures. `git diff --check` passed. At review, the working tree
  showed only `M task_step1.5/HANDOFF.md` and `M tests/test_rdp_broker.py`;
  no claim of staging/commit/push of these changes yet.
- CA-signed system GNOME Remote Desktop listener 3389 PKI excursion documented
  separately; successfully observed trust/hostname verification. It does not
  constitute a final managed SDL production TLS/NLA policy, and does not imply
  analogous user-service port 3390 configuration.

## Evidence pointers

- [`step1.5c5d-native-wayland-sdl-registration-evidence-2026-11-06.md`](step1.5c5d-native-wayland-sdl-registration-evidence-2026-11-06.md)
- [`step1.5c5d-native-wayland-sdl-gateA-identity-evidence-2026-11-06.md`](step1.5c5d-native-wayland-sdl-gateA-identity-evidence-2026-11-06.md)
- [`step1.5c5d-native-wayland-sdl-gateB1-refused-connection-evidence-2026-11-06.md`](step1.5c5d-native-wayland-sdl-gateB1-refused-connection-evidence-2026-11-06.md)
- [`step1.5c5d-native-wayland-sdl-gateB2-ctrl-c-cancellation-evidence-2026-11-06.md`](step1.5c5d-native-wayland-sdl-gateB2-ctrl-c-cancellation-evidence-2026-11-06.md)
- [`step1.5c5d-native-wayland-sdl-gateC1-unrelated-viewer-coexistence-evidence-2026-11-07.md`](step1.5c5d-native-wayland-sdl-gateC1-unrelated-viewer-coexistence-evidence-2026-11-07.md)
- [`step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md`](step1.5c5d-gnome-remote-login-pki-evidence-2026-11-07.md)
- [`HANDOFF.md`](HANDOFF.md) — continuity and current authority.

## Deferred, not acceptance blockers

X11 same-PID/same-marker temporary-versus-persistent viewer role (Increment 2),
placement release/remote readiness (Increment 3), configured SDL `-o` (Increment
4), production transport-security policy and overall closure (Increment 5).
The native Gate C1 began with no historical managed record; the integrated
headless two-success regression addresses that specific cross-request property
without another native session. No further native isolation test is required
solely for Increment 1 acceptance.

**Publication status:** acceptance is the maintainer's decision in this
conversation. The report, HANDOFF update and candidate test remain unpublished
until reviewed and committed/pushed by the maintainer. Codex's previous
headless tests were reported and independently reproduced; neither this
statement nor the task reports authorize Codex to publish or execute native
sessions.
