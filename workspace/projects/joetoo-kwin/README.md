# joetoo-kwin

Development workspace for replacing the joetoo X11 `xdotool_*` window workflows
with KWin-compatible tools on both X11 and Wayland. These are candidate sources
in `joetoo-ai`, not installed Gentoo packages. See [ARCHITECTURE.md](ARCHITECTURE.md)
for version 1 requirements, design contracts, and acceptance gates.

## Current status

**Completed through Step 1.4d** (October 2026). Step 1.4 established
broker-private managed-window registration, independent presence and placement
states, UUID-based observation reconciliation, read-only registry queries, and
bounded asynchronous placement confirmation. The four-window managed-launch
fixture passed native X11 and Wayland validation. These are collaboration
candidates in `joetoo-ai`, not yet the complete version 1 application.

| Increment | Status and scope | Evidence |
| --- | --- | --- |
| 1.4a | Complete: registry identity, state, and headless contracts | [PR #19](https://github.com/JosephBrendler/joetoo-ai/pull/19) |
| 1.4b | Complete: broker-private correlation and multiwindow UUID reconciliation | [PR #20](https://github.com/JosephBrendler/joetoo-ai/pull/20) |
| 1.4c | Complete: read-only `ListManaged`, `GetManaged`, `RegistryStatus` | [PR #21](https://github.com/JosephBrendler/joetoo-ai/pull/21) |
| 1.4d | Complete: managed multiwindow launches, asynchronous placement confirmation and native validation | [PR #22](https://github.com/JosephBrendler/joetoo-ai/pull/22) |

For Step 1.4d, the maintainer reported **144 Python and 8 JavaScript tests
passing on each development machine**. Native tests on `gmki91` (Plasma X11)
and `q552u01` (Plasma Wayland) each registered four separate Konsole windows,
confirmed all four placements, verified exact desktop/geometry and no adoption
of preexisting KWin UUIDs, and preserved placement history when a window was
closed (presence became `missing`). These results do not establish completion
of the general `-o` SSH/configuration workflow, destructive managed close,
checkpointing or reboot restoration.

For the completed milestone, its validation boundaries and deferred issues, see
[Step 1.4 closure handoff](task_step1.4/HANDOFF.md). The proposed next milestone,
including its authorization and validation plan, is in the
[Step 1.5 task handoff](task_step1.5/HANDOFF.md).

Step 1.5 addresses the shared geometry policy, `mw l/r`, colorized `-c`,
configuration-driven `-o` with SSH placeholders and `-v/-q`. Steps 1.6–1.9
remain planned according to [ARCHITECTURE.md](ARCHITECTURE.md). Phase 2
reserves measured optimization/refinement work after the core prototype.

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
- `joetoo-kwin` — current Bash CLI for active-window placement and the
  Step 1.4d managed test-launch fixture; generalized configuration-driven
  layouts and SSH placeholders are Step 1.5 work.
- `tools/joetoo-kwin-correlation-probe` — read-only launch correlation probe.
- `user-init.d/`, `conf.d/`, `user-conf.d/`, `poc-user-conf.d/` — OpenRC
  service and executable configuration.
- `tools/joetoo-kwind-install-poc` — user-owned POC installation/checking tool.
- `tests/` — headless regressions; `archive/` — historical POCs;
  `task_step1.4/` and `task_step1.5/` — milestone evidence and current-task
  handoffs, not runtime source.

Run these checks from `workspace/projects/joetoo-kwin/`:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/*.js
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
- [Step 1.4 closure](task_step1.4/HANDOFF.md) and
  [Step 1.5 active-task proposal](task_step1.5/HANDOFF.md) — milestone
  completion evidence and maintained task state, respectively.
Do not treat historical examples or evidence as newly accepted design
requirements. Architectural choices are discussed with the maintainer before
they are incorporated into `ARCHITECTURE.md`.
