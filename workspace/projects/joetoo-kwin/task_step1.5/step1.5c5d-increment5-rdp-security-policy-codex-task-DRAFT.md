# DRAFT Codex task — Increment 5 bounded RDP security-policy implementation

**Status:** Prepared for maintainer review/explicit issuance. This prompt is the requested next task, not evidence that implementation has happened. Remain on the current task branch; inspect worktree/status and current HEAD first, preserve user edits and drafts. No commits, pushes, PRs, merges, native-host operations or packaging changes without separately explicit maintainer authorization.

## Objective and authority

Finish Increment 5's **single bounded production-argument-policy correction** using existing Stage 4 configuration infrastructure. Maintainer decision (2026-11-11): built-in defaults **`rdp_security_protocol=nla`** and **`rdp_certificate_policy=strict`**; both user-overridable through existing, accepted system/user/selected profile/per-run plan/CLI precedence. The config display must show effective settings at **info** verbosity. Preserve the already accepted Increment 4 behavior and lifecycle; this is not a new stage or general redesign.

Read in order: `task_step1.5/HANDOFF.md`, `task_step1.5/step1.5c5d-increment5-production-native-security-evidence-2026-11-11.md`, `task_step1.5/step1.5c5d-increment5-security-native-closure-candidate.md`, `task_step1.5/README.md`, `task_step1.5/Step1.5c5_implementation_scope.md`, project `ARCHITECTURE.md`, actual Stage 4 short template and annotated configuration manual/reference and source/tests. Follow AGENTS.md. The candidate predates the new native results and does not supersede them.

## Required exact behavior

| Effective configuration | Value | Constructed SDL FreeRDP argv |
| --- | --- | --- |
| `rdp_security_protocol` | `nla` (built-in default) | One `/sec:nla` argument — **exclusive** NLA mode, **not** `/sec:nla:on` |
| `rdp_security_protocol` | `negotiate` | No `/sec:` argument — FreeRDP defaults, **NOT** `/sec:rdp` or `-nego` |
| `rdp_certificate_policy` | `strict` (built-in default) | One `/cert:deny` — refuse failed certificate validation with no exception dialog |
| `rdp_certificate_policy` | `prompt` | No `/cert:` argument — current stock FreeRDP trust/interactive handling |

Do **not** add `/tls:enforce:1.3`, `/cert:ignore`, arbitrary raw FreeRDP switches, individual security-bit toggles, new per-target grammar, passwords, or a third policy value. `/sec:tls` denotes TLS-only RDP security mode; NLA still relies on TLS internally. Security protocol choice, certificate verification, and TLS-version/cipher configuration are separate concepts. Verify the flags against the installed SDL FreeRDP version and existing launch tests before finalizing, but do not broaden scope.

## Implementation requirements

1. Implement these validated enum values in the established Stage 4 defaults/overrides, config reader and CLI path. Reject unknown, conflicting or malformed values **before spawning** a viewer. The current source uses a fixed argv builder and direct child; retain that guarantee and fixed `/usr/bin/sdl-freerdp` executable. Ensure same policy for supported production and development paths as appropriate to the existing shared builder, without changing existing exact-UUID lifecycle or backend handling. Inspect actual call graph; no untested secondary path.
2. Display **effective** `rdp_security_protocol` and `rdp_certificate_policy` in `show_config` at `$info` verbosity (including `-vc`), respecting the previously accepted notice/info/debug semantics and profile precedence. Do not print secrets. Check `-c` dry run validates policy without network or launch.
3. Update both the **short configuration template** and the **annotated configuration manual/reference** (locate the real files rather than invent paths). Put inline comments beside the variables that show each permitted value and its literal FreeRDP argv mapping, including when **no argument** is supplied. Include the four-row table above in the manual, and explanatory text that `negotiate` ≠ `/sec:rdp`, `nla` ≠ `/sec:nla:on`, NLA still uses TLS, and `/tls:*` is a separate dimension. State that `prompt` is a user-chosen, less restrictive behavior; `strict` rejects untrusted certs without an exception prompt. Preserve existing Stage 4 config layering, reference style, and instructions for optional `eselect` profiles.
4. Add focused tests for every mapping, omitted-argument cases, defaults and valid overrides at each supported layer, bad-value rejection, no argv injection, validation-only `-c`, and visibility at info while preserving quiet/debug display contracts. Extend existing tests rather than creating a parallel config system. Check path-specific behavior on X11 and Wayland insofar as covered by headless tests. Regression-test certificate rejection and process supervision using controlled mocks where appropriate; do not claim a mock proves real TLS negotiation.
5. Run applicable focused and full Python/JavaScript/ShellCheck (or `validate_scripts joetoo-kwin -l`) tests available in the environment; preserve exact commands, outputs, counts and failures. Use `git diff --check`. Do not modify the underlying broker, OpenRC integration, VNC, GNOME server, PKI, TigerVNC, X11 heuristic, Windows lifecycle or upstream FreeRDP unless a demonstrated narrow dependency is reported first.
6. Report changed files, current HEAD/worktree status, before/after CLI argv examples, output of `-c`/`-vc`, test evidence and any compatibility issue. Do not declare Increment 5 or Step 1.5c.5d accepted on headless results alone. Update the native evidence record **only** with actual new results; current successful X11/Wayland observations were obtained *before* these new strict defaults existed.

## Native maintainer acceptance after implementation (recommendations, not permission to execute)

Use existing approved `raspiubuntu401.brendler:3389` server and CA; test on one native host after updating/installing the candidate, verify `-vc` shows `nla`/`strict`, confirm exact launch flags (by safe process inspection or private diagnostics) and reach GDM with no cert exception. Do **one** safe strict failure using the same server reached under a verified identity not covered by SAN; no client or server trust modifications, no unrelated address and no password submission to an unverified endpoint. Expected `/cert:deny` fails certificate verification **automatically**, without a user acceptance choice. Capture production status, worker/child lifecycle, broker registration and exact UUID; note that SDL window registration can happen before certificate verification, so a recorded managed window can be present/missing even when remote verification fails. Do not make zero registration/placement a false mandatory criterion. No full native X11/Wayland matrix rerun unless code changes specifically invalidate accepted registration behavior. A blocked prerequisite should be reported, not bypassed.

## Separately deferred packaging note (not implementation permission)

The currently displayed `BUILD` number originates from installed `joetoolkit`. For future `joetoo-kwin` ebuild, install `/etc/joetoo-kwin/BUILD` containing `BUILD="${PVR}"` at install time and have scripts source their own package BUILD with a suitable source-checkout fallback. Keep this in HANDOFF/README backlog; do not bundle it into Increment 5 security work.

## Stop/approval gate

Deliver a reviewable bounded patch/report. Do not commit/push or run native services without explicit approval. The maintainer will review implementation/tests and provide the final native checks; only then may the HANDOFF be changed to **Increment 5 ACCEPTED / Step 1.5c.5d CLOSED**.
