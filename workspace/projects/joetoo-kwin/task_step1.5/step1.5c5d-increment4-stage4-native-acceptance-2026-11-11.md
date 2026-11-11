# Step 1.5c.5d / Increment 4 Stage 4 — configuration-system native acceptance (2026-11-11)

**Disposition: MAINTAINER ACCEPTED (2026-11-11).** This records the operator's Stage 4 configuration-layering, user-profile, live-launch, display-polish and regression evidence. Acceptance is scoped to Stage 4; it does **not** claim Step 1.5c.5d Increment 5 RDP security closure or official package integration.

## Implementation delivered

- Application CLI loading precedence: `plan_defaults()` → optional `/etc/joetoo-kwin/defaults.conf` → optional `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf` → one selected per-run plan (explicit `-f FILE`, else existing XDG user plan with system plan fallback) → supported CLI verbosity overrides. All files remain *trusted Bash*. Missing optional defaults are allowed; selected inaccessible, dangling, syntactically invalid or failed source files fail closed.
- Optional **non-root** `eselect joetoo-kwin list|show|set` selects user-owned profiles via the established XDG user-plan symlink. Tests cover name/number selection, ownership/mode checks, invalid profiles, prior regular-file preservation, locking, atomic exchanges and rollback behavior. List's selected-profile asterisk was added in the finishing pass, using the eselect framework's `highlight_marker()`; selection semantics and safety remained unchanged.
- Small copyable `joetoo-kwin-per-run-template.conf`, detailed `docs/configuration-reference.md`, and packaging-ready paths/instructions. No ebuild or user HOME was changed by package installation; the operator used a deliberate temporary XDG test directory.
- `show_config()` now uses `notice_varlist`, `info_varlist`, `debug_varlist` with cumulative severity; `rlv.config` supports long file paths and `bool.RDP_SMART_SIZING` / `bool.sftp_advisory_enabled` preserve header pseudo-Boolean rendering. Codex reported all **48** existing configuration variables appear exactly once across the lists.
- No Stage 3 RDP/VNC worker, broker, resident, remote-identity, geometry, stacking or OpenRC configuration redesign.

## Headless and local regression evidence

| Check | Observed/reported outcome | Provenance |
| --- | --- | --- |
| Initial complete Stage 4 candidate | 102 focused Python PASS; **903 full Python PASS**; **161 JavaScript PASS**; syntax/whitespace checks PASS | Codex report; user independently ran 102 focused and 903 Python / 161 JS via `restart_joetoo-kwind` |
| Stage 4 presentation refinements | **78 focused Python PASS; 911 full Python PASS; 161 JavaScript PASS**, zero skipped reported | Codex finishing-pass report; not separately rerun in the supplied native transcript |
| Installer/service integration at initial Stage 4 candidate | `restart_joetoo-kwind` update, stop/start, installed-file `--check` and `qdbus6` introspection PASS | Maintainer's local `gmki91` transcript, before the display-only polish |
| ShellCheck at final maintainer checkout | `validate_scripts joetoo-kwin -l` ended **`done; result: (Ok ✅)`** | Maintainer, after authentic sourced-module annotations and narrow `SC2034` suppressions; dummy stub removed |
| Source diff hygiene | ShellCheck no new warnings in Codex's finishing candidate; whitespace and syntax checks PASS | Codex report; subsequent maintainer clean ShellCheck output takes precedence for final local state |

Selected final ShellCheck operator output:

```text
$ validate_scripts joetoo-kwin -l
✨ looking for shellcheck ... (found) [ ✅ ]
🔎 checking joetoo-kwin ...
⌚Real: 0m7.837s  User: 0m6.733s  Sys: 0m1.100s
✨ done; result: (Ok ✅) [ ✅ ]
✨ validate_scripts complete. Total elapsed time (DD:HH:MM:SS:mmm): [00:00:00:07:899]
```

**Evidence limit:** The final 911/161 suite was supplied as a Codex report; the user's separately shown local run was 903/161 before the presentation-only refinements. No post-polish native `-c/-vc/-vvc` transcript is included in the supplied record. This does not negate the maintainer's explicit acceptance; it limits precisely what was observed.

## Native KWin X11: gmki91

