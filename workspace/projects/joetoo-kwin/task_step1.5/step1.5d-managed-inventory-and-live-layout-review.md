# Step 1.5d — inventory candidate and live-layout transaction boundary

> **Scope disposition (maintainer, 2026-11-11):** The shared live-layout reflow extension below is **NOT approved for current Step 1.5d**. Its analysis is retained as historical engineering evidence. The approved `-L` operation launches only a new managed window with omitted or explicit `over`, rejecting `panel`/`under` as "not implemented yet"; it does not move existing windows. The independent `-l` inventory candidate and tests remain in scope. Current authority is [HANDOFF](HANDOFF.md) and [ARCHITECTURE](../ARCHITECTURE.md).

**Candidate; Step 1.5d is incomplete.** Reviewed branch
`task/joetoo-kwin-step1.5d-integrated-regression`, initially clean at
`e29dd7f99c56cc59ecc6335d7da615863c03a9cd`, after accepted PR #29 merge
`3e9c4bf311bc65b32d332a00d3b50163a9043303`. Fetch was blocked by read-only
`.git/FETCH_HEAD`; no fresh remote synchronization is claimed. No native work,
publication or changes to accepted RDP/VNC behavior occurred.

## Implemented independent inventory action

`joetoo-kwin -l` uses only `ListManaged`; it does not enumerate observed windows,
source executable configuration or initialize a layout. Complete JSON/schema,
integer coordinates, canonical UUIDs, presence/placement domains, record count
and unique managed IDs/UUIDs/desktop-slot reservations are checked before any
rows print. Fixed columns expand for long IDs; full UUIDs remain available.
Sort is desktop, slot, numeric managed ID. Missing/uncertain records remain
visible. Optional/private fields are excluded rather than interpreted. Broker
failure and malformed/inconsistent inventory return nonzero; empty inventory
is a distinct successful result. Tests exercise the actual CLI and a snapshot
from the real broker/registry headless fixture, including missing retention.

## Concrete limitation for full `-L`, not a new UX question

The requested separate operands, default **over** for omitted `-L` layer,
unchanged implicit **panel** for `-o`, four-panel capacity, grouped reflow and
existing-window cascade/stack participation are accepted requirements. They
have not been replaced with a one-entry `-o` shortcut.

Current production source exposes no application-independent, exact-managed-ID
geometry reflow transaction:

| Inspected source | Existing boundary |
| --- | --- |
| `libexec/joetoo_kwin_registry.py`, `ManagedWindow` | No per-window layer or layout-order field. Intended desktop/slot are reservation identity, not panel index. |
| `libexec/joetoo-kwind`, `_managed_summary()` / `ListManaged()` | No layer/order exposed. The latest `initial_layout` object retains one cohort, not authoritative metadata for every live/historical managed record. |
| Broker `SubmitInitialLayout()` lines 1701–1758 | Entry schema accepts exactly registration request ID and layer. Freezes current geometry; it does not accept new target geometry. |
| Broker `CompleteInitialLayout()` lines 1773–1826; resident `initialLayoutFromBroker()` | Success requires independently unchanged geometry and desktop membership. This contract must remain unchanged for existing `-o`. |
| Broker `SubmitMove()` / `TakeMove()` lines 1274–1320 | Optional move binds the shortcut-selected window supplied by the resident; it cannot authorize reflow of a broker-selected managed peer. |
| Broker `_sdl_placement_record()` lines 853–865 | Explicit SDL marker/class/launch ownership. Reusing this as a generic peer mover would require weakening or changing the accepted adapter. |
| `libexec/joetoo-kwin-plan-functions`, `calculate_plan()` | Logical slots begin at 1 for the configured group; physical panel indices and cascade counts are local to that plan. It must not be called unchanged as though a live desktop were empty. |

The missing metadata alone has a small additive solution. The additional
**geometry-changing shared broker/resident transaction** is the material
extension: silently adding geometry to the stacking-only payload or driving
active-window moves would violate accepted interfaces or UUID safety. This is
the task's stated shared-transaction scope boundary; `-L` remains unimplemented
pending disposition of the concrete extension below, not pending selection of
another CLI syntax or another milestone.

## Smallest implementation option for maintainer disposition

1. Retain session-only, broker-owned layer, source epoch and stable per-desktop ordering on
   each managed record when an authorized cohort is finalized. Add optional
   layout metadata to the allowlisted query response. Existing records without
   positive metadata remain **unknown**, including historical missing records;
   never classify by title, geometry or logical slot. No restart adoption or
   on-disk persistence. A failed/incomplete cohort must not invent membership.
2. Add an explicitly selected geometry-reflow variant of the shared layout
   exchange, leaving the current payload/unchanged-geometry result intact. A
   proposed submission uses `protocol=2`, `expected_source`, and entries of
   `{managed_id, layer, geometry:{x,y,width,height}}`, with the
   existing focus/placement bounds conveyed explicitly. Existing v1 methods and
   resident protocol advertisements must continue working unchanged; advertise
   the reflow capability separately. This is a proposed schema, **not an
   implemented or accepted public contract**.
3. Resolve managed IDs to broker-held UUIDs (not through a possibly evicted
   completed launch-request entry); validate reservation, live owner/application
   evidence, intended desktop, source and peer snapshots before motion. Pin the
   authentic resident sender and transaction owner; late/foreign completions
   cannot claim a newer batch. Execute one serial batch through the existing
   `placeOptionalWindow`/common placement verification primitives. Do not add a
   second geometry solver, focus-based target or permanent stack enforcement.
4. Reuse `terminal_geometry()` for all 1–4 physical panel positions; keep each
   peer's original logical slot. Choose the new logical slot from unused values
   in 1..256 across **all retained reservations**; fail if none. Recheck at the
   existing authoritative registration reservation point. Capacity counts must
   include known reserved panels; unknown membership fails before confirmation.
   Compute graphical cascade using the existing planner policy with positively
   known live peers, without recascading other desktops.
5. Confirm the full resulting desktop arrangement. Launch/register/place the
   new viewer first using the existing serial path; a launch or initial
   placement failure must not move peers. Revalidate peer snapshots afterward.
   Then reflow existing panel peers in retained order, verifying each, followed
   by shared one-shot stack/focus only after all geometry verifies. On source,
   identity or verification loss, stop further assignments and report completed,
   failed and unattempted peers with actual frames; do not claim atomic rollback,
   kill existing windows or substitute UUIDs. A client may apply an already
   issued request later; terminal failure remains terminal.

Affected implementation would span CLI argument/validation and launch helpers,
registry metadata, broker transaction/schema and resident assignment dispatch,
plus focused Python/JS protocol tests. This is more than relabeling the existing
initial-layout call. No such shared API or production placement change was made
in the inventory candidate. `ARCHITECTURE.md`'s existing statement that omitted
`-L` layer uses the existing recipe default also needs the focused correction:
**only `-L` omission means `over`; `-o` omission/blank remains `panel`**. The user
instruction settles this; architecture status must not be used to change it.

## Native regression reserved for the maintainer

After review/publication/installation authorization, `-l` can be checked on both
existing native sessions before/after an already approved managed launch and
normal close: stable ID/UUID, intended slot, present→missing, unchanged other
windows, no motion or activation. No service reset is needed merely to list.
Full integrated `-L` native checks must await the reflow implementation, then
cover default over, explicit under, 1→2→3→4 panel group reflow and fifth-panel
preflight refusal, retained missing reservations, Busy/stale source refusal and
representative accepted `-o` mixed-client regressions. Existing RDP strict
security/native acceptance stands; no new PKI investigation is requested.
