# Step 1.5d — over-only single-recipe candidate

**Candidate for maintainer review, not native acceptance.** Started clean on
`task/joetoo-kwin-step1.5d-integrated-regression` at
`e7b90271fe25e31106a39c6f9d820ec532215566`, descended from accepted PR #29
`3e9c4bf311bc65b32d332a00d3b50163a9043303`. Fetch could not write read-only
`.git/FETCH_HEAD`; no fresh remote synchronization is claimed. Existing inventory
implementation/tests and historical source review are preserved. No source in
protected repositories, native session, service or installed package was changed.

## Implemented contract

- `-L DESKTOP PROGRAM MODE TARGET [over]` takes separate arguments; omitted layer
  is over. Explicit panel/under reports “not implemented yet”; other/blank layers,
  wrong counts, pipes and control characters fail before confirmation.
- Settings load through the existing configuration layers/selected profile or
  `-f`. Only the recipe array is replaced. Existing validators and a shared
  executable-pair allowlist provide field-specific, redacted errors; targets
  never become shell code. Existing RDP NLA/strict defaults remain unchanged.
- Reuse the validated `ListManaged` reader to select the first unused logical
  slot in 1..256, retaining missing reservations and rejecting uncertainty.
  Feed that starting slot into the shared planner: the single over window uses
  the existing graphical region, never physical panel allocation or peer reflow.
- Reuse `open_plan`, its invocation lock, preflight, confirmation, application
  adapters, registration/placement verification and cohort finalization. Recheck
  the confirmed slot after confirmation; a race fails rather than retargeting.
- The only placement/raise target is the new broker-owned registered UUID.
  Existing-window geometry is never assigned. Registered viewers are not killed
  to disguise a failed raise; incomplete geometry/stacking/focus remains nonzero.

## Minimal additive raise evidence (no new D-Bus signatures)

The resident advertises `single_raise_protocol=1` in synchronized inventory;
`RegistryStatus` exposes that capability. `-L` preflight requires it along with
existing health and initial-layout checks, so old installations fail before a
child starts. Old `-o` callers omit the new option and keep their existing behavior.

`SubmitInitialLayout` optionally accepts `single_raise:true` **only** with one
positively placed/present, source-owned `over` registration. `TakeInitialLayout`
passes the option to the resident. The broker freezes existing normal-peer
geometry/membership; the resident still calls the existing `raiseWindow` once
per cohort UUID (one here), then reports `raise_order` for all live normal windows
on that desktop, including sticky peers. It never writes another window's frame
or keep-above/below flags. Completion requires a complete, duplicate-free order
matching current broker observations, with the new UUID last, unchanged new
geometry and unchanged existing peers. Singleton cohort order alone is no proof.
Existing focus/desktop/source/liveness checks and deadlines remain effective.

This is a one-shot observation, not continuous Z-order enforcement. Shell/dock
layers are outside the normal-window observation contract. A normal keep-above
peer, competing activation, peer motion/closure, source loss or asynchronous
nonconvergence may cause conservative failure; none authorizes forced stacking,
new retries, desktop switching or adoption of another UUID. Late effects cannot
turn a terminal failure into success. No persistent layer metadata/reflow API
was added. The old live-layout review remains historical and unmodified.

## Headless evidence

Final results: **125 focused Python PASS; 938 full Python PASS; 163 JavaScript
PASS**, no skips reported. Bash/Python syntax, ShellCheck and whitespace checks
passed. The focused coverage includes actual CLI parsing/configuration/planning/
preflight and serial orchestration with fake bus/application seams; the real
broker/registry initial layout handlers; the existing resident JS in a VM; and
preserved inventory tests.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_single_recipe_launch test_initial_layout_broker test_step1_5d_inventory test_step1_5c_launch test_grouped_layers_launch test_rdp_configured
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
node --test --test-isolation=none tests/test_*.js
bash -n joetoo-kwin libexec/joetoo-kwin-launch-functions libexec/joetoo-kwin-plan-functions
shellcheck -x joetoo-kwin libexec/joetoo-kwin-launch-functions libexec/joetoo-kwin-plan-functions
node --check joetoo-kwin-resident.js
git diff --check
# End of commands

```

Changed Python files were parsed with `ast.parse` without bytecode output.
Development tests caught a missing single-raise peer-snapshot assignment and
fixture gaps; both were corrected before the final passing suites. No unresolved
test failure remains.
Disposable helpers cannot contact RDP/SSH/VNC or KWin. No mock proves native
placement, physical visibility, compositor scheduling or remote authentication.

Cases include default/explicit over; unsupported layers/counts; field diagnostics
and secret redaction; selected profile/explicit file; retained missing slots,
logical slot beyond four and full 256-slot exhaustion; declined confirmation;
Busy/malformed/uncertain state and post-confirmation conflicts; supported client
adapters; launch/placement/stack failure; older raise capability rejection; full
stack evidence and frozen peer geometry; unchanged configured `-o` and `-l`.

## Smallest reserved native integration matrix

Only after maintainer review/publication/installation authorization, with matching
broker/resident, use each host's existing valid per-run settings and approved
endpoints. No service operation or native test was executed by Codex.

| Host | Maintainer observations |
| --- | --- |
| `gmki91`, native X11 | `-l` baseline; default-over Konsole local and explicit-over Dolphin local; verify new IDs/UUIDs, chosen free slots, graphical region, intended desktop, final normal stack and unchanged peer frames. |
| `q552u01`, native Wayland | Same focused local-app checks; include inactive-desktop launch (no desktop switch) and normal close → retained missing listing. |
| Both, representative existing adapters | As practical, one unreachable-SSH placeholder Konsole, Dolphin SFTP, TigerVNC-over-SSH and strict SDL RDP across the two hosts; retain exact local outcomes without claiming transport/login success. Existing comprehensive PKI/renderer tests stand. |
| Both, negative and preservation | Reject panel/under/invalid target before confirmation; decline; verify an occupied/missing slot is skipped, Busy/uncertain state stops, no existing managed/unmanaged peer geometry changes. Manual changes after successful completion are not undone. |
| Both, existing configured flow | One representative mixed `-o` cohort with implicit panel and explicit under/over; preserve accepted layout/stack/focus and strict RDP settings. Do not clear missing reservations or restart merely to bypass Busy. |

Suggested basic commands (maintainer only; choose a free desktop and valid settings):

```bash
: "${PLAN:?Set the existing private per-run settings file}"
: "${DESKTOP:?Choose an approved target desktop}"
./joetoo-kwin -l
./joetoo-kwin -f "$PLAN" -L "$DESKTOP" konsole local btop
./joetoo-kwin -f "$PLAN" -L "$DESKTOP" dolphin local '' over
./joetoo-kwin -l
# End of commands

```

Use read-only broker `GetManaged`/observations to retain selected frame/membership
and UUID evidence before/after, plus terminal initial-layout status. Keep raw
captions/endpoints/logs private. Native acceptance and Step 1.5d closure remain
maintainer decisions; no publication or deployment is implied by this record.
