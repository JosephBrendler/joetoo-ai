# Increment 4 -- Configuration layering plan (stage 4)

**Status:** Design discussion only. No new policy, source edits, migration,
OpenRC service behavior, or Stage 3 implementation is authorized by this text.

## What is currently implemented (checked against published source)

- `joetoo-kwin` `check_plan()` calls `plan_defaults()`; then `select_config()` chooses explicit `-f` or one user/system config file; then `source "$config"`; then CLI verbosity overrides; then validation/calculation. `-m l|r` uses analogous loading. These are **trusted executable Bash** files, not a sandboxed key/value format.
- Without `-f`, `select_config()` first checks `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/joetoo-kwin.conf`, then `/etc/joetoo-kwin/joetoo-kwin.conf`. A present but unreadable file must fail, not fall back. Existing `ARCHITECTURE.md` explicitly declares this behavior **accepted and implemented**.
- `~/.config` is normally a *directory*, and `~/.config/joetoo-kwin/joetoo-kwin.conf` is a valid file **inside it**. The flatter proposed `~/.config/joetoo-kwin.conf` is also a possible filename, but changing to it requires a deliberate compatibility/migration decision.
- `poc-user-conf.d/joetoo-kwind` sets `JOETOO_KWIND_EXEC` and `JOETOO_KWIND_RESIDENT_JS`: these are **OpenRC user-service settings**, not CLI launch-plan variables. `/etc/conf.d/joetoo-kwind` and `~/.config/rc/conf.d/joetoo-kwind` are not read by `joetoo-kwin` as part of `select_config()`.
- Current `joetoo-kwin-template.conf` mixes planner geometry budgets, protocol/mechanical timeouts, SDL backend, SFTP advisories, and a five-entry sample `desktop_session_list` in one dense file. It still describes configured RDP as Stage 1/dry-run only; that comment is stale after accepted Stage 2.

## Principle worth adopting

Separate **scope/lifetime of each setting**, not merely which filename happens
to contain it. A daemon's startup/service environment is different from a
per-invocation CLI recipe. Changes to CLI default variables need not be read
by the daemon; process environments do not automatically share Bash globals.

| Class | Examples | Suggested owner / role |
| --- | --- | --- |
| Broker/OpenRC lifecycle | `JOETOO_KWIND_EXEC`, `JOETOO_KWIND_RESIDENT_JS`, service-specific env allowlist | `/etc/conf.d/joetoo-kwind`, user `~/.config/rc/conf.d/joetoo-kwind` as supported by local OpenRC; never source as launch plan merely for convenience |
| CLI/planner shared defaults | `desktop_limit`, `dt_win_limit`, geometry percentages, backend and RDP/VNC mechanical/resource budgets, `RDP_SMART_SIZING` | `plan_defaults()` for built-in fallback; optionally an **app-specific system defaults file** and **user global override file**, read by the CLI |
| Per-run layout/target intent | `screen_width`, `screen_height`, `desktop_session_list`, perhaps selected per-run overrides | Small, readable `joetoo-kwin.conf` per run via `-f`, or documented default user plan; validates complete effective configuration before side effects |
| CLI-only operation arguments | `-f`, `-c`, `-o`, verbosity `-v/-q` | CLI parser; preserve existing command-line precedence |

## Candidate setting inventory (classification, not a new interface)

| Setting family in current `plan_defaults()` | Preferred level (proposed) | Why |
| --- | --- | --- |
| `screen_width`, `screen_height`, `desktop_session_list` | **Per-run** | A plan describes a specific display/session/window arrangement |
| `desktop_limit`, `dt_win_limit`, `min_window_exposure_px` | **CLI-global**, overridable per run | Common planner policy; per-run changes may be useful for a distinct monitor |
| `terminal_*_percent`, `graphical_*_percent` | **CLI-global**, overridable per run | Common geometry policy; single shared planner stays authoritative |
| `initial_focus_*` | **CLI-global** | Mechanical focus observation policy, not a target recipe |
| `sftp_capability_timeout_ms`, `sftp_advisory_*` | **CLI-global**, overridable per run | SFTP performance/diagnostic policy; advisory enabled is *not* currently uppercase pseudo-boolean and should be reviewed separately before renaming |
| `vnc_*` registration/SSH/identity/cleanup/placement budgets | **CLI-global** | Viewer/tunnel operation policy, not OpenRC broker service initialization |
| `rdp_registration_*`, `rdp_backend_log_byte_limit`, `rdp_x11_*` | **CLI-global** | Registration identity and evidence budgets; host-dependent overrides possible |
| `rdp_remote_width/height`, `rdp_initial_client_width/height`, `RDP_SMART_SIZING` | **CLI-global defaults** with optional **per-run** override | Display scaling varies by remote/display workflow |
| `rdp_windowing_backend` | **Per-host/user default**, overridable per run | Must reflect actual local KWin backend; explicit selection remains validated |
| `JOETOO_KWIND_EXEC`, `JOETOO_KWIND_RESIDENT_JS`, daemon service environment | **OpenRC daemon config only** | A service-start override is distinct from a CLI invocation plan |

