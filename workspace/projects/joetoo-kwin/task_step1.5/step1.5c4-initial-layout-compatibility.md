# Initial-layout compatibility: focused native-failure follow-up

Branch: `task/joetoo-kwin-step1.5c4-graphical-launch`.
HEAD: `584eb2e4d024215e325e00bc6b24596e2c6f3e5c`. The preceding uncommitted
layer implementation and all existing evidence were preserved. No fetch or
publication performed; the client cannot write repository metadata.

## Findings and correction

Maintainer-reported X11 evidence: Konsole win-001 and Dolphin win-002 were
positively placed/present on desktop 3; initial layout failed with the old
aggregated missing/incompatible error. That error does not identify which UUID
or predicate failed. Native root cause is therefore not yet established.

`stackingOrder.find` used exact comparison of raw `String(internalId)` against
broker canonical UUIDs. The registry's `canonical_uuid()` uses Python UUID parsing,
which removes braces and normalizes case. The resident's general `windowUUID()`
returns the raw Qt string. This representation mismatch is a demonstrated code
compatibility defect, reproduced with braced uppercase Qt IDs in the focused JS
regression. A handler-local conversion now normalizes braces/case consistently
for lookup, focus comparison, raising and stack readback. It changes representation,
not identity: only the exact broker-owned UUID may match. General placement/move
code and registry remain unchanged.

KDE's [scripting reference](https://develop.kde.org/docs/plasma/kwin/api/)
describes stackingOrder as the managed window stack, ordered bottom-to-top.
It is not described as limited to the displayed desktop. Both cohort targets
should be represented if still managed; their actual inclusion at the failed native
claim was not captured. If a UUID is absent, the new diagnostic reports its absence
and whether windowList contains it (or whether windowList is unavailable).
windowList is diagnostic only: it never supplies an alternate stack target.
No native enumeration was performed by Codex.

Inspected installed `/usr/include/kwin-x11/window.h` and `/usr/include/kwin/window.h`:

| Property | Native declaration/meaning | Preserved rejection |
| --- | --- | --- |
| deleted | bool; retained closed-window animation object | truthy |
| fullScreen | bool; actual fullscreen state | truthy |
| keepAbove / keepBelow | bool; persistent stacking flags | truthy; never clear them |
| tile | Tile pointer, if associated; null means none | non-null/non-undefined |
| maximizeMode | MaximizeMode enum | anything other than numeric zero |

Both installed effect/globals.h enum declarations define Restore=0, Vertical=1,
Horizontal=2, Full=3. Thus ordinary false/false/false/false/null/0 floating state
passes these predicates. Unknown maximizeMode, null or string zero still rejects;
no speculative numeric coercion or compatibility bypass was added. Runtime Qt JS
property values on the failing windows remain unobserved. Each rejection now
identifies the UUID, exact failed property, observed value and JavaScript type.
Frame/membership mismatch also identifies its UUID. Upstream raw X11 source fetches
were unavailable; the installed X11/Wayland headers and public reference were inspected.

Broker completion now performs one guarded observation lookup per UUID instead of
repeated dictionary indexing. A disappearing observation after the active-request
guard produces terminal FAILED with UUID-specific detail. Disappearance before the
guard already terminates the transaction and returns a structured InvalidRequest.
Ownership, source/lease checks, Busy protection, geometry comparisons, relative
layer ordering, preferred-focus rules and manual overrides are preserved.

## Validation and changed paths

Executed headlessly:

- Full Python discovery: **282 passed**, no skips (includes installed-header integration).
- Focused broker suite: **10 passed**, including disappearance before completion and
  after the initial validity guard, with terminal status and released transaction state.
- Direct focused JS suite: **19 passed**. Floating displayed/inactive windows,
  braced/case UUIDs, each forbidden mode, unknown enum values, and missing stack
  identity without windowList adoption are covered. Existing focus/order/manual
  override cases remain intact.
- Node discovery: **4 test files passed**.
- `node --check joetoo-kwin-resident.js`, Python compilation and `git diff --check`: PASS.
- No shell executable changed; ShellCheck/Bash checks were not rerun this iteration.

Changed production: `joetoo-kwin-resident.js`, `libexec/joetoo-kwind`.
Changed tests: `tests/test_initial_layout.js`, `tests/test_initial_layout_broker.py`.
Evidence: this report, the focused compatibility patch and HANDOFF Section 5 row 17.
Prior full-feature patch/logs remain historical and were not overwritten.

[Focused complete diff](step1.5c4-initial-layout-compatibility.patch) is relative to
the dirty tree at this iteration's start, not a replacement for the preceding feature.

## Next native action

Maintainer reviews and repeats the existing smallest two-window stacking acceptance
procedure with fresh intended slots and the updated broker/resident installed by
maintainer. Save the initial-layout JSON and any exact UUID/property diagnostic.
Record placement, actual stacking and focus separately. Do not reuse occupied slots
or adopt existing windows. No claim of repaired native acceptance is made here;
if another property rejects, its actual value is the next evidence to review.
No GUI, deployment, service operation, commit, push or merge was performed.
