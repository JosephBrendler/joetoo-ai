# Step 1.9 — source maintainability/comment audit ledger

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Recorded 2026-11-27.** Source scope is derived from the project-root `MANIFEST`
(rechecked at `joetoo-ai` commit `0dd2ba3`), not an independent release
allowlist. This is an **ordered review checklist**, not a staging manifest.
See [HANDOFF.md](HANDOFF.md), [README.md](README.md), and
[the audit instructions](step1.9-source-stabilization_comment_audit_prompt.md).

Statuses: `PENDING` (not yet accepted), `INSPECTED`, `DRAFTED`, `VALIDATED`,
`ACCEPTED` (explicit maintainer semantic/inline-comment acceptance), and
`BLOCKED`. Lint/tests alone do not constitute `ACCEPTED`.

## Ordered production-source review

| # | Source relative to project root | Language / role | Status | Evidence / next action |
|---:|---|---|---|---|
| 1 | `joetoo-kwin` | Bash CLI | **ACCEPTED** | Maintainer acceptance in `f4e9ba92`, 2026-11-25 |
| 2 | `libexec/joetoo-kwin-plan-functions` | Bash planning library | **ACCEPTED** | Maintainer acceptance in `f4e9ba92`, 2026-11-25 |
| 3 | `libexec/joetoo-kwin-launch-functions` | Bash runtime launches | **ACCEPTED** | Reviewed by maintainer and committed as `98ce0d4`, 2026-11-27 |
| 4 | `libexec/joetoo-kwin-session.bashrc` | Bash session setup | **ACCEPTED** | Reviewed by maintainer and committed as `98ce0d4`, 2026-11-27 |
| 5 | `eselect/joetoo-kwin.eselect` | Gentoo eselect module | PENDING | `configs/` functional change committed/pushed as `0dd2ba3`; **separate** inline-comment audit/acceptance pending; see selector evidence |
| 6 | `user-init.d/joetoo-kwind` | OpenRC user-service script | PENDING | Audit service config layering and lifecycle comments |
| 7 | `libexec/joetoo-kwin-exposure.py` | Python | PENDING | Audit contracts and calculations |
| 8 | `libexec/joetoo-kwind` | Python D-Bus broker | PENDING | Audit broker state, registration, IPC and failure paths |
| 9 | `libexec/joetoo_kwin_launch_resources.py` | Python | PENDING | Audit launch-resource handling |
| 10 | `libexec/joetoo_kwin_registry.py` | Python | PENDING | Audit registry state and ownership |
| 11 | `libexec/joetoo_kwin_readonly.py` | Python | PENDING | Audit read-only queries; required in package inventory |
| 12 | `libexec/joetoo_kwin_managed_close.py` | Python | PENDING | Audit close and cleanup contracts |
| 13 | `libexec/joetoo_kwin_recovery.py` | Python | PENDING | Audit recovery state and validation |
| 14 | `libexec/joetoo_kwin_persistence.py` | Python | PENDING | Audit snapshots and filesystem safety |
| 15 | `libexec/joetoo_kwin_rdp_launch.py` | Python | PENDING | Audit RDP supervision and cleanup |
| 16 | `libexec/joetoo_kwin_rdp_target.py` | Python | PENDING | Audit target parsing/security |
| 17 | `libexec/joetoo_kwin_vnc_launch.py` | Python | PENDING | Audit VNC supervision and cleanup |
| 18 | `libexec/joetoo_kwin_vnc_target.py` | Python | PENDING | Audit target parsing/security |
| 19 | `libexec/joetoo_kwin_vnc_identity.py` | Python | PENDING | Audit viewer identity evidence |
| 20 | `libexec/joetoo_kwin_sftp_target.py` | Python | PENDING | Audit SFTP target parsing |
| 21 | `libexec/joetoo_kwin_sftp_advisory.py` | Python | PENDING | Audit nonblocking SFTP advice |
| 22 | `libexec/joetoo_kwin_sftp_capability.py` | Python | PENDING | Audit capability preflight |
| 23 | `joetoo-kwin-resident.js` | KWin JavaScript | PENDING | Audit observer, callbacks, KWin APIs and identity |
| 24 | `native/managed-close/adapter.cpp` | C++ | PENDING | Audit native effect and lifetime/ABI assumptions |
| 25 | `native/managed-close/x11.cpp` | C++ | PENDING | Audit X11/XWayland helper and protocol behavior |
| 26 | `native/managed-close/channel.h` | C++ header | PENDING | Audit shared native declarations and contracts |

**Scope accounting:** 4 accepted of 26 production code files; 22 remain
without recorded maintainer acceptance. `native/managed-close/CMakeLists.txt`
needs related build/installation commentary review alongside the C++ files;
`native/managed-close/metadata.json` gets separate accuracy/provenance review.
Test fixtures, archived POCs and unshipped tools are not counted as production
source. Do not infer audit completion from a prior regression pass.

**Additional reference tool (outside the curated release):**
`tools/joetoo-kwin-stage-upstream` was included with the first three
maintainer-accepted readability files in commit `f4e9ba92` (2026-11-25).
It is the explanatory-comment standard, not a 27th release-script entry.

## Selector update: distinct from audit acceptance

The maintainer applied the corrected `configs/` patch on 2026-11-27.
Before commit, `git apply --check`, `git apply`, `git diff --check`, both
`validate_scripts` invocations and `shellcheck -x -s bash` were successful;
`python3 -m unittest discover -s tests -p 'test_eselect_profiles.py' -v`
reported **18 tests, all OK**. The maintainer then committed/pushed
as `0dd2ba3`. See [the evidence record](step1.9-eselect-configs-evidence-2026-11-27.md).
This proves focused selector validation, not the production release nor the
maintainer's acceptance of a complete line-by-line *comment* audit.

## Separate functional issue / policy notes

- In `libexec/joetoo-kwin-plan-functions`, `plan_defaults()` currently sets
  `rdp_remote_width=1024`, `rdp_remote_height=768`, and
  `rdp_initial_client_width=800`, `rdp_initial_client_height=600` at
  `0dd2ba3`. The maintainer is considering changing only the **initial local
  RDP viewer size** to `1024x768`. This is a functional/config-default choice,
  **not** a reason to reopen the accepted comment audit; evaluate separately.
- The revised Step 1.9 packaging contract still refers to user `profiles/`
  and `README_eselect_profiles_conf.md` as of `98ce0d4`; synchronize that draft
  with `configs/` before staging. Keep any functional selector migration separate
  from readability-audit status.
- The selector's retained `.profile-selection.lock` filename is intentionally
  left unchanged to coordinate older/newer module instances; it is an internal
  compatibility name, not a user configuration-directory contract.

## Next operator sequence

1. Complete comment/readability review of `eselect/joetoo-kwin.eselect` and
   record maintainer acceptance if warranted. Its functional update is already
   committed in `0dd2ba3`. Do not repeat
   the four already accepted Bash audits.
2. Review `user-init.d/joetoo-kwind`, then the pending Python modules in the
   order listed above, `joetoo-kwin-resident.js`, and the three C++ files with
   related CMake commentary. Update statuses **only** on real review evidence.
3. Separately reconcile runtime installed paths, source/provenance, the
   packaging contract, upstream staging, tarup, ebuild and packaged-path QA.
