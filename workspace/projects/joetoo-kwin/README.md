# joetoo-kwin

Development workspace for replacing the joetoo X11 `xdotool_*` window workflows
with KWin-compatible tools on both X11 and Wayland. These are candidate sources
in `joetoo-ai`, not installed Gentoo packages. See [ARCHITECTURE.md](ARCHITECTURE.md)
for version 1 requirements, design contracts, and acceptance gates.

## Current status

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

## Development and validation platforms

The native validation reported below was conducted on Gentoo Linux with KDE
Plasma 6.7.5, OpenRC, and user-session KWin. These are test environments,
not permanent hardware or minimum-version requirements.

| Host | Relevant platform | KWin backend |
| --- | --- | --- |
| `gmki91` | GMKtec NucBox M3 PLUS, Intel i9-12900HK, x86_64 | X11 |
| `q552u01` | ASUS Q552UB, Intel i7-6500U, x86_64 | Wayland |

Both used 1920×1080 displays for the recorded development tests. Kernel,
theme, transient memory/battery use, and other fastfetch details are deliberately
not maintained here.

## Completed proof-of-concept and milestone evidence

| Step | Maintainer-reported result | Reference |
| --- | --- | --- |
| 0 / early POCs | KWin positioning, independent Konsole, interactive SSH `bash --rcfile`, unreachable-target placeholder, original-shell return and process exit behavior demonstrated | [Historical POCs](archive/README.md) |
| 1.2a–1.2b | OpenRC user-service and resident KWin JavaScript start/restart and reconnection validated; broker restart did not terminate existing Konsole/SSH clients | [Native validation](archive/step1.2a-candidate/NATIVE_VALIDATION.md) |
| 1.3a–1.3a.2 | KWin UUID/geometry/lifecycle observation and automatic inventory synchronization on both backends, without implied ownership | [PR #16](https://github.com/JosephBrendler/joetoo-ai/pull/16) |
| 1.3b.1–1.3b.2 | Diagnostic exact-PID correlation, class-candidate reporting, and conservative ambiguous/timeout behavior on both backends | [PR #17](https://github.com/JosephBrendler/joetoo-ai/pull/17) |

**Step 1.3b detail:** Konsole (`--separate`) and Dolphin (`--new-window`)
produced exact-PID `MATCHED` results on X11 and Wayland. Existing-profile
Chrome launches delegated to a running browser and correctly returned `TIMEOUT`
with a class-only candidate, not ownership. Unique Chrome `--user-data-dir`
launches matched their KWin PID and UUID on both backends, at the cost of an
isolated browser profile. Both machines passed 74 Python and 4 JavaScript
regression tests. This establishes useful diagnostics, **not** production-grade
ownership for arbitrary delegated applications. See the
[archived Step 1.3b notes](archive/STEP1_3B_PROBE.md) for the original experiment
instructions and protocol details.

## Active development files and checks

- `libexec/joetoo-kwind` — Python session D-Bus broker and observational data.
- `joetoo-kwin-resident.js` — KWin resident observation/placement interface.
- `joetoo-kwin` — current Bash client for active-window movement and legacy
  single-launch POC. The richer Step 1 planner is still archived.
- `tools/joetoo-kwin-correlation-probe` — read-only launch correlation probe.
- `user-init.d/`, `conf.d/`, `user-conf.d/`, `poc-user-conf.d/` — OpenRC
  service and executable configuration.
- `tools/joetoo-kwind-install-poc` — user-owned POC installation/checking tool.
- `tests/` — headless regression tests; `archive/` — historical references.

Run these checks from `workspace/projects/joetoo-kwin/`:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_step1_3a.js
bash -n joetoo-kwin tools/joetoo-kwin-correlation-probe
./tools/joetoo-kwind-install-poc --check
```

The POC user service can be inspected in a local Plasma session with
`rc-service -U joetoo-kwind status`. Installing/updating the POC or running
window-launching experiments are separate, explicit maintainer operations.

## Design and development references

- [Architecture and version 1 requirements](ARCHITECTURE.md) — authoritative
  product design; proposed schema and open questions remain subject to review.
- [Project AGENTS.md](AGENTS.md) — AI collaboration and documentation policy.
- [Archive index](archive/README.md) — original POCs, candidate designs and
  historical testing instructions.
- [PR #16](https://github.com/JosephBrendler/joetoo-ai/pull/16) and
  [PR #17](https://github.com/JosephBrendler/joetoo-ai/pull/17) — signed
  implementation history and milestone-level test evidence.

Do not treat historical examples or evidence as newly accepted design
requirements. Architectural choices are discussed with the maintainer before
they are incorporated into `ARCHITECTURE.md`.
