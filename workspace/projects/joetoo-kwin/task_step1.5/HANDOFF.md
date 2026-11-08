# Step 1.5 — Active task dispatcher

**Purpose:** Current scope, maintainer decisions, next authorized actor, and stop conditions. This is **not** a chronological history. See [task README](README.md) for the decision index and detailed [2026-11-08 A1 evidence](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md). Older HANDOFF versions grant no authority.

## Current dispatch — Step 1.5c.5d / Increment 2 / dual-renderer A1+C alignment (2026-11-08)

**Branch:** `task/joetoo-kwin-step1.5c5d-managed-rdp-implementation`. **Published checkpoint:** `111c04e3344ca211e1104e21f3d2508a2b42d4e9` is the recorded A2→A1/C transition commit, **not an assertion about current HEAD**. The maintainer subsequently edited diagnostic tooling locally and supplied native archives. Verify actual branch/HEAD/status and applicable `AGENTS.md`; never overwrite newer or uncommitted work.

## Results and evidence — maintainer-accepted feasibility

- **Increment 1 — native-Wayland SDL registration without placement:** **ACCEPTED / COMPLETE**, unchanged.
- **Increment 2 — legacy native-KWin X11 SDL registration without placement:** **OPEN / NOT ACCEPTED**; no broker C implementation or native managed-registration acceptance yet.
- **A2 Stage 1 patched-FreeRDP producer:** **ABORTED**; no client/SDL/KWin patches. A2 Stage 0 synthetic research remains previously accepted (46 focused + 99 existing JS PASS), not A1/C proof.
- **Gate F read-only A1/C feasibility:** **ACCEPTED**, including the Nov 5 observed 20 ms marked predecessor and 72.9 s persistent successor. These are observed lifetimes, not a general timing guarantee.
- **Gate N software-renderer native A1 feasibility on `gmki91`, Nov 8:** **ACCEPTED AS PROVISIONAL FEASIBILITY EVIDENCE**, not Increment 2 acceptance. The installed stock client ran with `SDL_RENDER_DRIVER=software` and `SDL_FRAMEBUFFER_ACCELERATION=0`; log confirmed native `x11` and SDL `software`. Of three observed same-PID X11 windows, only the eventual persistent normal desktop viewer carried the exact title marker. Reported usable remote GNOME desktop with some resize tearing. Main KWin transport was intact, **X11 discovery_gaps=1**; FreeRDP client exit **131** followed operator titlebar closure, while parent proof reported success. **Evidence (includes full terminal output, timestamps, UUID/XID correlations and raw-archive SHA-256):** [2026-11-08 A1 native evidence](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md). Do not claim infallibility or measured acceleration performance.

## Approved design direction (not yet implemented)

Two **independent**, user-configurable settings, restricted to the explicit legacy **native Plasma/KWin X11** SDL FreeRDP profile:

- Proposed `rdp_x11_renderer = auto|software`. `auto`: SDL default renderer selection, with inherited `SDL_RENDER_DRIVER` and `SDL_FRAMEBUFFER_ACCELERATION` removed **only for the managed child**. `software`: pass `SDL_RENDER_DRIVER=software` and `SDL_FRAMEBUFFER_ACCELERATION=0` to that child. `auto` does not guarantee hardware acceleration; `software` may have a performance cost not quantified by this run. Renderer configuration **does not prove viewer identity**.
- Proposed `rdp_x11_identity_settle_ms = 500`, **one** centrally configurable broker-local monotonic dwell eligibility interval for **both renderer modes**. Start on **first full qualification of the specific UUID**, not its birth or each polling iteration. Concurrent provenance/history checks and fresh unique-live-UUID revalidation; no second `PollCorrelation()` 500 ms gate, no blocking sleep, no silent UUID retarget. The 600 ms marked-transient counterexample remains a mandatory negative test and residual risk. This is a best-effort legacy selector, not infallible proof.

These choices supersede the older sequential phrasing *“only consider C if A1 fails”* for the proposed combined A1+C design, **subject to updating the active [A1/C contract](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md) and [governing scope §5A](Step1.5c5_implementation_scope.md)**. Their existing restrictive terms remain operative until aligned; this HANDOFF does not silently rewrite them.

## Next authorizations and actors

**Codex — Gate D, bounded documentation/contract alignment (AUTHORIZED by maintainer, effective with accompanying prompt):** Read the accepted evidence and actual source/config template *read-only*; edit **only** `task_step1.5/step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md` and the **Increment 2 subsection** of `task_step1.5/Step1.5c5_implementation_scope.md`. Align the two independent settings, explicit `auto` child-environment handling, C in both modes, the single timer, limits and acceptance risks. Keep Gate F/N completed statuses and next stages accurate. No change to this HANDOFF, evidence or task README without a further prompt. **No runtime code, tests, diagnostic scripts, FreeRDP/SDL source, system, config file deployment or release changes.** No Git commit/push/merge. Stop when the docs-only diff is ready for maintainer review. See the accompanying Codex Gate D prompt.

**Maintainer — Gate N2, one default-renderer comparison (AUTHORIZED, strictly maintainer-operated):** On `gmki91` use the now locally updated interactive runner and phase file with both SDL hints **unset**, not set empty, and `RDP_DIAG_SECONDS=900`. Preserve separate private archives; inspect exact marked UUID lifetimes, gaps, backend/renderer, usability and client exit. No resident/broker restart or `mw` operations during the observation. No TLS/NLA changes, client build or patch. Suggested invocation:

```bash
env -u SDL_RENDER_DRIVER -u SDL_FRAMEBUFFER_ACCELERATION \
    RDP_DIAG_SECONDS=900 \
    ./tools/joetoo-rdp-diagnostic-run.sh \
    sdl-freerdp raspiubuntu401:3389 joe
```

**Gate I (broker/launcher/config/headless implementation): NOT YET AUTHORIZED.** Review N2 evidence and aligned scope first; issue another exact bounded source-edit prompt. **Gate A** native registration acceptance is separate and also not authorized. `Increment 3` placement, `Increment 4` configured `-o -f`, PKI/security changes, automatic B interaction gate and any A2 work are out of scope. Codex must never run the native RDP test.

## Governing pointers and stop conditions

- Policy: repo/root, workspace and project `AGENTS.md`; [scope §5A](Step1.5c5_implementation_scope.md); [A1/C active draft](step1.5c5d-sdl-x11-a1c-contract-addendum-DRAFT.md); [native evidence](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md).
- Historical: [aborted A2](step1.5c5d-sdl-x11-a2-contract-addendum-ABORTED.md), [native-Wayland Increment 1 acceptance](step1.5c5d-increment1-native-wayland-acceptance-2026-11-07.md), [deferred authentication/placement](increment2-deferred-authentication-workflow-section.md).
- Retain strict positive caller/child/marker/class/source/owner/FD provenance, complete bounded event/birth/removal history and transaction deadline; never change native-Wayland v1 or generic/TigerVNC behavior. An observed disappearance of a marked X11 transient can be recorded as a tombstone in a future C implementation, not silently erased. The initial 500 ms is an **experimental** setting. No proof of renderer completion, remote authentication or absence of all windows can be inferred from the A1 run.
- Private raw files: `~/.local/share/joetoo-ai/rdp-evidence/` is the maintainer's intended private store. Verify both named `.tbz2` archives exist; the displayed `mv` command only confirms the Stage A **directory** move. Do not commit logs/archives, export secrets, or circulate raw window inventories.
