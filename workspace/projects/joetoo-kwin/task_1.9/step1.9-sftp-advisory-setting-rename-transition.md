# Step 1.9 transition: SFTP advisory pseudo-boolean rename

Status: **source transition proposal**, for maintainer review (not a runtime
acceptance or a decision to implement a checkpoint-reset command).
Baseline: `joetoo-ai` branch `task/joetoo-kwin-step1.9-packaging-integration`,
commit `b061a28` (including the accepted first three audit files and the
committed second-round `libexec/joetoo-kwin-launch-functions` comments).

## Decision and scope

Before the first production ebuild release, rename the configurable Joetoo
pseudo-boolean `sftp_advisory_enabled` to `SFTP_ADVISORY_ENABLED`.
Keep its representation (`$TRUE` is nonempty `0`; `$FALSE` is empty), enabled
default, and advisory-only behavior. This is a name/schema change, not a
redesign of NSS/TCP probes or launch control flow.

Change the nine active code/config/reference/test files found by `git grep -l`:
`joetoo-kwin`, `joetoo-kwin-template.conf`,
`libexec/joetoo-kwin-plan-functions`,
`libexec/joetoo-kwin-launch-functions`,
`libexec/joetoo_kwin_persistence.py`,
`docs/configuration-reference.md`,
`tests/test_config_presentation.py`, `tests/test_openrc_user_setup.py`, and
`tests/test_sftp_advisory.py`. Preserve files under `archive/` unchanged:
they record the historical spelling in its original context. A future search
must distinguish historical occurrences from active ones.

## Local development deployment and compatibility

No production ebuild has shipped. The maintainer elects **no compatibility
alias/migration** for this experimental configuration name. Old config files
that assign the lower-case name will still be valid Bash, but will no longer
override the newly default-enabled upper-case variable: audit local external
configuration layers and any hand-selected `-f` files before native testing.
Likely layers include `/etc/joetoo-kwin/defaults.conf` and
`${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/defaults.conf`, plus the
selected per-run configuration and other local fixtures. The rename patch
does **not** write to host-installed or user-home files.

The saved recipe schema also changes: Python's `SETTING_NAMES` and enum
validation, generated `-S` text, and `-r` verification now use the new name.
Existing experimental snapshots with the old name are not promised backward
compatibility. Any old durable snapshots chosen for disposal should be
inspected and removed by the operator when no save/restore is in progress.
Do not mistake them for runtime checkpoints.

Two independent persisted stores must be distinguished:

- **Durable, explicit**: `${XDG_STATE_HOME:-$HOME/.local/state}/joetoo-kwin/`
  contains `last-session.conf` (a pointer to immutable timestamped
  `snapshot-*.conf` history). `-S` saves verified recipes/settings; explicit
  `-r` validates and launches *new* instances. Service restart does not
  automatically invoke `-r`.
- **Runtime, automatic**: `$XDG_RUNTIME_DIR/joetoo-kwin/managed-windows.json`
  is broker-maintained same-KWin-session identity/reservation history used to
  reconcile existing windows after broker restart. It can contain embedded
  `restore_intent` with the old settings key; changed schema validation can
  reject such a checkpoint. It must not be casually deleted while live
  managed windows or authoritative broker state need preservation. Broker
  shutdown may rewrite it.

## Reported recovery issue and follow-up proposals

The maintainer recalls an earlier gmki91 development session with absent
windows retained in `-l`, slot conflict on a new launch, and `-x` unable to
retire the stale records after windows had been closed outside the broker.
The exact historical command/log sequence and file deletion have **not** been
re-verified for this note. This is motivation to examine an explicit
operator-controlled runtime checkpoint reset, not evidence that deletion is
safe while managed windows survive.

Potential follow-up **`-Z`**: a narrowly defined, guarded reset of the
*runtime checkpoint*, with explicit operator confirmation and a quiescent
broker/session contract. Determine the exact shutdown/reconciliation and
safety preconditions from source before authorizing implementation. It must
not silently discard live-window ownership or the durable snapshot history.
Potential **`-z [timestamp]`**: deliberate curation of the *durable* last-good
selection and immutable history (including timestamp selection, lock, link,
retention, and atomicity rules). Defer this feature for possible version 2
rather than treating it as a prerequisite to this rename. Neither flag is
implemented or authorized by the present change.

## Verification and disposition

1. Inspect `git diff` for only the named setting and this note; preserve all
   executable semantics, including the committed second-round launch-function
   audit work.
2. Confirm non-archive tracked sources contain **no old spelling**. Inspect
   local external configs separately; `git grep` cannot find them.
3. Run shell syntax/ShellCheck, Python syntax, focused advisory/config tests,
   and snapshot/recovery tests. Compare any existing baseline failures.
4. In a disposable development session, inspect both private stores and
   arrange a controlled test reset if necessary, without silently deleting
   runtime ownership records. Confirm a disabled advisory is actually
   disabled with the new setting name before native acceptance.

This note records the transition and its boundaries, not proof that native
validation or live-state cleanup has occurred.
