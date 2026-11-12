# Step 1.5 — Active task dispatcher

**Current status (2026-11-12): Step 1.5d FUNCTIONALLY ACCEPTED BY THE MAINTAINER; publication/merge pending.** The accepted feature consists of `-L` one managed `over` launch, collision-free logical slot selection, broker-verified one-shot raise preserving existing windows, and read-only `-l` managed inventory. Native X11 on `gmki91` and native Wayland on `iota01` succeeded; the critical multi-window raise scenario was demonstrated on both. The maintainer explicitly accepted Step 1.5d following these results. See [the Step 1.5d native acceptance and regression record](step1.5d-native-acceptance-2026-11-12.md).

**Next actor: Codex, but only when separately instructed, for one tightly scoped TEST-FIXTURE hardening round.** A single isolated libxcb/socketpair event-delivery test intermittently failed in the full `iota01` Python suite; it passed eleven successive isolated reruns. Codex should implement a bounded synchronization/acknowledgement in the **test fixture**, avoiding arbitrary sleeps and preserving production `xcb_poll_for_event()` nonblocking semantics. Rerun focused/full headless tests and deliver patch/evidence for maintainer review. **Do not confuse the test-only cleanup gate with reopening Step 1.5d functional acceptance.** Do not commit, push, open a PR, merge, or perform native-host actions unless the maintainer explicitly authorizes them separately.

**Accepted predecessor:** Step 1.5c.5d CLOSED, ACCEPTED AND MERGED, PR [#29](https://github.com/JosephBrendler/joetoo-ai/pull/29), `main` merge commit `3e9c4bf311bc65b32d332a00d3b50163a9043303` (2026-11-11). All five RDP implementation increments and existing strict NLA/certificate/security acceptance remain closed and must not be reopened by this work.

**Repository:** `JosephBrendler/joetoo-ai`  
**Project:** `workspace/projects/joetoo-kwin/`  
**Active Step 1.5d branch:** `task/joetoo-kwin-step1.5d-integrated-regression` (unmerged; verify exact HEAD, local status and origin before altering source).  
**Authoritative architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md).  
**Task/evidence index:** [README.md](README.md).

## Accepted 1.5d contract and demonstrated behavior

- CLI `-L DESKTOP PROGRAM MODE TARGET [LAYER]` accepts distinct operands and uses existing authoritative configuration/validators, confirmation, managed identity, placement, and backend/security policy. On `-L` only, omitted layer defaults to `over`, explicit `over` works, and `panel`/`under` are rejected before launch as **not implemented yet**. Existing configured `-o` retains its implicit `panel` and accepted `under`/`panel`/`over` layers.
- `-L` reserves exactly one unused logical slot in 1..256, respecting retained missing reservations. It launches one new managed window and verifies registration and placement by exact UUID. It performs **one-shot raise of the new window above existing normal windows** on its desktop; no existing peer geometry changes, panel reflow, recascade, generalized managed-ID reflow transaction, or persistent keep-above.
- `-l` is read-only `ListManaged` inventory, sorted and fixed width, showing full IDs/UUID, presence, placement and retained missing reservations without adopting unregistered observed windows.
- `single_raise_protocol=1` is additive/opt-in in the existing initial-layout exchange; other `-o` paths and accepted broker/resident semantics remain unchanged. Positive broker completion is evidence of its stack/peer checks, not a claim about remote RDP authentication.
- `gmki91` X11: default and explicit `over`, desktop 11 slot 3 and desktop 12 slots 1/2 with 1/1 successful stacking, inventory, and prelaunch rejection of `panel`/`under`. One early failed RDP mission was handled cleanly. Its relevant SDL log shows `ERRCONNECT_LOGON_FAILURE [0x00020014]`; exact original failure-to-log matching and specific credential cause are not conclusively established. A deliberate bad-password experiment reproduced the generic CLI failure pattern.
- `iota01` Wayland: 1024x600 built-in display and 1920x1080 external; configured dimensions adjusted from 1920x1080 to 1024x600. Successful Konsole/SSH: desktop 4 slot 1 (`win-001`), desktop 3 slot 1 (`win-002`), then desktop 3 slot 2 (`win-003`) above existing desktop-3 window, screenshot supplied. All reported completed 1/1 with registered UUID and broker-verified placement and initial stacking. Inventory displayed both earlier managed IDs in desktop order. This satisfies the main native Wayland single-raise acceptance case.
- Headless: earlier candidate `gmki91` 938 Python / 163 JavaScript PASS; later `iota01` full run **949 Python, one isolated XCB test failure; 163 JS PASS**. The precise failing assertion was `observer.drain(16) == []` versus expected `[('desktop', 123)]`. The same test then passed **11/11 isolated reruns** (one verbose, ten quiet). This is **not** a clean full-Python pass; a targeted fixture fix and full rerun remain a prepublication quality gate.
- A temporary `LC_CTYPE=en_US.UTF-8` in the interactive shell suppressed Qt warnings on `iota01`. The joetoo system locale baseline `LC_COLLATE=C`, `LC_CTYPE=C` must not be modified as part of this task; its intended interactive override can be investigated separately. No evidence attributes the isolated XCB failure to locale.
- Narrow timestamp / recognized NLA-console-diagnostic refinement has been discussed. The latest Wayland CLI already displays `[20261112-11:28:15] Launching ...`; do not assume every NLA diagnostic behavior is independently verified. **This handoff's next assignment is fixture hardening only**, not a second feature round.

