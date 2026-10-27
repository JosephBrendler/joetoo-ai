# joetoo-kwin

Development workspace for replacing the joetoo X11 `xdotool_*` window workflows
with KWin-compatible tools on both X11 and Wayland. These are candidate sources
in `joetoo-ai`, not installed Gentoo packages. See [ARCHITECTURE.md](ARCHITECTURE.md)
for version 1 requirements, design contracts, and acceptance gates.

## Current status

**Completed through Step 1.3b** (October 2026). Current sources can observe
KWin window identities and lifecycles, recover observational inventory after a
broker restart, and diagnose direct-PID launch-to-window correlation. They do
**not** provide a managed-window ownership registry, a multiwindow `-o`
launcher, or safe managed-window close operations.

**Next: Step 1.4 — in-memory multiwindow registry**, in four agreed increments:

| Increment | Intended outcome |
| --- | --- |
| 1.4a | Review the proposed record/identity model and create headless contract tests; approve design changes before implementing them |
| 1.4b | Implement multiwindow registration and observational state updates, without class-only adoption |
| 1.4c | Expose read-only managed-window list, detail, and broker status |
| 1.4d | Validate a 37-window mock, then native X11 and Wayland scenarios |

The detailed registry schema, eligibility rules, and new D-Bus method names
remain **design questions**, not approved implementation contracts.

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
