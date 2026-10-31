# Step 1.5c implementation prerequisite: public preflight state

Observed checkout: clean task/joetoo-kwin-step1.5c-configured-launch at
31400fe0d2be05064b898cf520d06d6445e13839, equal to local main and cached origin/main.
The supplied bf835c7 baseline is an ancestor. Branch creation was unnecessary.
No fetch was attempted, consistent with the earlier sandbox fetch prohibition;
remote freshness beyond cached refs is not independently established.

The latest user confirmation resolves draft-status language and authorizes
1.5c.1–1.5c.3. The remaining issue is an actual public-interface limitation:

- Broker _managed_summary, ListManaged and GetManaged expose positive identity,
  presence, placement and observation, but omit stored recipe.desktop/slot.
- Registry ManagedWindow.recipe holds the intended slot, but is broker-private.
  Observed geometry/caption/current desktop cannot safely reconstruct that slot.
- RegistryStatus includes registry request counts and observation synchronization,
  but omits self.request (the placement transaction). A legacy move/launch can
  therefore be active while all registry request counts show no active work.
- Status requires a known request ID. It cannot discover another client's request.

Consequently the CLI cannot implement the required complete preflight through
existing read-only interfaces. Rejecting every existing managed window would
incorrectly block independent entries; guessing slots from titles/geometry would
weaken identity policy. Submitting a probe transaction would mutate broker state
before confirmation and is not an acceptable read-only preflight.

Proposed smallest additive read-only extension, for separate authorization:

1. Add an allowlisted intended object containing desktop and slot to managed
   summaries (copied from broker-owned recipe). Do not expose full trusted recipes.
2. Add a placement object to RegistryStatus with state and request ID when active,
   or an explicit idle state. Define whether querying advances expiry consistently
   with Status; do not report elapsed stale state as safely completed.
3. Keep all D-Bus signatures intact; extend returned JSON additively and test
   legacy consumers. No resident or registry implementation changes proposed.

These queries enable preflight, not atomic reservation. Recheck before each
submission; keep SubmitManagedLaunch's existing atomic Busy handling authoritative.
A concurrently created slot conflict still needs a defined policy: either a bounded
broker-side slot check at submission or an explicitly accepted single-orchestrator
assumption. Do not silently promise race-free slot reservation from read-only queries.

Next actor: maintainer decides this bounded broker scope extension (and slot-race
policy) before implementation proceeds. Current HANDOFF Section 4 and the latest
user instruction explicitly prohibit existing broker edits without separate approval.
No production changes or tests were performed. Only this evidence and the Codex-owned
Section 5 record were added; no native operations, staging, commit, push or deployment.
