# Proposed graphical layers and layout budget — decision required

This document proposes future policy only. No parser, geometry, broker, resident,
registry or application dispatch change implements it in the current correction.

## Terminology, defaults and syntax

Each entry may explicitly choose layer=panel, under or over, independent of its
application. panel consumes a rectangle in the panel allocation; under requests a
large rectangle behind panels with a usable exposed region; over requests foreground
placement. Dolphin is not intrinsically under.

Recommend preserving the existing four-field syntax and proposing an optional fifth
field `|panel`, `|under`, or `|over`, with strict rejection of any other extra field.
This needs maintainer approval before changing grammar. Logical slots still enumerate
all entries in configuration order on each desktop; layers neither rename nor sort slots.

Proposed default for entries without a layer: panel for every application. This would
change legacy graphical geometry, so approve either that explicit migration or an opt-in
layout-version switch. Do not silently retain application-dependent defaults and call
them layer-independent. Blank/default layer counts as implicit; explicit panel counts
as explicit even though it requests the same effective layer.

## Capacity and geometry

Proposed dt_win_limit defaults to 4 and counts implicitly layered entries per desktop:

- implicit count > dt_win_limit: reject;
- total count > dt_win_limit with implicit count <= limit: accept the capacity check
  with a conspicuous warning;
- otherwise: accept the capacity check normally.

Explicit layers express intentional excess entries but cannot waive nonzero geometry,
fit, minimum usable dimensions or exposure requirements. All effective panel entries,
including explicit panels, share panel geometry regardless of application. Current
terminal geometry supports only 1–4 participants: approval is needed for generalizing
the panel allocator or requiring another layout mechanism for >4 explicit panels.
A capacity warning alone cannot make an impossible layout executable. Distinguish
policy-budget acceptance from failure of a separately validated geometry contract.

For multiple under/over windows, decide whether repeated rectangles are intentional
occlusion, staggered windows or user-specified geometry. Recommend deterministic
staggering for under windows only when each has a usable exposed strip; explicit over
windows can follow file order, with later over windows above earlier ones. These are
proposals, not inferred accepted defaults. Reject impossible combinations before launch
rather than silently shrink, reorder or hide them.

## Exposure, Z-order and focus

Propose separate underlay_horizontal_protrusion_percent and
underlay_vertical_protrusion_percent, initially 2 only if approved. Specify whether
values are minimum exposed strips or exact offsets. Recommended units: percentage
of configured display width/height, rounded up to logical pixels. At 1920x1080,
2% gives 39 horizontal and 22 vertical pixels. Validate the *actual* clipped visible
region after screen edges, gutters, decorations and all panel rectangles; offsets alone
are not proof of clickable area. Approve a minimum pixel hit target and reject layouts
that cannot provide it instead of silently clipping away the promised strip.

[KWin scripting source](https://github.com/KDE/kwin/blob/master/src/scripting/workspace_wrapper.h)
exposes stackingOrder, writable activeWindow, raiseWindow and, since 6.5,
constrain/unconstrain. It does not expose a window-argument lowerWindow method in the
inspected wrapper; slotWindowLower targets active state. Installed Window headers
expose keepBelow/keepAbove. Native availability must be checked on each deployed
version. Persistent constraints or keepBelow can defeat click-to-raise and manual
overrides, so they are not interchangeable with a one-time initial lowering.

Prefer an initialization-only operation on positively verified UUIDs. Evaluate
one-time panel/over raising in file-order-preserving orchestration before proposing a
new lowering API. Explicitly decide focus after launch, including a last entry under
window. Do not steal focus through an active-window-dependent shortcut without a
captured UUID contract. Any necessary resident/broker request flags or completion
acknowledgment require separate narrow authorization; no global stacking privilege
or background re-enforcement is implied. Manual moves/resizes/raise must remain free.

Native acceptance must cover both backends, all layer-order permutations, multiple
under/over windows, 1–4 panels across applications, clipping/minimum-size cases,
click-to-raise, final focus and manual overrides. Record geometry, actual stack order
and focus separately. Current native overlap is evidence for this design work, not
an underlay implementation failure to fix inside the present accepted increment.
