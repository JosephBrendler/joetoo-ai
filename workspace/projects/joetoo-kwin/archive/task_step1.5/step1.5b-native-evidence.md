# Step 1.5b maintainer-provided native evidence

Source: maintainer transcripts and screenshots supplied in the collaboration
conversation on 2026-10-29. These are selected, sanitized excerpts/summaries,
not agent-executed tests or complete raw logs. Screenshots remain in the original
conversation; unrelated desktop content, environment dumps and network details
are intentionally not copied into this public repository. Host labels identify
only the two agreed validation environments. No exact tested commit was included
with the latest runs; the local recording baseline is de79be3.

## Six forms

Earlier transcripts on gmki91 (X11) and q552u01 (Wayland) each showed successful:

| Input after -m | Verified result |
| --- | --- |
| l / r | Left (19,54) / right (873,54), 816x918 |
| 2 | Desktop 2 with unchanged position and size |
| 1 r (also explicit l cases) | Explicit desktop and shared layout geometry |
| 2 100 120 | Desktop 2, position (100,120), size preserved |
| 100 120 700 500 | Position (100,120), size 700x500, desktop preserved |
| 1 100 120 700 500 | Legacy five-value move succeeds |

Earlier desktop-preserving diagnostics printed placeholder after=[0]. The later
screenshots show corrected actual after=[1]/[2] membership and two asterisk-prefixed
info lines, following the completed notice-level verification line.

## Safety and membership

Maintainer labeled the gmki91 test as maximized; q552u01 also reported rejection
in the corresponding maximized test:

> ERROR Optional move failed: Error: Refusing geometry change on tiled/fullscreen/maximized or unknown-mode window

Invalid desktop 45 on gmki91 and 47 on q552u01 reported:

> ERROR Optional move failed: Error: Virtual desktop does not exist

Sticky left/right moves on gmki91 reported:

> before=[all] (873,54) 816x918 after=[all desktops] (19,54) 816x918 tiled=false fullscreen=false

> before=[all] (19,54) 816x918 after=[all desktops] (873,54) 816x918 tiled=false fullscreen=false

Wayland sticky right move reported:

> before=[all] (19,54) 816x918 after=[all desktops] (873,54) 816x918 tiled=false fullscreen=false

Wayland explicit `-m 2 l` reported:

> before=[all] (873,54) 816x918 after=[2] (19,54) 816x918 tiled=false fullscreen=false

A later command starts sticky again. Intervening manual state changes were not
logged; do not infer a continuous automatic transition from desktop 2 to sticky.

## Formatting and verbosity

Latest X11 and Wayland screenshots show completed notice result lines followed
by separate asterisk-prefixed info lines: identity ending at PID, then before/after
geometry and mode details. DEBUG=$TRUE shows request IDs and preservation flags.
X11 `-vvvv -q` clamps at 7 then ends at 6, showing info without request-debug lines.
Wayland `-vvv -q -v` ends at 7 and shows both info and debug. Narrow terminals
still wrap long geometry details, as expected from the header.

## Focus and overlapping requests

X11 individual tests distinguished window A and B by different reported PIDs;
both moved successfully. Delayed-command tests targeted the window active at
shortcut invocation, which need not be the terminal issuing the command.
They do not constitute controlled focus changes after capture.

Earlier Wayland overlap returned org.joetoo.KWinBridge.Busy with
“Previous request has not completed”. Its old compatibility explanation was
subsequently corrected, but no post-correction native Busy transcript was supplied.
The other request reported placement confirmation timeout with observed x about
921.795, y about 76.304, width 816.0000000000002, height 918. The maintainer may
have dragged the window; cause remains inconclusive.

The latest Wayland screenshot instead shows fractional before geometry (x about
510.766, y about 97.437, width 815.9999999999998), then successful verified
placement at (873,54), 816x918. Fractional starting geometry alone is not a failure.

## Maintainer regression runs

Latest gmki91 output:

> Ran 198 tests in 15.756s
>
> OK

Node `--test tests/test_*.js`: 14 tests, 14 pass, zero failures/skips. Cases include
inventory, delayed exact-UUID verification, preservation flags, captured focus,
desktop bounds, stale/deleted windows, mode rejection and unclaimed requests.

Earlier q552u01 output: 190 Python tests passed; inventory JS file reported four
passing tests; Bash syntax and ShellCheck returned zero. Maintainer additionally
reports headless regressions passed on both hosts; the supplied earlier Wayland
JS transcript covers only the inventory file, not all three current files.
