# Step 1.7 — q552u01 native Wayland and refined snapshot acceptance evidence

**Date:** 2026-11-19. **Host:** `q552u01`, local Plasma Wayland.  **Branch:**
`task/joetoo-kwin-step1.7-recovery-snapshot`. **Code under test:** refined
candidate subsequently committed as `33bbbee03a5effbf1c4c31b5600254ab28374510`
(source baseline `f18fea2`). **Operator:** maintainer, not an AI agent.

**Source transcripts (complete; only trailing terminal whitespace/blank lines normalized):**

- [Initial candidate native-context focused test console](step1.7-q552u01-initial-native-focused-console-2026-11-19.txt) — 47 tests passed, including the isolated SO_PASSCRED fixture; this preceded the refinements.
- [Refined native Wayland console](step1.7-q552u01-refined-native-console-2026-11-19.txt)
- [Focused/full headless, JavaScript and combined ShellCheck console](step1.7-q552u01-refined-headless-console-2026-11-19.txt)
- The maintainer separately supplied the final failed-`-S` preservation output
  reproduced below. The `validate_scripts` pass for `joetoo-kwin` was also
  supplied in a screenshot and appears in the native-console transcript.

For provenance, the original uploaded attachment SHA-256 hashes (before
trailing-whitespace normalization) were:

| Original attachment | SHA-256 |
| --- | --- |
| Initial 47-test console | `b87deeed7dbadde9a795279c1e748f82ff6b050b8662ed8fdae87cdae4e45b21` |
| Refined headless console | `6544ff20c7e2deec6a2523f5417abc410626f778f8fecf716f14442d411b3bed` |
| Refined native console | `fc956ba487fd8a67098e4cd5d4df0e08931e5ee26ad337eac6a64ff093b6068b` |

This document records observed results; no native operations were performed by
its author. Native evidence belongs to the candidate, not a claim that the
milestone has already been accepted or merged.

## Results and selected actual output

### Native recovery and legacy migration

- Pre-refinement state: `win-004` missing, `win-005` and `win-006` present,
  all desktop 3. The existing last-good was a **regular file** owned by `joe`,
  mode `0600`, and was independently backed up with `cp -p`.
- The refined deployment installed/checked all 14 development user-owned
  components. Initial immediate D-Bus introspection from the restart helper
  reported `Service 'org.joetoo.KWinBridge' does not exist`, but subsequent
  `RegistryStatus` returned `recovery: "ready"`, managed count 3 and the
  original missing/present identities. This is an observed startup-readiness
  race, not a demonstrated lasting broker failure.
- `XDG_STATE_HOME="$test_state" ./joetoo-kwin -f "$test_conf" -S` with a
  missing record refused. The original regular snapshot remained byte-for-byte
  equal to its backed-up copy (`cmp` succeeded).
- A confirmed `-x` retired one missing registration and closed two Wayland
  managed windows. `-r` read the legacy regular file and successfully launched
  three new managed windows (`win-007`, `win-008`, `win-009`) with new UUIDs and
  placements. The old file was demonstrably backward-compatible for restore.
- First refined `-S` migrated the legacy regular file to immutable history and
  published a **relative** `last-session.conf` symlink. A search with `cmp`
  found the migrated legacy file byte-identical to the backup. The directory
  was `0700` and the symlink target regular file `0600`, both owned by `joe`.

```text
=== REFUSAL TEST ===
EXPECTED: incomplete arrangement was refused
=== LEGACY FILE MUST BE UNCHANGED ===
Original last-good preserved

=== SNAPSHOT FORMAT ===
"protocol": 2
"settings": 47
entries: desktop 3/slots 1,2,3 (konsole, dolphin, konsole)

Migrated legacy snapshot found: snapshot-20261119T205253.282637211Z-bd47a7f9e7841dd1d083711bcb1ad6cc.conf
Legacy migration verified
```

The concise format lines above are an excerpt/abbreviation; consult the raw
console for the literal JSON and per-entry recipe fields.

### Repeated saves, retention and refusal

- Three consecutive `-S` invocations produced distinct timestamp/random
  filenames, even with unchanged launch intent. Initial default depth was 10;
  the configured `snapshot_history_depth=2` then retained precisely the two
  newest history files with a valid latest symlink.
- `-r` against occupied desktop/slot reservations was correctly refused with
  `managed desktop/slot conflict [win-007]` without launching replacements.
- On `win-007`, confirmed `-d` closed the exact Wayland window while retaining
  the missing record and reserved desktop/slot. A broker-only restart recovered
  `win-007` as **missing**, not present. `GetManaged` retained the caption,
  desktop file, desktop list, frame, PID and resource class; a sorted observation
  comparison returned `result: 0`.
- The connection field became `unknown` after restart, not a fabricated
  authenticated connection. Historical observation is diagnostic, never
  live-identity or close authority.

```text
win-007 desktop=3 slot=1 UUID=db08cbb4-b3e1-48f2-adf7-ba4a17509128
presence: missing
caption: joetoo-kwin : bash — Konsole
resource_class: org.kde.konsole
pid: 1039249
last-known frame: x=19 y=54 width=1670 height=918

$ diff -u <(jq -S '.window.observation' missing-before) <(jq -S '.window.observation' missing-after)
result: 0
```

### Final post-refinement failure-preservation check (separate maintainer paste)

With `win-007` missing and `last-session.conf` already a symlink, the operator
saved the pre-test symlink target and sorted history filenames, attempted an
ineligible `-S`, then compared both values. Actual output:

```text
PASS: incomplete arrangement refused
PASS: last-good symlink unchanged
PASS: snapshot history unchanged
```

This covers the negative path for both legacy regular-file preservation and
new history/symlink preservation.

### Headless, JavaScript and static checks run on q552u01

The **refined candidate on the native host** test transcript reports:

```text
Ran 79 tests in 12.823s
OK
Ran 1080 tests in 200.087s
OK
ℹ tests 163
ℹ pass 163
ℹ fail 0
ℹ skipped 0
```

The combined four-file `shellcheck -x ...` invocation printed `Killed`. It must
**not** be reported as a successful combined invocation. Afterward the
maintainer ran `validate_scripts ... -l` **individually** for
`joetoo-kwin`, `joetoo-kwin-plan-functions`,
`joetoo-kwin-launch-functions` and `joetoo-kwind-install-poc`; all four
reported `Ok ✅`. `bash -n`, `sh -n` and `git diff --check` produced no
reported syntax/whitespace errors in the supplied run. The cause of `Killed`
was not established; `dmesg` did not show an OOM record in the supplied output.

## Limits and disposition

These results substantiate the Wayland Step 1.7 contracts on this candidate:
private same-session recovery, safe historical observations, fail-closed
complete-snapshot selection, protocol-1 read compatibility, protocol-2
normalized recipes, timestamped immutable history, retention, and fresh-instance
restore. The earlier initial-candidate Wayland declined-`-r` test is a separate
operator-reported result; it is not recharacterized as a refined-candidate run.

**Assessment:** focused native Wayland tests passed. Maintainer acceptance and
branch merge remain separate decisions. See [task README](README.md) and
[slim2 X11 evidence](step1.7-slim2-native-x11-evidence-2026-11-19.md).
