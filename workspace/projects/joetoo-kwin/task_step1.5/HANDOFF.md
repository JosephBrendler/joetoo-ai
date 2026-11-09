# Step 1.5 — Active task dispatcher

**Task:** Step 1.5c.5d / Increment 3 — native-Wayland SDL placement validation and residual geometry question.  
**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Relevant source commits:** `e7f63ce2a9bbb0ed09f7f7465099e360ecd88fa1` (Increment 3 placement implementation), `5a2e152ab4f22e21be14c0df2f2cee17e9a6dd8c` (reviewed sequential registration fix). Inspect actual checkout/HEAD/dirty state; do not reset or force a stale checkout.

**State as of 2026-11-09:** Increment 1 native-Wayland registration-only and Increment 2 native-X11 registration-only remain **ACCEPTED**. Increment 3 controlled SDL placement is implemented and native X11 `software` and `auto` exact-UUID placement/closure both passed. The previously observed terminal-`OK` false `Broker is busy` was fixed in `5a2e152`, independently code reviewed, verified with maintainer-run **691 full Python / 158 JavaScript tests** on `gmki91`, and **PASSED native sequential A/B registration in the same broker lifetime**. **Do not reopen that settled defect.** Increment 3 overall is **NOT YET ACCEPTED**, pending native-Wayland placement and the explicitly unresolved exact frame-size question.

**Primary evidence:** [native X11 sequential A/B closeout (2026-11-09)](step1.5c5d-increment3-native-x11-sequential-registration-closeout-2026-11-09.md), [earlier X11 `software`/`auto` placement and historical pre-fix Busy transcript](step1.5c5d-increment3-native-x11-placement-2026-11-09.md), [native Wayland Increment 1 registration acceptance](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md). Also: [task README](README.md), [engineering scope](Step1.5c5_implementation_scope.md), [settled serial-workflow decision](step1.5c5d-increment3-strategy-decision.md).

## Closed X11 defect — native acceptance summary

On `gmki91` kernel 6.18.62, after publishing `5a2e152` and restarting/installing the service (691 Python / 158 JS PASS), the maintainer:
- Registered viewer **A**, `software`, `win-001`, desktop 1/slot 2, UUID `2a99dcb3-5c7e-4206-b006-ed6b6a57c5b2`; explicitly placed it at (0,0) (`reason=verified`), closed it, and observed `presence=missing` with UUID retained and `placement=succeeded`.
- **Without restarting `joetoo-kwind`**, registered viewer **B**, `auto`, `win-002`, desktop 1/slot 3, UUID `5a893ce2-5cec-4b20-b7d0-01626385df42`, while A's previous `placement_transaction={state:"OK",id:"c32cddcc7d6848759890ad9210047f5e"}` remained. B was intentionally **not placed** (`placement=not_requested`).
- Closed B: both records were `missing` with original distinct UUIDs, two successful and zero failed/ambiguous/timed-out registrations, synchronized observation and no viewer-cleanup uncertainty.

**Sequential-launch defect CLOSED.** Retain the old `Broker is busy` evidence as a historical pre-fix finding, not a current blocker.

## Next active task — native-Wayland placement on q552u01

This is a **maintainer-run graphical acceptance test** of Increment 3 controlled placement, not an X11 renderer/dwell experiment or an Increment 4 configured `-o` launch.

1. On `q552u01`, inspect its **actual** `~/joetoo-ai` checkout: `git status --short --branch`, `git branch --show-current`, `git remote -v`, and local changes. **Stop for inspection on any dirty or divergent checkout.** Run `git fetch origin` (non-destructive), switch to `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation` if an existing local task branch is safe; otherwise create a tracking branch from `origin/task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. Fast-forward only with `git merge --ff-only origin/task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. **Never use `reset --hard`, `clean`, automatic stash, forced checkout or force push.** Verify resulting HEAD contains `5a2e152` and this documentation, and that the worktree is clean.
2. Verify **native KWin Wayland** is active (`kwin_wayland`, not `kwin_x11`); in the graphical `joe` session verify local session D-Bus and `sdl-freerdp`/Python/`qdbus6`/`jq`/Node prerequisites. Do not confuse a login-TTY-derived `XDG_SESSION_TYPE=tty` label with proof of a native-X11 compositor.
3. After source sync and preflight, run `./tools/restart_joetoo-kwind test` to update the installed user service/resident and run tests (record any unavailable Node dependency; if needed choose `notest` but do not claim tests passed). Check introspection, `ListManaged` and `RegistryStatus.observation.synchronized=true`. Restart clears broker in-memory managed records: **no restart during subsequent registration/placement/closure**.
4. **Konsole 1**, register a new viewer with **native Wayland wire shape**: `python3 tools/joetoo-sdl-registration-launch.py opi6plus01.brendler joe --desktop 1 --slot 1` (choose a verified free slot if needed). **Do not pass** `--profile sdl-x11-a1c-v1`, `--rdp-x11-renderer`, or `--rdp-x11-identity-settle-ms`. Keep foreground launcher and viewer open through placement; no need to log in past GDM.
5. **Konsole 2**, record `ListManaged`, `GetManaged <id>`, `RegistryStatus`, exact original UUID, desktop/slot and `placement=not_requested`. Invoke the independent `joetoo-sdl-release-placement.py <confirmed-id> --confirm --desktop 1 --slot 1 --x 120 --y 90 --width 800 --height 600`; capture result and live `GetManaged` plus `ListObserved` geometry. Match the **same** UUID; position/desktop correctness and final frame size are separate observations. Do not alter focus/stack or run continuous geometry repair.
6. Close the viewer with its titlebar X. Verify the original UUID remains `presence=missing`, placement history stays correct, and a new placement attempt of the now-missing viewer safely fails `InvalidRequest`; capture final registry and launcher child-exit result. Never adopt a new UUID or restart midtest.
7. Preserve native outputs as new evidence; then decide Increment 3 closure or a narrowly justified geometry contract/fix.

## Outstanding geometry question

Both earlier X11 renderer tests requested `800×600`, but the observed decorated KWin frame later measured `1032×804`, even though target positions/desktops were correct. This is consistent with, but does not prove, a 1024×768 remote RDP client area plus decorations. Placement `reason=verified` is a point-in-time result, not continuous enforcement. Compare Wayland measurements and investigate SDL FreeRDP client-area versus frame-size policy; any future launch-time sizing may belong in Increment 4's existing derived geometry planner. **No endless resizing/focus/stack repair loop.** Keep exact-UUID/position acceptance separate from stable-size acceptance.

## Settled later roadmap — not current implementation

**Increment 4:** existing `DESKTOP|PROGRAM|MODE|TARGET[|LAYER]` grammar, derived slots/geometry, serial mixed Konsole/Dolphin/TigerVNC/RDP `-o` launches, human-interactive NLA/VNC/SSH prompts. Genuine human credential-wait must **not terminate the client/tunnel solely on an arbitrary fixed automated timeout**; machine identity/placement/cleanup deadlines remain bounded. **Increment 5:** RDP TLS/NLA/security and native regression. **Step 1.5d:** broader X11/Wayland and `-L`/`-l`. **Phase 2:** optional measured throughput/concurrency.

**Hard stops:** No active-window, title/class/PID-only replacement for exact UUID; no automatic placement on registration, credentials injection, TLS bypass or false remote login claims. No automatic change to unrelated config, source history or local workstation state. Maintainer authorizes any future code change, publication or native operation separately.
