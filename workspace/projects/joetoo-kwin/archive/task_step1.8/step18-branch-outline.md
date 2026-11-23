# Proposed new Step 1.8 — CLI completion (outline for maintainer review)

<!-- Copyright 2026 Joseph Brendler; SPDX-License-Identifier: GPL-3.0-or-later -->

**Planning only; not a source implementation or a test report.** The former
Step 1.8 was combined into the accepted Step 1.7 (PR #33). This is a NEW,
separately scoped Step 1.8 following that accepted baseline.

## Scope and decisions

1. **`joetoo-kwin -s` — read-only broker status.** Use the existing
   `org.joetoo.KWinBridge.RegistryStatus()` interface; validate its returned
   schema and distinguish unavailable broker, inconsistent response, Busy and
   actual status. Do not change registry state or imply that a remote session
   is connected merely because a KWin window is present.
2. **`joetoo-kwin -i MANAGED_ID` — read-only managed-window detail.** Accept
   one canonical managed ID, use existing `GetManaged(identifier)`, clearly
   distinguish `FOUND` from `UNKNOWN`, absent/uncertain and last-known
   observation fields. Do not accept arbitrary raw UUIDs at the CLI or expose
   unapproved sensitive data. Must not adopt, move, close or select a window.
3. **`joetoo-kwin -L DESKTOP PROGRAM MODE TARGET under`.** Reuse accepted
   one-window confirmation, validators, capacity, slot reservations, launch,
   positive original UUID registration and placement. Add native KWin X11 and
   Wayland proof of a **one-shot lower of the newly managed window** below
   eligible peers on its target desktop, with readback evidence. No peer
   movement/reflow, no permanent keep-below, no class/title substitution, no
   fallback to `over` on failure. Preserve omitted LAYER=`over` and explicit
   `over`, and unchanged `-o` `under/panel/over` semantics. Prove supported
   compositor API and correct interaction with focus/activation before accepting.
4. **`-L ... panel` remains unsupported until Version 2.** No panel insertion,
   geometry recomputation, occupancy rebalancing or live reflow in this task.

## Suggested branch and steps

1. Maintainer accepts/merges the documentation baseline, confirms a clean,
   current `main`, then creates
   `task/joetoo-kwin-step1.8-cli-completion` from that exact commit.
2. Create `task_1.8/README.md` with this bounded objective/tests and a short
   `task_1.8/HANDOFF.md` linking back to `ARCHITECTURE.md`.
3. Implement `-s` and `-i` first; add focused, headless tests for argument
   grammar, JSON parsing, no broker, empty/unknown/uncertain records,
   nonmutation and diagnostic redaction.
4. Investigate KWin's supported one-shot lower API on both accepted 6.7.6
   compositor backends, then minimally extend the existing single-window
   stacking transaction and its broker/resident readback protocol. Do not
   introduce another window-identification path or general reflow engine.
5. Run focused Python/Bash/JavaScript syntax/regression tests and the
   maintainer-approved native X11 and Wayland `-L under` proof, including
   competing activation, inaccessible target, omitted-layer `over` and
   rejection of `panel`. Existing Step 1.7 recovery and `-o` must not regress.
6. Review updated `-h`, user manual, configuration/CLI docs and Step 1.8
   evidence. Human approves merge; Step 1.9 then resumes source freeze.

## Non-goals

No KWin 6.8 compatibility milestone, Portage/`tarup` integration, new remote
clients, persistent stacking rule, panel reflow, unrelated refactoring, or
rewriting accepted Step 1.7 history. Protected repositories are maintainer-only.