## Immediate next steps / acceptance versus publication

1. **Maintainer decision recorded:** Step 1.5d accepted (2026-11-12); retain all actual successes, failures and uncertainty in the linked evidence file. Do not relabel any earlier failed full-suite run as passed.
2. **Codex focused fixture fix:** inspect `tests/test_vnc_identity.py::IdentityPrototypeTests.test_real_libxcb_receives_isolated_server_event` and the related `NativeObserver` test contract. The fake server thread sends a wire event in response to `GetInputFocus` after setup/select; test asserts immediately using nonblocking `xcb_poll_for_event()`. Confirm root cause; use deterministic, bounded test synchronization **for event arrival/readability**, not merely a sender-side write acknowledgement, and never change production poll semantics to satisfy a test. Ensure proper thread/socket teardown, timeout failure diagnostics, no real DISPLAY/GUI, and no indefinite waits. Add/adjust focused test(s), rerun full Python/JavaScript, syntax/lint/diff checks. Report exact totals, changed-file inventory and limitations. No runtime service installation/restart.
3. **Maintainer review:** inspect focused patch and complete regression results on the final candidate commit/working tree. Decide whether fixture is fixed or explicitly dispositioned. Record the tested Git SHA and post-fix evidence. Do not silently suppress, skip or xfail the test.
4. **Publication is subsequent and separately controlled:** maintainer explicitly authorizes any Codex commit/push to the existing branch; thereafter review PR/diff and explicitly authorize PR creation and merge. Update HANDOFF/README/evidence with final branch/merge SHAs and the accepted final regression results. Neither these documents nor the draft prompt grant Git publication authority.

## Non-goals and safety constraints

- **No more feature implementation under Step 1.5d acceptance** absent a new explicit maintainer decision. No `-L panel/under`, reflow, application-independent managed-ID geometry transactions, auto-adoption, background window enforcement, or new RDP auth/cert policy.
- Do not alter production libxcb observer's nonblocking `drain` contract or simplify its event-budget fail-closed behavior just to make an isolated fixture pass.
- Preserve accepted Step 1.5c.5d implementation, original local Bash/SSH continuity, exact UUID identity, broker source/lease/owner checks, cleanup gates, true status reporting, managed reservations and untouched peer windows.
- Do not edit `joetoo`/`joetoo-upstream` (advisory/read-only for AI). Honor project/repository `AGENTS.md` and scope limits.
- Distinct future work: Step 1.6 managed `-a/-d/-x`, 1.7 restart reconciliation, 1.8 snapshot/recovery, 1.9 Gentoo packaging. The 1.9 backlog includes `/etc/joetoo-kwin/BUILD` from ebuild `$PVR` and an appropriate CLI version source; not authorized now.

## Evidence and history

- [Step 1.5d native acceptance and regression evidence (2026-11-12)](step1.5d-native-acceptance-2026-11-12.md) — new authoritative acceptance record, including original error and repeat results.
- [Step 1.5d headless candidate and planned native checks](step1.5d-single-recipe-headless-candidate.md) — preacceptance source/candidate snapshot, **historical** status.
- [Earlier source review](step1.5d-managed-inventory-and-live-layout-review.md) — historical reflow analysis; revised no-reflow decision supersedes it.
- [Superseded Codex task](step1.5d-codex-task-DRAFT.md) — old reflow proposal; **do not execute**.
- [Step 1.5 history and evidence index](README.md)
- [Final Step 1.5c.5d Increment 5 acceptance](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md)
- [Pre-strict production native RDP evidence](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md)
- [Merged PR #29](https://github.com/JosephBrendler/joetoo-ai/pull/29)

**Interpretation rule:** older evidence and candidate documents accurately describe their own historical state but **cannot override this 2026-11-12 accepted milestone or the maintainer's subsequent explicit instructions**.
