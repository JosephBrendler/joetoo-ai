# Step 1.5c.5d / Increment 2 — Stock-FreeRDP SDL X11 A1/C contract (DRAFT)

**Status (2026-11-08):** Active, **provisional** replacement-design proposal, **not** an implementation or native-test authorization. The maintainer **aborted A2 Stage 1** because it would require carrying a downstream FreeRDP C++ patch for a retiring Plasma X11 session. The renamed [A2 addendum](step1.5c5d-sdl-x11-a2-contract-addendum-ABORTED.md) is historical research only; its accepted Stage 0 test remains a valid synthetic research artifact, **not** A1/C acceptance. Increment 1, native-Wayland registration without placement, remains **ACCEPTED and unchanged**. Increment 2 remains **OPEN**.

This document is subordinate to [governing §5A](Step1.5c5_implementation_scope.md#5a-increment-15c5d--managed-rdp-implementation), with the narrowly scoped Increment 2 exception defined in §5 below. Follow the current [HANDOFF](HANDOFF.md) and explicit maintainer prompt for actual authorization. **No patching FreeRDP, SDL or KWin; no new application-side proof emitter.**

## 1. Goal and supported boundary

Identify the **persistent normal SDL FreeRDP desktop viewer** among marked X11 windows sharing a launched PID, application class and exact title marker, using **unmodified upstream FreeRDP** and the existing `joetoo-kwin` resident/broker observation path. Register the chosen **KWin UUID only**, without moving, focusing, stacking or placing the window. A correct registration does **not** claim NLA completion, GDM readiness, a successful remote session or first rendered frame.

- Restrict the experiment to **native Plasma/KWin X11 on `gmki91`**, stock SDL FreeRDP 3.32.1 and the installed SDL/KWin combination. Verify actual versions rather than assuming them; this initial profile does **not** automatically encompass XWayland under Plasma Wayland.
- Preserve the accepted native-Wayland v1 and generic/TigerVNC behavior exactly. Any later X11 profile must be explicit, opt-in and fail closed for unsupported combinations; never infer it silently from DISPLAY or a title.
- Retain existing launcher ownership, ProcessFD where available, parent/child/start/executable evidence, trusted evidence log, observation source/revision, baseline/event floor, bounded histories and deadline/cleanup rules. No PID-only, title-only, class-only or last-window selector.
- Use existing resident window events. No new continuously running observer, patched-client property, synthetic READY record, transaction-local A2 resolver, or user-input capture.

## 2. Candidate A1 — stock-renderer policy and comparison

**Hypothesis, not finding:** FreeRDP/SDL renderer configuration may influence creation and native-X11 replacement of the initial marked normal window. Prior source review made renderer-induced recreation plausible, but did **not** establish its cause or show a supported stock option that eliminates it.

Proposed centrally user-configurable `rdp_x11_renderer` accepts exactly `auto` or `software`, only for the explicit legacy native-KWin-X11 profile. Renderer policy is independent of Candidate C and **is not identity proof**:

| Mode | Managed child's environment only |
| --- | --- |
| `auto` | Use stock SDL renderer selection: remove inherited `SDL_RENDER_DRIVER` and `SDL_FRAMEBUFFER_ACCELERATION` keys from the spawned environment. Do not pass empty values. |
| `software` | Set both `SDL_RENDER_DRIVER=software` and `SDL_FRAMEBUFFER_ACCELERATION=0`. |

Construct a separate child environment; never mutate the parent/system environment or accepted Wayland/generic/VNC settings. `auto` does not guarantee GPU acceleration. `software` does not disable the remote host GPU or all FreeRDP protocol acceleration. Performance costs remain **unmeasured**, especially for demanding video. Neither mode is infallible, and no silent renderer fallback is permitted.

The Nov 8 software trial is qualified feasibility evidence (§6); the next single stock/default-renderer comparison is maintainer-only Gate N2. Record actual renderer/backend, per-UUID lifecycle/marker evidence, diagnostic gaps and graphical usability. Absence of replacement in one run proves neither renderer causation nor universal viewer-role correctness. **C applies in both modes**, not only if A1 fails. No upstream instrumentation, client rebuild or security-policy change is implied.

## 3. Candidate C — one bounded X11-only persistence selector

Candidate C is a **maintainer-acknowledged best-effort heuristic in both `auto` and `software` modes**, not an exact FreeRDP initialization proof. A short-lived temporary window may share all normal positive identity fields with the persistent viewer. The Nov 5 baseline recorded a marked 20 ms predecessor and 72.9 s successor; these observed lifetimes support evaluation, not a universally safe default.

A prospective X11-only selector may:

1. Arm the existing registration transaction **before** the direct child's launch, retaining exact source, baseline and observed birth/removal history; require a positively observed new UUID, live normal window, owned child, actual `x11` backend, expected PID/application identity and exact generated marker. An `added` signal alone or a delayed title update alone is insufficient.
2. On first **full qualification** of each candidate UUID, capture a broker-local `time.monotonic()` eligibility timestamp. A late marker starts eligibility at its qualification time, **not** retroactively at birth. Persist identity across polls for that *same UUID*; do not restart the clock on every poll.
3. Keep watching all relevant lifecycle events during the interval. Retain short-lived marked **X11** predecessors as explicit removed tombstones rather than failing merely because one disappeared. Never erase a contradictory mutation, drop a source/revision gap, or reclassify a preexisting UUID as new.
4. At or after the configured threshold, recheck *the same live UUID* against the newest complete state, event history, exact marker, class/PID, source, child and owner. Reject simultaneously eligible live competitors, missing/evicted history, changed identity and unresolved replacement; a subsequent UUID must never silently inherit another UUID's timer or registration.
5. Register **only without placement**, within the original transaction deadline. Once registered, do not automatically retarget on a later replacement/removal. Preserve stable failure/terminal states and inert late callbacks.

**Known failure mode:** A fully qualifying marked temporary window lasting **600 ms** may be wrongly registered at **500 ms** before its replacement appears. Retain this counterexample as a required test and residual risk in both modes; later replacement must never be silently re-enrolled. A longer configurable interval and trials do **not** eliminate the possibility. If the evidence or residual risk is unacceptable, stop for maintainer review rather than claiming exact proof or automatically switching renderer or adopting the separately gated B fallback.

## 4. One timer, configuration and event ordering

Two independent centrally user-configurable settings are proposed for future integration in the existing configuration template's private SDL/RDP section (`key=value` syntax): `rdp_x11_renderer` (§2) and the **single X11 eligibility interval**:

`rdp_x11_identity_settle_ms=500`

- This is the **only dwell/eligibility interval for X11 SDL registration in either renderer mode**, starting at first full qualification of a particular new exact-marked normal UUID (§3), not automatically at birth. It runs **concurrently** with lifecycle observation, backend/child evidence checks and the existing polling/watchdog, **not** as a blocking sleep and **not** before an additional `PollCorrelation()` 500 ms gate.
- `PollCorrelation()` currently measures its own *diagnostic* uniqueness interval from the first qualifying **poll** and does not enroll/authorize SDL registration. Candidate C should use one broker-owned candidate timestamp in the registration path; do **not** call diagnostic `PollCorrelation()` as a second decision or chain equal deadlines. If future shared state is considered, it must consume the **same timestamp**, not start a new timer.
- Validate one user-configurable integer value from the established configuration template, with a documented bounded range and effective deadline compatibility. **500 ms is an initial experimental value, not yet an evidence-validated default.** A future maintainer may tune it without source edits. Prefer the existing scheduled event loop; no busy-wait, repeated full-window scan outside existing bounds, renewed registration lease or new always-running timer.
- Eligibility is a **`now >= first_qualified_at + settle_interval`** condition followed by fresh identity/history validation, not a race between two 500 ms expirations. Completion may occur on the next existing poll/event-loop dispatch; that scheduling jitter is not a second intentional delay. Synchronous processing/ordering assumptions and queued removals must be tested explicitly.
- The original Begin/registration deadline and history/event limits still dominate; a caller cannot extend them by modifying the settle setting or by supplying another candidate.

## 5. Explicit narrow exception to governing §5A

This section records the **only narrow X11 exception** adopted in governing §5A's Increment 2 subsection. It applies in **both renderer modes**; this subordinate DRAFT grants no implementation authority and cannot broaden that exception.

> For the explicitly selected **legacy SDL FreeRDP / native KWin X11 profile only**, permit a **bounded, centrally configurable, monotonic candidate-persistence interval**, used **concurrently** with the existing broker observation and ownership checks, as one component of an *empirically supported, best-effort* viewer-role selector. It must **not** be followed by an additional diagnostic correlation wait. Retain complete birth/removal history, unique live UUID requirements, exact PID/application/marker/source/owner/child evidence and fresh final validation; fail closed on source/history loss, contradictions and unresolved live competitors. A window's survival does **not** prove renderer completion. Do not change native-Wayland v1, silently substitute a UUID, or authorize placement, client patches or security-policy changes.

This exception explicitly replaces the prior stricter X11 expectation of independently proven persistent-role identity **for this opt-in legacy profile only**. It does **not** relax requirements for exact ownership and identity of whichever UUID is actually registered.

## 6. Minimal evidence and implementation gates

**Gate F — ACCEPTED read-only feasibility:** The Nov 5 pair (`Fm6EBB11` / `7DZi9Tfj`) recorded a 20 ms marked temporary predecessor and 72.9 s persistent successor. These are observed KWin wall-clock capture intervals, corroborated by X11 monotonic discovery/removal timing, not broker full-qualification timestamps. No sequential diagnostic `PollCorrelation()` wait is required by the SDL registration path. Supported stock SDL renderer hints justify a bounded comparison, not an identity guarantee.

**Gate N — software trial ACCEPTED only as provisional feasibility evidence:** See [the exact Nov 8 evidence record and original console output](step1.5c5d-a1-software-renderer-native-evidence-2026-11-08.md). The stock client confirmed `x11` and `software`, one observed marked normal persistent UUID and two earlier **unmarked** window generations. Main KWin transport was intact; the X11 companion reported **one discovery gap**. Client exit **131** followed operator titlebar closure; the parent proof result was 0, not a clean-zero client exit. Neither exhaustive coverage, universal selector correctness nor renderer causation was proven; demanding-video performance was not measured.

**Gate N2 — next, single default-renderer comparison, authorized for the maintainer only:** Unset both SDL renderer hints with `env -u SDL_RENDER_DRIVER -u SDL_FRAMEBUFFER_ACCELERATION`, use `RDP_DIAG_SECONDS=900` and the existing diagnostic runner. Codex must not execute it. Record actual renderer/backend from `client.log`, exact marker/PID and UUID/XID lifetimes, diagnostic completeness/gaps, graphical usability, client exit and private archive names/checksums. No broker/resident restart or `mw` operations between baseline and result; keep NLA/TLS policy unchanged. This is feasibility, not managed-registration acceptance.

**Gate I — NOT YET AUTHORIZED, X11-only broker/launcher implementation:** Review N2 and aligned scope before a separately bounded source/config/test grant. Test both renderer policies, child-only environment isolation, temporary window disappearance, the 600 ms predecessor counterexample, late marker, candidate overlap, replacement after threshold, competing viewers, evicted/reordered history, wrong PID/class/backend/source/owner, expiry/cancel and intact Wayland/VNC/generic tests. Mocked tests are not native proof.

**Gate A — NOT YET AUTHORIZED, separate `gmki91` managed acceptance:** Demonstrate stock-client selection of the actual persistent UUID in both renderer modes without premature registration or placement, with measured threshold, sufficient repeated runs and explicit residual heuristic risk. Do not claim a universal no-false-positive guarantee or that one observed success establishes robustness. Increment 2 remains OPEN until maintainer review.

**Out of scope:** A2 client patch, A1 reinterpretation as an upstream source change, A2 READY/nonce/XCB workers, automatic B user-interaction gate, placement, configured `-o -f CONFIG`, TLS/NLA/certificate changes, installation/packaging and production deployment.
