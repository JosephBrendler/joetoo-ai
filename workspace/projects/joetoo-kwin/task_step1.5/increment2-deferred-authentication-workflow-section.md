# Interactive authentication, placement and multiwindow scheduling — historical baseline

**Status: HISTORICAL — SUPERSEDED for Increment 4 (2026-11-10).** This discussion preserves the earlier open-ended human-wait rationale, **not** the current implementation requirement. The [authoritative Increment 4 maintainer decisions](step1.5c5d_Increment_4_decisions.md) establish finite, configurable five-minute RDP/VNC viewer-readiness defaults and keep parallel/queued prompting deferred to Version 2. The older analysis below remains unchanged as historical context.

## Accepted baseline: serialized, human-interactive launch

A configured `-o` launch plan proceeds through its windows sequentially, one positively owned registration/placement operation at a time. Remote authentication is an interactive part of a launch and **may take several minutes or longer**. The program must not automatically terminate an owned viewer or tunnel solely because the operator has not answered a password/NLA/host-key dialog within an arbitrary finite human-wait deadline. An operator can explicitly cancel; an actual client/transport exit, expired remote server session or loss of proven ownership is distinct and must be handled honestly. The configured plan may remain paused awaiting the human rather than opening all later windows concurrently. Its progress, pending request/target, cancel path and partial-completion reporting must remain intelligible.

Human waiting must not convert mechanical safety checks into unbounded operations. D-Bus calls, UUID proof after the correct viewer exists, broker placement, cancellation and owned cleanup still use separately justified bounded timeouts. The implementation must not label unverified remote usability as successful merely because the local viewer was registered or placed. Do not conflate source/owner ambiguity with a normal interactive wait.

**Existing known gap, to be addressed during Increment 4 integration (not already implemented):** current development RDP launcher has a 120 s pre-registration deadline; current VNC supervisor has a 10 s SSH startup and 120 s viewer-ready deadline. A fixed deadline can cancel the owned process while a human is entering credentials. Increment 4 must distinguish demonstrable human-wait state from technical failure while preserving safe resource and transaction ownership. If an interactive prompt cannot be identified reliably, no unbounded unknown state or unsafe adoption is permitted: return a precise blocker for maintainer design review. The decision does not imply that GRD, GDM or VNC servers permit indefinite inactivity.

## Distinct lifecycle states

1. A configured request reserves its intended desktop/slot and records its target/request identity without credentials in config, argv, public logs or registry.
2. Local client NLA, VNC or SSH authentication may precede creation of the persistent viewer. Such a dialog is **not** the registered desktop viewer.
3. The genuine persistent viewer is identified by complete per-client, per-backend identity/ownership evidence and exact KWin UUID. For RDP, native Wayland and legacy X11 use their individually accepted correlation rules. Registration itself is not remote login success.
4. **Increment 3:** the operator can explicitly release that positively registered RDP UUID to verified desktop/slot/geometry placement, without auto focus/stack or inferred remote readiness.
5. **Increment 4:** the configured serial launch continues on a genuine terminal registration/placement result, operator cancellation or correctly classified failure; no skipped ambiguous ownership or automatic reassignment.

A remote GNOME GDM screen appears *inside* the already existing persistent RDP viewer after RDP transport/session negotiation. It is distinct from the earlier local NLA dialog. VNC/SSH prompt handling must be evaluated from their own actual client contracts.

## Deferred optimization options and necessary evidence

Staging multiple independently identified NLA/VNC dialogs on a launch-control desktop, providing readable target labels/cascading geometry, continuing local windows around remote requests, and scheduling several pending remote authentications are **not** in the first serial implementation. Any later proposal must measure operator/launch latency; prove temporary-prompt ownership; preserve current single active broker registration/correlation transaction, per-slot reservations and launcher lock; and define pending, failed, cancelled, expired and registered semantics without silent replacement or focus stealing. See [strategy decision](step1.5c5d-increment3-strategy-decision.md).

Server-specific behavior remains an external constraint to characterize in later native verification: SDL FreeRDP local NLA prompt idle behavior; GRD pre-authentication and redirection timeouts; GDM remote-login/locked-session idle behavior; and TigerVNC/SSH interactive prompts and transport failures. No unlimited server idle lifetime is asserted. Never introduce password injection, credential persistence, insecure certificate exceptions or bypass of SSH host-key policy as a workaround.

This document is a recorded engineering decision, **not** new implementation/native-test authorization.