This inventory is intentionally a *candidate grouping*, not a claim that
existing code already sources these separate layers. The actual scope of
variables consumed by the broker (as distinct from those sent by CLI per
launch) must be verified before proposing any genuinely shared settings.

## Recommended alternative for review

Preserve OpenRC conf.d for **service** configuration. Do **not** source it from
`joetoo-kwin` by default: that would couple a user GUI command to service
startup syntax and possibly root-managed shell content. Instead, consider
this explicitly app-specific CLI precedence:

1. Code `plan_defaults()` (known complete default values).
2. Optional system CLI defaults: `/etc/joetoo-kwin/defaults.conf` (or a maintainer-chosen name).
3. Optional XDG user CLI-global overrides: `${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf`.
4. Selected trusted per-run plan `-f FILE`; otherwise the existing default user-plan path (with preserved system fallback until migration is decided).
5. Explicit CLI parameters, where actually supported (currently e.g. `-v/-q` after source).

This is **not current behavior** and does not propose implicit loading of
arbitrary files by shell initialization. A safer minimal first step may be
**only to split the template/documentation** into a short per-run example plus
an annotated reference of all optional tunables, leaving the runtime loader
unchanged until a separately approved migration.

### Example of an intentionally short per-run file (proposal only)

```bash
# Trusted Bash. Screen size supplied explicitly until auto-detection is supported.
screen_width=1920
screen_height=1080

desktop_session_list=(
    '3|konsole|local|btop|panel'
    '3|dolphin|local||under'
)

# End of example; not an executable command sequence.

```

## Decisions required before code changes

- Whether system/user **CLI-global** files are warranted, and their exact canonical paths; user preference is the XDG subdirectory (default to $HOME/.config/joetoo-kwin/joetoo-kwin.conf)
- Whether any settings genuinely need to be shared between broker and CLI. If yes, identify each consumer and the explicit handoff, rather than assuming OpenRC conf.d is visible to the CLI.
- Preserve the current explicit `-f` behavior: does it replace **only** the per-run recipe, or all optional CLI config? Proposed above: per-run file overlays shared defaults. Decide and test.
- System defaults file trust/ownership, readable/missing/invalid behavior, symlink policy, environment/XDG handling and validation before side effects. [`possible eselect module to configure the symlinks choosing the per-run config`]
- Safe migration from current accepted path, including whether older file is honored (warning or precedence), preventing double sourcing and avoiding silent wrong-plan selection. Avoid using different defaults on X11 and Wayland hosts without an explicit per-host file.
- Revise template into **small runnable recipe** plus **commented reference - including an example of each kind of recipe and default values for variables more likely to "need" a user-override**; retain current code/default validation until a separately reviewed change.

## Timing relative to Stage 3

Do this as Stage 4. Stage 3 must update two timeout defaults in `plan_defaults()` and the existing
template. That is a small compatibility-preserving edit. The **full config
loader redesign is not a prerequisite** for five-minute waits or clean
continuation, and mixing the two would expand the regression surface. Best
sequence: accept this proposal (or revise it) as a separate maintainer
decision; implement it as a small separately authorized config subincrement,
preferably after functional Stage 3 closeout, or as a clearly separate Stage 3
subgate. Do not let the Codex Stage 3 functional assignment silently migrate
paths or make service conf.d the CLI's configuration source.
