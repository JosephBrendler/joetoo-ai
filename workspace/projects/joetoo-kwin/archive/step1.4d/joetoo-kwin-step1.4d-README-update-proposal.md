# Proposed README update for Step 1.4d review

This is a **draft replacement** for the `## Current status` block in
`workspace/projects/joetoo-kwin/README.md`, stopping before
`## Development and validation platforms`. It is not part of the code patch.

## Current status

**Completed through Step 1.4c** (October 2026). The broker observes KWin
window UUIDs and lifecycles, recovers observational inventory, and diagnoses
PID-based launch correlation. Steps 1.4a–1.4b introduced an in-memory
managed-window registry with broker-private, positively correlated registration
and conservative per-UUID reconciliation. Step 1.4c added read-only D-Bus
`ListManaged`, `GetManaged`, and `RegistryStatus` queries without exposing a
public registration or close API.

| Increment | Status and scope | Evidence |
| --- | --- | --- |
| 1.4a | Complete: registry model, identities and headless contract tests | [PR #19](https://github.com/JosephBrendler/joetoo-ai/pull/19) |
| 1.4b | Complete: broker-private registration, multiple records, UUID-based observation reconciliation | [PR #20](https://github.com/JosephBrendler/joetoo-ai/pull/20) |
| 1.4c | Complete: read-only managed list/detail/status D-Bus interfaces | [PR #21](https://github.com/JosephBrendler/joetoo-ai/pull/21) |
| 1.4d | In progress: multiwindow scenarios and X11/Wayland native validation | Pending maintainer results |

On `gmki91`, the maintainer reported **114 Python and 4 JavaScript tests
passing** for the merged Step 1.4c candidate. These are headless regression
results, **not** native proof that a CLI launch results in managed registration.

A proposed Step 1.4d diagnostic `test-multi-launch` fixture reuses the existing
placement-only `launch_one_window` to open four independent local Konsole
windows over two desktops, with fixed test geometry for 1920x1080 displays.
It deliberately ignores configuration recipes, SSH and VNC, and does **not**
register windows. The full `-o` launcher, managed launch authorization/IPC,
managed close, and checkpoint recovery remain future work under Steps
1.5–1.7. Neither observation nor placement confers managed ownership.

Native X11 and Wayland results will be added after the maintainer runs the
corresponding tests; do not treat this proposal as verification of them.
