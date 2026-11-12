# Step 1.5 — Active task dispatcher

**Current status (2026-11-11): Step 1.5c.5d CLOSED, ACCEPTED AND MERGED.** All Increment 1–5 acceptance decisions stand. PR [#29](https://github.com/JosephBrendler/joetoo-ai/pull/29) merged into `main` at **`3e9c4bf311bc65b32d332a00d3b50163a9043303`** (GitHub merge commit, 2026-11-11). Maintainer independently reported `gmki91` on clean, up-to-date `main` and a **good GitHub GPG signature** on that commit. No remaining Step 1.5c.5d implementation or native-security acceptance gate.

**Next milestone:** Step **1.5d** — integrate the existing planned **`-L` (single-window launch) and `-l` (managed-window listing)** CLI actions; perform cross-feature integrated native X11/Wayland regression. Current source still returns `not yet integrated` for both actions. This is **not** a reopening of managed RDP, nor an authorization to start the next milestone by reading HANDOFF.

**Repository:** `JosephBrendler/joetoo-ai`  
**Accepted baseline:** `main` at merge commit `3e9c4bf311bc65b32d332a00d3b50163a9043303` (verify fresh remote/local HEAD before starting work)  
**Preparation branch:** `task/joetoo-kwin-step1.5d-integrated-regression` created from that merge commit for **handoff documentation only**. Maintainer may use the same task branch for authorized 1.5d work after reviewing its exact current state.  
**Project:** `workspace/projects/joetoo-kwin/`

## Accepted Step 1.5c.5d outcome

- **Increments 1–3 accepted:** native Wayland/X11 SDL FreeRDP identity and exact-UUID registration, bounded automatic placement, smart-sizing and original-viewer lifecycle. Historical failures and conservative X11 persistence-heuristic limits remain recorded as evidence, not reopened tasks.
- **Increment 4 Stages 1–4 accepted:** serial configured `-o` RDP alongside Konsole/Dolphin/TigerVNC, bounded readiness and known-clean failure continuation, exact registered UUID and placement, initial stacking/focus, Stage 4 configuration layering, optional non-root `eselect joetoo-kwin` user profiles, templates/reference and severity-aware configuration output. Accepted native X11/Wayland evidence and full regression remain in the task index.
- **Increment 5 accepted:** `rdp_security_protocol=nla|negotiate` (default `nla` -> `/sec:nla`; `negotiate` -> omit `/sec:`) and `rdp_certificate_policy=strict|prompt` (default `strict` -> `/cert:deny`; `prompt` -> omit `/cert:`). Both are validated, layered, displayed under `-vc` and documented. Codex reported **185 focused Python / 919 full Python / 161 JavaScript PASS**, syntax, ShellCheck and diff checks (report, not independently rerun in this handoff).
- Maintainer native **strict trusted connection** on `gmki91` X11: actual `/sec:nla /cert:deny` process argv, GNOME GDM visible, exact `win-001` UUID `255d1e14-7890-439d-8a96-fe1bd24266ce`, desktop 19 slot 1, successful placement/stacking. Previously observed production RDP interoperability on `q552u01` Wayland remained accepted.
- Maintainer native **negative certificate-identity test** on `gmki91`: accessing the same private-CA-signed GRD system Remote Login server by `192.168.62.171:3389` (not a certificate SAN) produced `CERTIFICATE NAME MISMATCH`, strict automatic denial, `certificate not trusted, aborting`, and `ERRCONNECT_TLS_CONNECT_FAILED`. The pending client exited; broker terminal failure was verified, child reaped, resources released, `cleanup_confirmed=true`, `continuation_eligible=true`, no uncertain requests, and the trusted desktop-19 viewer remained intact. Broker `child_identity_rejected` labels the terminal process outcome, **not** the TLS reason; FreeRDP's own log establishes that reason.
- Evidence: [final Increment 5 native acceptance](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md), [pre-policy production native X11/Wayland evidence](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md), [increment evidence index](README.md). Remote-session status in local registration records remains `unverified`, even when the greeter is visible. Exact negotiated TLS version/cipher is not established. Historical test data must not be mistaken for policy-downgrade acceptance.

## Next actor and Step 1.5d preparation

**Current actor: maintainer**, followed by a separately issued bounded Codex Step 1.5d assignment. A [focused Step 1.5d Codex prompt](step1.5d-codex-task-DRAFT.md) is prepared for review; it does not itself authorize implementation. The old PR-readiness / Increment 5 implementation drafts are historical, not current tasks.

1. **Local Git readiness:** on `gmki91`, the maintainer already confirmed clean `main` at the merge commit. On `q552u01`, fetch/prune, inspect local changes, fast-forward `main`, then switch off the merged task branch; remove that local task branch only if merged and clean. The old remote task branch may be deleted after confirming PR #29 and merge history; do not force-delete a unique/unmerged branch. Runtime services, managed windows and OpenRC state do not need resetting for Git cleanup.
2. **Step 1.5d source contract:** read current [architecture milestone table](../ARCHITECTURE.md) and the actual CLI `-L`/`-l` stubs and existing launcher/read-only broker interfaces. Establish minimal argument/target/selection semantics for one-window `-L`, presentation/filters and meaning of `-l`, and truthful failed/partial outcomes. Reuse `-o` preflight, confirmation, configured modes, broker identity and already accepted security rules; **do not infer that `-L` is a shorthand for a whole `-o` file**. If an essential UX choice remains open, put one concise source-grounded proposal before the maintainer; avoid inventing a new architecture or submilestones.
3. **Integrated regression:** make a test matrix of actual accepted Step 1.5 operations across `gmki91` native Plasma X11 and `q552u01` native Plasma Wayland: Konsole SSH placeholder/continuity, Dolphin local/SFTP, TigerVNC SSH tunnel, SDL RDP strict security, placement/desktop membership and stacking/focus, existing slot reservations/Busy outcomes, clean failure continuation and unresolved-failure stop, independent remote-session vs window status. Reuse accepted tests; add only gaps introduced by `-L`/`-l` and cross-feature combinations. Native operations remain maintainer-controlled.
4. **Task authorization:** once the maintainer agrees to the bounded Step 1.5d behavior, Codex may implement and headlessly test on a fresh branch based on accepted `main`, report its diff and proposed native checks for review. This document does not itself authorize implementation, commits, pushes, PRs, native testing or host changes.

**Keep out of Step 1.5d unless explicitly revised:** managed `-a/-d/-x` (Step 1.6), checkpoint/restart reconciliation (1.7), snapshot/recovery (1.8), official Gentoo packaging and full `eselect` installation (1.9), new viewer frameworks/clients, RDP/VNC worker normalization, Option D asynchronous lifecycle, or unnecessary rework of accepted Increment 5.

**Packaging backlog for Step 1.9:** ebuild should generate `/etc/joetoo-kwin/BUILD` from `$PVR`; CLI should source its own version file, rather than `joetoolkit`'s BUILD, with a sensible source-checkout fallback. No packaging changes authorized here.

**Boundaries:** comply with repository/project `AGENTS.md` and actual accepted architecture; `joetoo` / `joetoo-upstream` are advisory/read-only for AI. Protect exact UUID ownership, fail-closed handling and existing user-managed windows. A PR merge does not itself prove every host's checkout or runtime installation is updated.

## References

- [Step 1.5 history / evidence index](README.md)
- [Architecture and 1.5d milestone](../ARCHITECTURE.md)
- [Step 1.5c.5 implementation scope (historical 1.5c.5 detail)](Step1.5c5_implementation_scope.md)
- [Final 1.5c.5d / Increment 5 native acceptance](step1.5c5d-increment5-final-native-acceptance-2026-11-11.md)
- [Pre-strict-policy X11/Wayland evidence](step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md)
- [Increment 4 Stage 4 acceptance](step1.5c5d-increment4-stage4-native-acceptance-2026-11-11.md)
- [PR #29 — merged milestone](https://github.com/JosephBrendler/joetoo-ai/pull/29)
- [Draft Step 1.5d Codex implementation assignment](step1.5d-codex-task-DRAFT.md)