The maintainer created an isolated user-owned XDG tree with two copies of the new short template, `profiles/work.conf` and `profiles/alternate.conf`, and `defaults.conf` setting `terminal_width_percent=75`. The plans explicitly overrode this to **70** and **65**, respectively; built-in value was **87**. The operator set `XDG_CONFIG_HOME` to that temporary tree, leaving the normal user configuration alone. No `/etc` defaults were modified; the system-default precedence path was covered by headless tests.

| Operator step | Observed result |
| --- | --- |
| `./joetoo-kwin -c -f "$config_dir/profiles/work.conf"` | Valid plan, effective `terminal_width_percent=70`, dry-run 2 entries |
| Same, `alternate.conf` | Valid plan, effective `terminal_width_percent=65`, dry-run 2 entries |
| `eselect joetoo-kwin list` | Listed `alternate.conf` and `work.conf` |
| `eselect joetoo-kwin show` before selection | `(no user selection; CLI system-plan fallback may apply)` |
| `eselect joetoo-kwin set work.conf`; `show` | `Selected user profile: work.conf`; `show` returned `work.conf` |
| `./joetoo-kwin -c` | Effective 70, using the XDG selected `joetoo-kwin.conf` link |
| `eselect joetoo-kwin set 1`; `./joetoo-kwin -c` | Switched to `alternate.conf`, effective 65 |
| `./joetoo-kwin -c -f "$config_dir/profiles/work.conf"`; `eselect ... show` | Explicit run used effective 70; active selection remained `alternate.conf` |
| `eselect joetoo-kwin set missing.conf` | Rejected: `Profile is missing, unsafe, unreadable or has invalid Bash syntax` |
| `eselect joetoo-kwin set 2`; `./joetoo-kwin -c` | Selected `work.conf`; effective 70 |

For native execution, the operator confirmed the two-entry Dolphin `under` + Konsole `panel` plan on desktop 3, with effective width budget 70:

```text
$ ./joetoo-kwin -o
Validating configured launch intent result: (completed)
LAUNCH PLAN: [2] windows; confirmation required
Desktop  Slot  Program  Mode   Target  Layer  X   Y   Width  Height
3        1     dolphin  local  -       under  96  32  1804   972
3        2     konsole  local  btop    panel  19  54  1344   918
Do you want to continue? [Y/n]: y
Launching desktop [3] slot [1]
Registered [win-001] UUID [a3825926-ab56-4129-bfe8-3ef7a77a6567]
OK launch: Home — Dolphin (pid=571535) before=[1] (694,63) 531x918 after=[3] (96,32) 1804x972
Launching desktop [3] slot [2]
Registered [win-002] UUID [9e401699-74c7-49b1-8811-2f309df83ac4]
OK launch: Konsole (pid=571758) before=[1] (694,63) 531x918 after=[3] (19,54) 1344x918
Desktop [3] initial stacking/focus result: (completed)
Entries: completed [2], failed [0], skipped [0]; incomplete desktop cohorts [0]
Configured layout: [2/2] windows completed ... (completed)
```

**Presentation polish:** The operator requested a single active-profile asterisk in `eselect list` and less noisy `show_config` output. Codex implemented both and reported tests using the real eselect framework and installed `script_header_joetoo`; the maintainer subsequently achieved clean `validate_scripts`. The supplied transcript *does not separately demonstrate* the post-polish asterisk or three live verbosity renderings.

## Accepted scope, exclusions and next milestone

**Accepted Stage 4:** configuration layering, compatibility with existing user/system plan lookup, per-run override authority, safe opt-in user profiles, documentation/packaging-ready assets, reduced severity-sensitive display, native X11 dry-run and managed-launch behavior. The maintainer reported pushing the updated files and explicitly accepted Stage 4.

**Not asserted:** Native Wayland re-testing of the Stage 4 configuration loader; post-polish native screen output; install into `joetoo` protected ebuild; RDP TLS/NLA/server identity or remote-login security acceptance. These are not newly invented Stage 4 acceptance gates.

**Next:** Step 1.5c.5d Increment 5 is the existing RDP security/native closure objective. First inventory *already collected* GNOME Remote Desktop, certificate, authentication and X11/Wayland evidence; distinguish established observations from gaps. Request only precisely justified missing checks, rather than assuming more implementation is required. See `HANDOFF.md` and the draft Increment 5 evidence-reconciliation task.
