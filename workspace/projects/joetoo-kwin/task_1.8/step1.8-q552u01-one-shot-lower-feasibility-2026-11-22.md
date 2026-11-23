# Step 1.8 — q552u01 one-shot `-L under` feasibility evidence

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Date:** 2026-11-22. **Host/session:** `q552u01`, native Plasma Wayland, KWin 6.7.6 (maintainer-operated). **Target:** positively registered managed `win-012`, UUID `e727c860-d65b-4dd3-a686-7d7cedf959cf`, desktop 3, slot 4, Dolphin local `/tmp` recipe. This record is **feasibility proof**, not native acceptance of an integrated `joetoo-kwin -L ... under` implementation.

## Origin and scope

The maintainer confirmed `./joetoo-kwin -L 3 dolphin local /tmp over` printed `Registered [win-012] UUID [e727c860-d65b-4dd3-a686-7d7cedf959cf]`, `OK launch`, and `Initial stacking/focus result: (completed)`. `./joetoo-kwin -l` listed a present/succeeded `win-012` and a separate retained missing `win-007`. Probe scripts resolved the target via broker `GetManaged`, not a class/title or window adoption.

KWin 6.7.6 reported `slotWindowLower: "function"`, `raiseWindow: "function"`, `stackingOrder: true`, but `lowerWindow: "undefined"`. The lower slot operates on the active window, not an explicit `Window*`.

## Native observations (selected actual terminal output)

1. The original V1 probe's `--inspect` and `--lower` both timed out with `NO VERIFIED REPORT` and no confirmed temporary-script unload; they establish no lower outcome.
2. V2 `--inspect win-012` from **desktop 1** returned `state: refused`, `reason: wrong_desktop`, `mutated: false` for a desktop-3 target. V2 from **desktop 3** returned `state: inspected`, `mutated: false` with full UUID/stack readback; no movement was expected.
3. V2 guarded `--lower` without a manual click returned `state: refused`, `reason: target_not_active`, `mutated: false`. Its six-second arm period required an operator click.
4. V2 manual-click lower: operator clicked the target (Dolphin window showing *35.0 GiB Internal Drive (dm-6)*). Exact target active, one slot lower, `state: acted`, `verdict: PASS`, `mutated: true`. Both immediate and settled assessments reported target at bottom, peer relative order intact, same normal-window set, desktop unchanged, and unchanged eligible frame/membership/keep flags.
5. V3 automatic `--activate-and-lower win-012`: initially active Konsole `612d4bba-ac04-451d-9fc3-3179faf856a5` on desktop 3. Probe requested target UUID activation, verified target active, called lower once, then settled. Output included `activation_requested: true`, `lower_invoked: true`, `state: acted`, `verdict: PASS`. No manual click was needed.
6. V3 attempted **from desktop 1**: maintainer reports it did not work when target was on desktop 3, but supplied no console transcript from this particular attempt. The V3 probe explicitly guards the current desktop; this alone does **not** prove the compositor lacks a safe cross-desktop alternative.

### V2 manual-click lower — actual stack excerpt (bottom-to-top UUID prefixes)

```text
before:    cab72b5f, ed81456e, 3bbbc9d0, 612d4bba, e727c860 [target]
immediate: e727c860 [target], cab72b5f, ed81456e, 3bbbc9d0, 612d4bba
settled:   e727c860 [target], cab72b5f, ed81456e, 3bbbc9d0, 612d4bba
```

```json
{
  "mode": "lower", "mutated": true, "state": "acted", "verdict": "PASS",
  "settled_assessment": {
    "desktop_unchanged": true,
    "eligible_frames_memberships_keep_flags_unchanged": true,
    "full_stack_unchanged": false,
    "pass": true,
    "peer_relative_order_preserved": true,
    "same_normal_window_set": true,
    "target_at_bottom": true
  }
}
```

### V3 automatic activation/lowering — actual stack excerpt (bottom-to-top UUID prefixes)

```text
before:    cab72b5f, 3bbbc9d0, e727c860 [target], 0afc492d, 612d4bba
pre_lower: cab72b5f, 3bbbc9d0, 0afc492d, 612d4bba, e727c860 [active target]
immediate: e727c860 [target], cab72b5f, 3bbbc9d0, 0afc492d, 612d4bba
settled:   e727c860 [target], cab72b5f, 3bbbc9d0, 0afc492d, 612d4bba
```

```json
{
  "activation_requested": true,
  "lower_invoked": true,
  "managed_id": "win-012",
  "mode": "activate_and_lower",
  "mutated": true,
  "state": "acted",
  "verdict": "PASS",
  "settled_assessment": {
    "active_after": "612d4bba-ac04-451d-9fc3-3179faf856a5",
    "active_before": "612d4bba-ac04-451d-9fc3-3179faf856a5",
    "desktop_unchanged": true,
    "eligible_frames_memberships_keep_flags_unchanged": true,
    "full_stack_unchanged": false,
    "pass": true,
    "peer_relative_order_preserved": true,
    "same_normal_window_set": true,
    "target_at_bottom": true
  }
}
```

`full_stack_unchanged: false` is **expected** when the target changes position. Its peers' order and geometry remained unchanged in these trials.

## Screenshots (maintainer-supplied, unchanged)

- [Desktop 3 before V2 inspection](screenshots/20261122-q552u01-desktop3-before-inspect.png)
- [V3 before visual context](screenshots/20261122-q552u01-v3-before.png)
- [V3 after, terminal PASS output](screenshots/20261122-q552u01-v3-after-pass.png)
- [V3 after, settled assessment](screenshots/20261122-q552u01-v3-after-settled.png)

## Engineering consequence and limits

On a displayed target desktop, the proven Wayland operation is **activate exact UUID → verify that active UUID → call `slotWindowLower()` once → read back the settled bottom-to-top stack**. The probe did not prove this works from an inactive target desktop, nor that all X11/focus/competing-activation cases are safe.

The separate implementation **candidate** proposes an inactive-desktop fallback: raise the existing eligible normal peers on the target desktop in their existing bottom-to-top order, without changing the user's displayed desktop or focus; verify that target is then bottommost and peer order/geometry/membership/keep flags remain unchanged. This is deliberately a **narrow proposed relaxation** of the earlier no-peer-restacking contract. It is not native-tested or accepted by the provided V2/V3 evidence. Existing `-L over`, configured `-o`, management/close, and recovery contracts remain in scope for regression tests. No `-L panel` work is proposed.
