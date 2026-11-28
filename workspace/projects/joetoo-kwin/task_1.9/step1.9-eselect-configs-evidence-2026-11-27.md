# Step 1.9 — `eselect joetoo-kwin` `configs/` update evidence

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-27 (maintainer-provided native Gentoo terminal transcript).
**Host:** `gmki91`; project `~/joetoo-ai/workspace/projects/joetoo-kwin`.
**Work branch:** `task/joetoo-kwin-step1.9-packaging-integration`.
**Tested baseline:** `98ce0d4` plus the corrected, then-uncommitted selector
patch (readability changes for launch library/session bashrc in baseline).
**Publication status (later on 2026-11-27):** committed, signed and pushed to
this task branch as `0dd2ba3`. The maintainer's commit output reports seven
files changed (204 insertions, 164 deletions) with the companion README rename.

## Intended behavior

`eselect joetoo-kwin list/show/set` operates on **this user's** per-run launch
configuration files, not on Gentoo system profiles or any `/etc` links. The
selected default `joetoo-kwin -o` plan is the existing user configuration
pathname; `eselect` only creates/switches its symlink:

```text
${XDG_CONFIG_HOME:-$HOME/.config}/joetoo-kwin/
├── configs/
│   ├── joetoo-kwin.conf
│   └── joetoo-kwin2.conf
└── joetoo-kwin.conf -> configs/joetoo-kwin.conf
```

`XDG_CONFIG_HOME`, when absent or relative, resolves under `$HOME/.config` as
implemented by the CLI and selector. `-f FILE` continues to override the
selected per-run plan. Global/system and user defaults remain distinct layers.
No `/etc` target discovery or symlink management was requested.

The source change replaces the selector's former `profiles/*.conf` candidates
with `configs/*.conf`, updates its displayed terminology and link target,
updates `docs/configuration-reference.md`, `docs/joetoo-kwin_user_manual.md`,
renames the colocated selector README to
`eselect/README_eselect_configs_conf.md`, updates `MANIFEST`, and adjusts
`tests/test_eselect_profiles.py` (filename retained). The internal
`.profile-selection.lock` is deliberately retained for cross-version lock
coordination. Selection still refuses to overwrite an ordinary active config
file, foreign/dangling symlinks, unsafe/unowned targets or invalid Bash.

## Application evidence supplied by maintainer

The first patch failed to apply to the two documentation files due to
zero-context hunks. The **corrected** patch was then applied successfully:

```bash
cd ~/joetoo-ai
git apply --check ~/Downloads/joetoo-kwin-eselect-configs-98ce0d4-corrected.patch
git apply ~/Downloads/joetoo-kwin-eselect-configs-98ce0d4-corrected.patch
git diff --check
git status --short
```

The displayed `git status --short` after applying reported the following
(uncommitted) working-tree changes:

```text
 M workspace/projects/joetoo-kwin/MANIFEST
 M workspace/projects/joetoo-kwin/docs/configuration-reference.md
 M workspace/projects/joetoo-kwin/docs/joetoo-kwin_user_manual.md
 D workspace/projects/joetoo-kwin/eselect/README_eselect_profiles_conf.md
 M workspace/projects/joetoo-kwin/eselect/joetoo-kwin.eselect
 M workspace/projects/joetoo-kwin/tests/test_eselect_profiles.py
?? workspace/projects/joetoo-kwin/eselect/README_eselect_configs_conf.md
```

`git apply --check` and `git diff --check` produced no errors in the supplied
transcript. A `D` plus `??` for the README rename is the normal unstaged Git
presentation; it does not imply the replacement README was omitted.

## Shell validation and unit tests

On `gmki91`, from the project directory, the maintainer ran:

```bash
validate_scripts eselect/joetoo-kwin.eselect
validate_scripts eselect/joetoo-kwin.eselect -l
shellcheck -x -s bash eselect/joetoo-kwin.eselect
echo $?
python3 -m unittest discover -s tests -p 'test_eselect_profiles.py' -v
```

Results as provided:

- Both `validate_scripts` invocations completed successfully; the maintainer's
  `validate_scripts-1.0.20` transcript did not print individual lint diagnostics.
- `shellcheck -x -s bash` returned exit code **0**.
- `unittest`: **18 tests in 2.524 seconds — OK**. The reported passing cases
  include `test_existing_configs_link_can_be_switched`,
  `test_legacy_profile_link_requires_manual_migration`, selection by name and
  number, invalid/dangling/foreign symlinks, locked selector, protection of an
  existing regular plan and concurrent-file races, relative XDG fallback, and
  actual selected-plan loading with explicit `-f` bypass.
- The maintainer reported the selector change is **working well**.

This is evidence of patch application, syntax/lint and focused functional
regression tests before the subsequent `0dd2ba3` commit/push. It does **not** establish that an installed new eselect module
was used for a live `list/show/set` run on the original non-test configuration,
that the full project suite passed, or that source staging/package release QA
completed. It also does not by itself constitute maintainer acceptance of the
whole module's source-comment readability audit.

## Development installer and integration impact

Review of `tools/joetoo-kwind-install-poc` and
`tools/joetoo-kwind-configure-openrc-user` at baseline `98ce0d4` found
that they install development CLI/broker/OpenRC support and configure
`$XDG_CONFIG_HOME/rc/rc.conf`, not `joetoo-kwin/configs/*.conf` or the selected
per-run symlink. **No installer code update is required** for this selector
change. Production packaging must continue to avoid writing user HOME files.

## Remaining follow-up (no action implied)

1. Maintainer reviews the committed `eselect/joetoo-kwin.eselect` comments
   and records a separate readability-audit acceptance if warranted; the
   functional `configs/` update is already committed and pushed.
2. Bring `task_1.9/step1.9-packaging-inventory-contract-REVISED-DRAFT.md`
   references from `profiles/` to `configs/`, including the renamed colocated
   README, before human-operated source staging. Verify stale old-named files
   are not left in `joetoo-upstream`.
3. After installing the updated selector in the target Gentoo host, a user may
   separately confirm `eselect joetoo-kwin list/show/set` against the actual
   account's configs and a safe `joetoo-kwin -c`; do not conflate this with
   the tests already completed.
