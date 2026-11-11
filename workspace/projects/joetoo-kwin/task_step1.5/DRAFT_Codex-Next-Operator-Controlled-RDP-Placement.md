# Codex task — implement explicit operator-controlled SDL RDP placement

**Task:** `joetoo-kwin` / Step 1.5c.5d, **Increment 3 controlled placement**, first bounded implementation. **This is a request to write tested software**, not an exploratory memo or a design-only/renderer experiment. No native execution or Git publication is authorized.

## Entry conditions and current source of truth

1. Work in the existing checkout of `JosephBrendler/joetoo-ai`, `workspace/projects/joetoo-kwin`, branch `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. The maintainer just pushed Codex/maintainer fixes, verified on GitHub at code HEAD `13e532c5d80c5beef69451f77d44dd4b36e1b50d`. This is a **checkpoint, not a reset instruction**. Check actual branch/HEAD/dirty status; preserve newer changes. Stop and report if the expected HANDOFF/evidence update has not been installed yet, if authorization differs, or if unexpected local edits conflict.
2. Read applicable root/workspace/project/subdirectory `AGENTS.md`, `workspace/README.md`, current `task_step1.5/HANDOFF.md`, governing `task_step1.5/Step1.5c5_implementation_scope.md` **Increment 3**, `task_step1.5/increment2-deferred-authentication-workflow-section.md`, and the latest [native X11 registration evidence](task_step1.5/step1.5c5d-increment2-native-x11-registration-2026-11-08.md). Current architecture and code are authoritative; do not copy an old patch or reintroduce a completed issue.
3. Maintainer has accepted the current **native-X11 registration implementation candidate** and its **registration-only `auto` native proof**, including same-UUID `presence=missing` after titlebar closure. All **644 Python / 145 JavaScript** tests passed. Native managed `software` acceptance remains maintainer-owned; it is not a blocker to offline Increment 3 development. Do not change A1 `auto|software` configuration, 500 ms selector, or its residual-risk wording.
4. The earlier `XDG_SESSION_TYPE=tty` integration issue is closed in the current source: the broker no longer requires the service environment to say `x11`; actual SDL child/backend evidence remains verified. Do not restore the old guard or alter OpenRC allowlists.

## Implement one small, useful capability

After the existing SDL development launcher has **successfully registered a unique live viewer UUID without placement**, provide a **deliberate, independently invoked operator action** to release **that same broker-owned managed window** for one controlled placement operation. The user may first complete NLA, GDM login, and visually decide the remote desktop is ready. The broker must **not guess** any remote readiness from renderer/frame, window survival, RDP logs, GDM pixels or the registration outcome.

**Expected user-visible behavior:**

- Default behavior is exactly as today: SDL launches, verifies native Wayland or explicit native-X11 registration, returns the exact managed UUID and `placement=not_requested`, and **does not move/focus/stack any window**.
- A new explicit operator action, targeting a **managed ID / broker-held registration** (not a user-supplied raw KWin UUID as authorization), requests placement with validated destination and geometry, using established joetoo-kwin placement mechanisms and configuration policy. Design the smallest ergonomic CLI/action that works **while the foreground SDL launcher continues supervising its child**. It must be possible for a separate Konsole/interactive command to trigger this action after visual confirmation, without killing or restarting FreeRDP or replacing the child identity.
- Bind the action to the *existing registered* KWin UUID and its managed record, expected source, live current observation and intended desktop/slot; retain source/registry/owner/PID/exact UUID checks at claim and verification. No class-only/title-only/last-window fallback, no retarget when missing, moved, or replaced. If the window disappears or the source changes, fail closed and report a useful outcome.
- Honor exclusive broker placement transaction/busy state, exact UUID revalidation, bounded timeouts, atomic/retained result semantics, and existing window-frame/desktop/geometry verification. Prefer reusing existing broker/resident placement machinery; no duplicate coordinate or observation solver. Keep a failed attempt from corrupting ownership or making another window eligible.
- A successful explicit release reports placement independently of `registered` and `remote_session=unverified`; no automatic focus or stack operation. Leave operator-manual window changes alone after completion; this task does not impose ongoing layout enforcement. Remote NLA/TLS/certificate handling is unchanged.
- The implementation should support **registered SDL viewers in their already accepted native-Wayland path and the explicit legacy native-X11 path**, with backend-specific identity checks preserved. Unsupported XWayland-as-native-X11 is not silently admitted.

Do not treat an interactive remote login dialog as the registered viewer; do not move a credential window by heuristic. The **operator's explicit release request** is the only placement readiness signal in this increment. Do not add automatic authentication, clipboard interception, keyboard/mouse capture, or a background observer.

## Source scope and authorization

Start by inspecting real broker registration, `GetManaged`, `RegistryStatus`, `SubmitMove`/`TakeMove`/`Complete`, VNC managed placement and resident JS. The existing generic shortcut moves the selected active window; it must **not** substitute for precise broker-owned registered-RDP identity. Reuse its safe UUID-level mechanics where justified, not any ambient selection heuristic.

Authorized **only as needed for this feature**:

- `libexec/joetoo-kwind` — minimal broker-side registered-viewer placement intent / verification, additive D-Bus API **only if the existing exact-UUID path is insufficient**.
- `joetoo-kwin-resident.js` — minimal bounded new request handling **only if required** to apply a broker-verified exact UUID through existing resident placement functions.
- `libexec/joetoo_kwin_registry.py` — minimal placement status integration **only if demonstrably necessary**; preserve existing serialization and managed identity semantics.
- `tools/joetoo-sdl-registration-launch.py` — only if necessary for additive status output and backward-compatible coordination. Prefer a small **new** operator-invoked tool (e.g. `tools/joetoo-sdl-release-placement.py`) over altering the foreground launcher’s lifetime semantics.
- Focused `tests/test_rdp_*.py`, `tests/test_*.js`, or one clearly named new test module; existing configuration template if a new bounded value is essential. Never hard-code a new timing/geometry parameter that belongs in configuration.

If source inspection reveals a materially different public API, new privileged capability, a broad resident rewrite, or placement cannot be correctly bound to a registered UUID, **stop with the precise blocker and smallest proposed resolution**, rather than implementing a weaker heuristic. No general refactor.

Not authorized: edit or run the protected maintainer scripts (`tools/restart_joetoo-kwind`, `tools/rdp_identity-security_proof`, etc.); install/restart service/resident; connect to RDP; interact with a real desktop; patch FreeRDP/SDL/KWin; change TLS/NLA/certificates; implement configured `-o -f`, prompt relocation, multiwindow scheduling, unattended login, placement automation, focus/stack enforcement, new daemon/observer; mutate `joetoo` or `joetoo-upstream`; commit/push/open PR/merge. No changes to task HANDOFF/README/evidence or architectural scope without separately permitted edit authority.

## Headless acceptance before returning to maintainer

Add positive and negative tests that exercise **actual broker/registry and resident contract** where practical:

- No placement on registration alone, including both backend modes; explicit release of one current registered UUID succeeds and verifies intended desktop/geometry without modifying other windows.
- Pre-registration, unknown ID, missing/uncertain record, absent/stale UUID, wrong source/revision, wrong desktop/slot, stale or competing request, invalid geometry, and expired/cancelled release are rejected.
- Window disappears or is manually moved/changed during release: no replacement UUID is used; result is honest, with no unfounded success; no extra focus/stack.
- Accepted Wayland registration behavior, X11 A1/C selector and renderer modes, generic/VNC/Konsole/Dolphin moves, source and owner protections remain unaffected.
- Headless tests cannot prove human completed GNOME authentication or graphical correctness. Do not present them as native acceptance.

Run focused Python/JS suites, full `python3 -m unittest discover -s tests -p 'test_*.py'`, `node --test --test-isolation=none tests/test_*.js`, syntax and `git diff --check` where available. Preserve the root `AGENTS.md` command-copy safety convention: shell blocks end with a harmless `# End of commands` comment **and a blank line**. If a failure is known unrelated, identify exact tests and cause; do not quietly exclude them.

## Return exactly the engineering deliverable

Report actual base/current HEAD, changed paths, concise diff summary, resulting operator command/API, tests passed/failed, how the exact registered UUID is revalidated, failure modes, and any residual issues. Attach or provide a complete diff for maintainer review; explicitly ask for authorization before commit/push/installation/native testing. Include a **small maintainer-only native test proposal**, but **do not run it**. The first native release test should be on a single free slot, with the operator confirming actual remote readiness before opting in, inspecting `GetManaged`/`RegistryStatus` before and after, and refusing wrong-UUID or unintended placement.

**Stop after tested code and report. Do not spend a turn rewriting history or reopening renderer feasibility.**
