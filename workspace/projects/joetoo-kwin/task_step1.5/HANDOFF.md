# Step 1.5 — Active task dispatcher

**Task / current gate:** Step 1.5c.5d, **Increment 4 Stage 2 — configured SDL FreeRDP production `-o` integration**. Stage 1 (offline recipe/settings validation) is **maintainer accepted and published**. Stage 2 candidate implementation is the proposed next Codex assignment, **not yet authorized by this HANDOFF**. Stage 3 remains separately gated.

**Repository:** `JosephBrendler/joetoo-ai`  
**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Accepted Stage 1 HEAD (verified on GitHub, 2026-11-10):** `12c8f0435f3dace71ecfb4dac79469ee3669de48` (`joetoo-kwin: Increment 4 Stage 1 RDP recipe validation`). Fetch and verify the actual checkout, branch, worktree, and later maintainer edits before any candidate changes; never reset or overwrite them.

## Accepted baseline and evidence

Stage 1 added `libexec/joetoo_kwin_rdp_target.py` and offline `DESKTOP|sdl-freerdp|rdp|rdp://USER@HOST[:PORT][|LAYER]` validation, documented config defaults/bounds, `RDP_SMART_SIZING=$TRUE` with `bool.RDP_SMART_SIZING` display, and regression coverage. The canonical planner, geometry allocator, runtime RDP launch path, existing broker interfaces and development harness behavior were not changed. `-c` accepts the recipe; `-o` still rejects it during preflight, before any application or broker launch. The accepted commit includes the maintainer's `task_step1.5/layers-examples/joetoo-rdp-native.conf` and `joetoo-rdp-bogus.conf` for subsequent positive/negative testing; preserve these files.

**Maintainer verification on `gmki91`:** 803 Python tests **PASS**, 161 JavaScript tests **PASS**; installer `--check` and broker introspection **PASS**. `./joetoo-kwin -c -f .../joetoo-rdp-native.conf` succeeded with the correct two-window desktop-5 plan and `RDP_SMART_SIZING` rendered `True`. The bogus `rdp:rdp://...` target failed with the redacted validator message. Stage 1 did **not** implement production RDP `-o`, select the effective local video backend at runtime, or change existing 120000 ms readiness defaults. Installed-file inventory still excludes the new target helper pending Stage 2.

Earlier **development-only** native Wayland evidence at `599f7f3` established one exact-UUID automatic placement (`(1,1) 800×628`) before remote GDM content became visible; it is not repeated cross-backend acceptance, production RDP operation, TLS/server-identity validation, or proof of remote-session usability. The earlier failed 15-second placement trace remains historical evidence. See [task history](README.md) and its linked native records.

## Governing design and current objective

Read the repository/workspace/project `AGENTS.md`, `workspace/README.md`, [ARCHITECTURE.md](../ARCHITECTURE.md), [authoritative Increment 4 decisions](step1.5c5d_Increment_4_decisions.md), and [scope](Step1.5c5_implementation_scope.md). The older [Increment 3 strategy](step1.5c5d-increment3-strategy-decision.md) and authentication discussion are historical where superseded. The acceptance and publication process is governed by `workspace/README.md`, not by this summary.

**Stage 2 objective:** For an operator-confirmed mixed `-o` plan, launch one directly owned SDL FreeRDP client per RDP recipe; positively enroll its **persistent viewer** using the existing SDL-specific broker/observer identity protocol; submit and verify one exact-UUID placement to the existing planner-owned outer frame and intended desktop/slot; then include the successfully placed registration in the existing desktop cohort's `under → panel → over` one-shot stacking/focus. Remote GDM login is independent of registration and placement. Complete one unresolved viewer transaction before advancing to the next recipe. The short-lived configured frontend must return a truthful result while a persistent worker continues supervising an already registered client.

**Preferred production module boundary:** Extend existing broker-imported `libexec/joetoo_kwin_rdp_launch.py` into **one executable frontend plus persistent worker**, reusing `joetoo_kwin_rdp_target.py` for the Stage 1 parser and sizing arguments. Preserve broker imports and development harnesses; the production `-o` workflow must not execute or chain POC tools. If this design or a new broker JSON/API payload requires material changes, present the exact minimal alternatives/contract for maintainer approval **before** making those changes. Do not introduce a generic VNC/RDP framework.

**Safety and constraints:** Preserve the original worker-owned D-Bus connection and direct SDL child, exact-UUID/source/PID evidence, private result/acknowledgement/cleanup protocol, no inherited `-o` FD 9 lock, viewer survival after frontend exit, and broker-restart non-recovery semantics. `rdp_windowing_backend=auto|wayland|x11` remains user intent: require supported positive backend evidence; if reliable `auto` selection is not straightforward, fail `-o` preflight for `auto` and require an explicit per-host setting, without weakening `-c`. Preserve independent NLA/remote-session outcomes and certificate/SSH trust policies. No hardcoded decoration offsets or new layout formulas. Add the target helper to installer source/destination/check/archive inventory only within the approved Stage 2 implementation.

**Not Stage 2:** Stage 3's shared default **300000 ms** RDP/VNC viewer wait, revised known-clean continuation policy, and conditional verified slot release are deferred; do not silently change 120000 ms defaults, release `presence=missing` slots, relax Busy/uncertain-owner safeguards, or implement Option D concurrent missions. Additional security/native acceptance remains a later maintainer gate. Keep all state transitions truthful and fail closed when ownership or placement is unresolved.

## Next actor and permissions

**Next actor:** Codex **only if the maintainer expressly issues** the separately drafted [Stage 2 Codex prompt](Codex-Increment4-Stage2-Configured-RDP-Launch-DRAFT.md) or equivalent authorization. Within the granted scope, prepare reviewable candidate code and headless tests in `joetoo-ai` and report the full diff (including new/untracked files), exact test results, unchanged peer behavior, and unresolved API/security decisions. **Pause for maintainer approval** before material D-Bus protocol changes or a substantially different launcher design. No native client operation, service install/restart, official repository edit, signed commit, push, PR, merge, or deployment without separate authorization.

**Next review gate:** Maintainer reviews the Stage 2 candidate and decides what further source changes/native checks/publication to authorize; Stage 3 remains a separate assignment.
