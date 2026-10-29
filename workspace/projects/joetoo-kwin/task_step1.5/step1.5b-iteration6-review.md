# Step 1.5b focused native-feedback corrections

Baseline: clean `task/joetoo-kwin-step1.5b-interactive-move` at
`22e93f21e27c38f28e60fd3c2fa4f99523f13d68`. No fetch performed.
Current Section 4 permits these bounded CLI/broker/test/evidence edits.
Maintainer skill and demonstration remained read-only.

## Changes

- Broker optional-move success uses verified observed membership: `after=[2]`,
  `after=[1,2]`, or `after=[all desktops]`. Legacy Submit reporting is unchanged.
- CLI recognizes exact qdbus6 error-name lines for Busy, Unsupported,
  UnknownMethod/UnknownInterface, BadArguments/InvalidRequest/InvalidArgs.
  It also recognizes the exact missing-SubmitMove diagnostic previously observed.
  Unknown failures get a generic submission failure label. Original diagnostics
  are retained in every case. qdbus6 exposes text rather than structured exceptions;
  no arbitrary message-body keyword matching or new IPC dependency was added.
- Notice verification now closes its concise announcement with a result. Info
  (`-v`) shows the full verified window/desktop/geometry detail; debug (`-vv`)
  adds request identity, preservation flags and polling count. Failures retain
  details at error severity. Action status remains separate from reporting status.
- No signature, grammar, geometry policy, capture, ownership, concurrency,
  resident or Step 1.5c changes.

## Precision finding and separate proposal

The broker compares each observed x/y/width/height with the resolved request
using Python `==`. Numerically equal integer/float values match, and preserved
fractional values can match exactly. A new test demonstrates that width
816.0000000000002 alone, against 816, keeps verification pending and ultimately
fails. A separate displaced-position case also fails. No tolerance was added.

This demonstrates numeric sensitivity in a controlled regression, not the cause
of the native timeout: that native observation also had a substantially wrong
position. Manual dragging remains plausible but unproven.

For separate maintainer review, a possible narrowly bounded contract is absolute
error <= 0.000001 logical pixel independently for each finite geometry component,
with no relative tolerance, rounding, or change to UUID/desktop/source checks.
This would accept the shown width roundoff while rejecting the displaced native
position. Validate native roundoff without dragging and test the threshold on
both sides before approving any change; this iteration deliberately keeps exact
comparison intact.

## Evidence and remaining gate

197 Python tests passed without skips (portable and real installed-header tests);
3 Node test files passed; Bash syntax, ShellCheck and whitespace checks passed.
Logs are `step1.5b-iteration6-{python,node,syntax,shellcheck}.log`.
The complete iteration diff is `step1.5b-iteration6.patch`, including new evidence.

User-reported native evidence before these corrections covers all six forms on
X11 and Wayland and successful basic placement/preservation. The overlapping
Wayland run showed Busy rejection and nonconvergence, not proof of a targeting
or roundoff defect. The previously supplied q552u01 transcript explicitly ran
only the inventory JS file; this iteration's agent run covers all three files.

Maintainer next: review this diff, validate corrected desktop membership/status
and notice/info/debug output natively, and confirm Busy is no longer labeled
as incompatibility. Sticky/multiple membership and post-capture focus changes
still need native evidence if required for acceptance. No native operations,
staging, commit, push, installation or protected writes were performed.
