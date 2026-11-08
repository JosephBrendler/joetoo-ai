# Step 1.5c.5d / Increment 2 — Stock-FreeRDP SDL X11 A1/C contract (DRAFT)

**Status (2026-11-08):** Active, **provisional** replacement-design proposal, **not** an implementation or native-test authorization. The maintainer **aborted A2 Stage 1** because it would require carrying a downstream FreeRDP C++ patch for a retiring Plasma X11 session. The renamed [A2 addendum](step1.5c5d-sdl-x11-a2-contract-addendum-ABORTED.md) is historical research only; its accepted Stage 0 test remains a valid synthetic research artifact, **not** A1/C acceptance. Increment 1, native-Wayland registration without placement, remains **ACCEPTED and unchanged**. Increment 2 remains **OPEN**.

This document is subordinate to [governing §5A](Step1.5c5_implementation_scope.md#5a-increment-15c5d--managed-rdp-implementation), with the narrowly scoped Increment 2 exception defined in §5 below. Follow the current [HANDOFF](HANDOFF.md) and explicit maintainer prompt for actual authorization. **No patching FreeRDP, SDL or KWin; no new application-side proof emitter.**

## 1. Goal and supported boundary

Identify the **persistent normal SDL FreeRDP desktop viewer** among marked X11 windows sharing a launched PID, application class and exact title marker, using **unmodified upstream FreeRDP** and the existing `joetoo-kwin` resident/broker observation path. Register the chosen **KWin UUID only**, without moving, focusing, stacking or placing the window. A correct registration does **not** claim NLA completion, GDM readiness, a successful remote session or first rendered frame.

- Restrict the experiment to **native Plasma/KWin X11 on `gmki91`**, stock SDL FreeRDP 3.32.1 and the installed SDL/KWin combination. Verify actual versions rather than assuming them; this initial profile does **not** automatically encompass XWayland under Plasma Wayland.
- Preserve the accepted native-Wayland v1 and generic/TigerVNC behavior exactly. Any later X11 profile must be explicit, opt-in and fail closed for unsupported combinations; never infer it silently from DISPLAY or a title.
- Retain existing launcher ownership, ProcessFD where available, parent/child/start/executable evidence, trusted evidence log, observation source/revision, baseline/event floor, bounded histories and deadline/cleanup rules. No PID-only, title-only, class-only or last-window selector.
- Use existing resident window events. No new continuously running observer, patched-client property, synthetic READY record, transaction-local A2 resolver, or user-input capture.

## 2. Candidate A1 — rapid stock-renderer experiment

**Hypothesis, not finding:** FreeRDP/SDL renderer configuration may influence creation and native-X11 replacement of the initial marked normal window. Prior source review made renderer-induced recreation plausible, but did **not** establish its cause or show a supported stock option that eliminates it.

**Read-only feasibility gate first:** Check the *actual installed binary* and locally retained FreeRDP/SDL sources or `--help` for documented, supported settings that could affect the renderer/acceleration/window-creation path. Record exact options and versions. Do **not** invent a renderer option, alter negotiated RDP security, rebuild the client, or suggest a downstream patch.

**Optional maintainer-native gate, separately approved:** Compare the stock baseline with at most the justified stock configuration(s), using existing bounded lifecycle diagnostics on `gmki91`. Record per-UUID `added`/`removed` events, order, monotonic time where available, PID/class/marker, whether an initial native-X11 generation is replaced, graphical correctness and whether the eventual viewer remains usable. **Absence of replacement in a few runs is supporting empirical evidence, not a guarantee of future role identity.**

If the installed client has no supported applicable option, or a quick comparison does not materially improve identity stability, **close A1 as unhelpful and evaluate C**. Do not turn A1 into new upstream-instrumentation work.

## 3. Candidate C — one bounded X11-only persistence selector

Candidate C is a **maintainer-acknowledged best-effort heuristic**, not an exact FreeRDP initialization proof. A short-lived temporary window may share all normal positive identity fields with the persistent viewer. The retained original observations show such a pair; its actual lifetimes must be measured before selecting a default.

A prospective X11-only selector may:

1. Arm the existing registration transaction **before** the direct child's launch, retaining exact source, baseline and observed birth/removal history; require a positively observed new UUID, live normal window, owned child, actual `x11` backend, expected PID/application identity and exact generated marker. An `added` signal alone or a delayed title update alone is insufficient.
2. On first **full qualification** of each candidate UUID, capture a broker-local `time.monotonic()` eligibility timestamp. A late marker starts eligibility at its qualification time, **not** retroactively at birth. Persist identity across polls for that *same UUID*; do not restart the clock on every poll.
3. Keep watching all relevant lifecycle events during the interval. Retain short-lived marked **X11** predecessors as explicit removed tombstones rather than failing merely because one disappeared. Never erase a contradictory mutation, drop a source/revision gap, or reclassify a preexisting UUID as new.
4. At or after the configured threshold, recheck *the same live UUID* against the newest complete state, event history, exact marker, class/PID, source, child and owner. Reject simultaneously eligible live competitors, missing/evicted history, changed identity and unresolved replacement; a subsequent UUID must never silently inherit another UUID's timer or registration.
5. Register **only without placement**, within the original transaction deadline. Once registered, do not automatically retarget on a later replacement/removal. Preserve stable failure/terminal states and inert late callbacks.

**Known failure mode:** If a temporary marked window survives the threshold and its replacement appears later, a dwell-only implementation can register the wrong UUID. A longer configurable interval and trials reduce observed risk; they do **not** eliminate that possibility. If the measured evidence cannot support a reasonable threshold, or the observed wrong-UUID risk is unacceptable, **NO-GO for C** and reconsider the documented interaction-gated B fallback rather than claiming exact proof.

## 4. One timer, configuration and event ordering

Proposed **single centrally configured X11 selector parameter** (illustrative until explicitly approved):

`rdp_x11_identity_settle_ms = 500`

- This is the **only dwell/eligibility interval for X11 SDL registration**. It runs **concurrently** with lifecycle observation, backend/child evidence checks and the existing polling/watchdog, **not** as a blocking sleep and **not** before an additional `PollCorrelation()` 500 ms gate.
- `PollCorrelation()` currently measures its own *diagnostic* uniqueness interval from the first qualifying **poll** and does not enroll/authorize SDL registration. Candidate C should use one broker-owned candidate timestamp in the registration path; do **not** call diagnostic `PollCorrelation()` as a second decision or chain equal deadlines. If future shared state is considered, it must consume the **same timestamp**, not start a new timer.
- Validate one user-configurable integer value from the established configuration template, with a documented bounded range and effective deadline compatibility. **500 ms is an initial experimental value, not yet an evidence-validated default.** A future maintainer may tune it without source edits. Prefer the existing scheduled event loop; no busy-wait, repeated full-window scan outside existing bounds, renewed registration lease or new always-running timer.
- Eligibility is a **`now >= first_qualified_at + settle_interval`** condition followed by fresh identity/history validation, not a race between two 500 ms expirations. Completion may occur on the next existing poll/event-loop dispatch; that scheduling jitter is not a second intentional delay. Synchronous processing/ordering assumptions and queued removals must be tested explicitly.
- The original Begin/registration deadline and history/event limits still dominate; a caller cannot extend them by modifying the settle setting or by supplying another candidate.

## 5. Explicit narrow exception to governing §5A

This section specifies the *only proposed exception* to §5A's earlier blanket rejection of fixed-delay selectors. It is valid only when the governing scope's matching Increment 2 exception is reviewed and adopted; this DRAFT **cannot supersede §5A on its own**.

> For the explicitly selected **legacy SDL FreeRDP / native KWin X11 profile only**, permit a **bounded, centrally configurable, monotonic candidate-persistence interval**, used **concurrently** with the existing broker observation and ownership checks, as one component of an *empirically supported, best-effort* viewer-role selector. It must **not** be followed by an additional diagnostic correlation wait. Retain complete birth/removal history, unique live UUID requirements, exact PID/application/marker/source/owner/child evidence and fresh final validation; fail closed on source/history loss, contradictions and unresolved live competitors. A window's survival does **not** prove renderer completion. Do not change native-Wayland v1, silently substitute a UUID, or authorize placement, client patches or security-policy changes.

This exception explicitly replaces the prior stricter X11 expectation of independently proven persistent-role identity **for this opt-in legacy profile only**. It does **not** relax requirements for exact ownership and identity of whichever UUID is actually registered.

## 6. Minimal evidence and implementation gates

**Gate F — read-only feasibility (next Codex task):** Inspect the existing `PollCorrelation()` and registration paths, previously retained X11 archives (begin with the November 5 successful activity/diagnostic pair), and the stock client's actual supported rendering options. Compute window lifetimes *only if the records contain defensible comparable timestamps*; distinguish broker receipt time from native creation time. Evaluate thresholds of 250 and 500 ms and identify any longer-lived predecessor, missing timing, or contradictory trace. Provide a concise A1 GO/NO-GO and C GO/NO-GO, plus at most a small separately gated native A1 test recipe. **No source or document edits and no native execution.**

**Gate N — optional maintainer-operated A1 native comparison:** Only after separate authority and a recorded baseline; no broker/resident restart or `mw` operations between the recorded baseline and result. Keep test credentials/logs private; no TLS/NLA weakening or FreeRDP patch.

**Gate I — separately approved X11-only broker implementation:** Only after the feasibility decision. Smallest justified broker/launcher/config/test changes; exact path permissions in a new prompt. Test temporary window disappearance, predecessor longer than threshold, late marker, candidate overlap, replacement after threshold, competing viewers, evicted/reordered history, wrong PID/class/backend/source/owner, expiry/cancel and intact Wayland/VNC/generic tests. Mocked tests are not native proof.

**Gate A — separately approved `gmki91` acceptance:** Demonstrate stock-client selection of the actual persistent UUID without premature registration or placement, with measured threshold, sufficient repeated runs and explicit residual heuristic risk. Do not claim a universal no-false-positive guarantee or that one observed success establishes robustness. Increment 2 remains OPEN until maintainer review.

**Out of scope:** A2 client patch, A1 reinterpretation as an upstream source change, A2 READY/nonce/XCB workers, automatic B user-interaction gate, placement, configured `-o -f CONFIG`, TLS/NLA/certificate changes, installation/packaging and production deployment.
