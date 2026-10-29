# Step 1.5b native acceptance record

Recorded 2026-10-29 from **maintainer-executed** tests; no agent native operations.
Recording branch: task/joetoo-kwin-step1.5b-interactive-move, clean initial HEAD
`de79be3ef14665c0510162f0e72a8352827641b8`. Latest native transcripts were not
individually tied to a commit hash. This records evidence, not a claim of deployment
synchronization or maintainer approval to publish.

**Assessment:** sufficient evidence to proceed to final review and PR preparation
for Step 1.5b. Remaining cases below are explicit native coverage gaps, not observed
implementation defects. Maintainer decides whether to accept those gaps or request
additional tests. This is not acceptance of the broader Step 1.5 milestone.

PASS means the supplied result matches the expected behavior; an expected rejection
is a PASS. FAIL denotes an unsuccessful operation and does not alone establish a
product defect. NOT TESTED means no controlled native evidence was supplied.

| Case | X11 gmki91 | Wayland q552u01 | Evidence / qualification |
| --- | --- | --- | --- |
| All six move operand forms | PASS | PASS | [Six forms](step1.5b-native-evidence.md#six-forms) |
| Shared left/right geometry and desktop-only / size preservation | PASS | PASS | Same transcripts; configured 1920x1080 geometry |
| Correct observed desktop reporting | PASS | PASS | Later screenshots replace placeholder zero |
| Sticky/all-desktops preservation | PASS | PASS | [Membership evidence](step1.5b-native-evidence.md#safety-and-membership) |
| Explicit desktop replaces sticky membership | NOT TESTED | PASS | Wayland all-desktops to exactly desktop 2 |
| Maximized geometry-change refusal | PASS | PASS | Expected rejection; no success falsely reported |
| Nonexistent desktop rejection | PASS | PASS | Desktop 45 / 47 rejected |
| Separate-window targeting | PASS | PASS | Distinct reported windows; not a post-capture race test |
| Info split, debug diagnostics, -v/-q handling | PASS | PASS | [Formatting](step1.5b-native-evidence.md#formatting-and-verbosity) |
| Fractional before geometry converges to requested frame | NOT TESTED | PASS | Latest screenshot, not proof that all roundoff cases converge |
| Controlled focus change after capture | NOT TESTED | NOT TESTED | Headless coverage exists |
| Membership specifically on desktops 1 and 2 simultaneously | NOT TESTED | NOT TESTED | Sticky membership is a different case |
| Tiled refusal, separately exercised | NOT TESTED | NOT TESTED | Headless coverage exists |
| Fullscreen refusal, separately exercised | NOT TESTED | NOT TESTED | Headless coverage exists |
| Corrected Busy classification | NOT TESTED | NOT TESTED | Earlier native Busy rejection predates correction; current headless coverage |
| Controlled overlapping-request test without dragging | NOT TESTED | NOT TESTED | Earlier tests do not isolate post-capture behavior |
| Earlier Wayland placement attempt during possible dragging | NOT TESTED | FAIL | [Timeout evidence](step1.5b-native-evidence.md#focus-and-overlapping-requests); cause inconclusive, not acceptance failure by itself |

Regression evidence: latest maintainer X11 run **198 Python tests PASS**, **14 Node
tests PASS**. Earlier Wayland run **190 Python tests PASS**, inventory JS **4 PASS**,
syntax and ShellCheck **PASS**. See [provenance and limits](step1.5b-native-evidence.md#maintainer-regression-runs).
Agent logs separately cover the Iteration 6 full regression and Iterations 7–8
focused installed-header checks; do not conflate those with native execution.

No numeric-tolerance change is approved or implemented. Exact comparison remains
in force. The [controlled sensitivity test and optional proposal](step1.5b-iteration6-review.md#precision-finding-and-separate-proposal)
remain available for separate review; current native evidence does not justify
changing that contract in this acceptance iteration.

Next: maintainer final code/diff review and disposition of listed native gaps,
then separately authorized publication. No commit, push, PR creation, deployment,
protected-repository integration or Step 1.5c work is authorized by this record.
