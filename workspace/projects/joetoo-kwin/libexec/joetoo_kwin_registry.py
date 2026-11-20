#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Step 1.4a in-memory model for positively registered KWin windows.

This module neither observes KWin nor grants close authorization. The broker
must establish trusted launch/correlation provenance before calling it. The
Step 1.4b broker integration, Step 1.4c D-Bus APIs, and later persistence are
intentionally separate work.
"""

from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass, field
import uuid
import math


TERMINAL_REQUEST_STATES = frozenset(
    ("succeeded", "failed", "timeout", "ambiguous"))
PRESENCE_STATES = frozenset(("present", "missing", "uncertain"))
PLACEMENT_STATES = frozenset(
    ("not_requested", "pending", "succeeded", "failed"))
CONNECTION_STATES = frozenset(
    ("not_attempted", "connecting", "connected", "unavailable", "exited", "unknown"))


class RegistryError(ValueError):
    """An invalid transition, registration, identity, or evidence contract."""


def canonical_uuid(value):
    """Return KWin's normalized UUID, rejecting invalid/missing identifiers."""
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise RegistryError("invalid KWin UUID") from exc


def historical_observation(value):
    """Bounded last-known facts; optional legacy fields remain absent, not invented.

    This validation never establishes current presence or destructive authority.
    Only the broker's authenticated inventory/native verification can do that.
    """
    if not isinstance(value, dict):
        raise RegistryError('invalid historical observation')
    result = dict(uuid=canonical_uuid(value.get('uuid')))
    if type(value.get('pid')) is not int or value['pid'] <= 0:
        raise RegistryError('invalid historical PID')
    app = value.get('resource_class')
    if not isinstance(app, str) or len(app) > 256:
        raise RegistryError('invalid historical class')
    result.update(pid=value['pid'], resource_class=app)
    for name in ('resource_name', 'desktop_file', 'caption'):
        if name in value:
            if not isinstance(value[name], str):
                raise RegistryError('invalid historical text')
            result[name] = value[name][:256]
    if 'desktops' in value:
        desktops = value['desktops']
        if (not isinstance(desktops, list) or len(desktops) > 256
                or any(type(v) is not int or not 1 <= v <= 256 for v in desktops)
                or len(set(desktops)) != len(desktops)):
            raise RegistryError('invalid historical desktops')
        result['desktops'] = list(desktops)
    if 'on_all_desktops' in value:
        if type(value['on_all_desktops']) is not bool:
            raise RegistryError('invalid historical desktop membership')
        result['on_all_desktops'] = value['on_all_desktops']
    if 'geometry' in value:
        frame = value['geometry']
        if (not isinstance(frame, dict) or any(type(frame.get(k)) not in (int, float)
                or not math.isfinite(frame[k]) or abs(frame[k]) > 2147483647
                for k in ('x', 'y', 'width', 'height'))
                or frame['width'] < 0 or frame['height'] < 0):
            raise RegistryError('invalid historical frame')
        result['geometry'] = {k: frame[k] for k in ('x', 'y', 'width', 'height')}
    return result


@dataclass
class LaunchRequest:
    request_id: str
    source: str
    baseline: frozenset
    recipe: dict
    run_id: str | None = None
    state: str = "pending"
    launch_pid: int | None = None
    result: str = ""


@dataclass
class ManagedWindow:
    managed_id: str
    window_uuid: str
    request_id: str
    run_id: str | None
    recipe: dict
    observation: dict
    presence: str = "present"
    placement: str = "not_requested"
    connection: str = "not_attempted"
    # No general application-session monitor is implemented in Step 1.4a.
    application_sessions: list = field(default_factory=list)
    restore_intent: dict | None = None  # Validated recipe/settings, never ownership.


class WindowRegistry:
    """Broker-owned data model; NOT a public D-Bus registration interface.

    The caller must only supply the actual broker-owned correlation result,
    current synchronized inventory, and observation-source context. Structural
    checks here are defense in depth, not authentication of D-Bus senders.
    """

    def __init__(self, completed_limit=128):
        if isinstance(completed_limit, bool) or not isinstance(completed_limit, int) or completed_limit < 0:
            raise RegistryError("completed_limit must be a nonnegative integer")
        self.managed_windows = {}       # UUID -> ManagedWindow
        self.uuid_by_managed_id = {}    # win-NNN -> UUID
        self.requests = {}              # request ID -> LaunchRequest
        self._completed = OrderedDict() # bounded IDs of completed requests
        self._completed_limit = completed_limit
        self._active_request_id = None  # serialize in-flight correlations
        self._next_managed_number = 1   # do not reuse aliases this broker lifetime
        self._before_register = lambda record: None  # Durable publication seam, not identity validation.
        self._changed = lambda: None  # Broker persistence adapter; model tests remain offline.

    def begin_launch(self, request_id, *, source, synchronized, baseline,
                     recipe, run_id=None):
        """Record an armed launch intent, not a managed KWin window."""
        if synchronized is not True or not isinstance(source, str) or not source:
            raise RegistryError("prelaunch KWin inventory must be synchronized")
        if not isinstance(request_id, str) or not request_id or request_id in self.requests:
            raise RegistryError("invalid or duplicate request ID")
        if self._active_request_id is not None:
            raise RegistryError("a launch correlation is already active")
        if run_id is not None and (not isinstance(run_id, str) or not run_id):
            raise RegistryError("invalid run ID")
        if not isinstance(recipe, dict):
            raise RegistryError("launch recipe must be a mapping")
        try:
            snapshot = frozenset(canonical_uuid(value) for value in baseline)
        except (TypeError, RegistryError) as exc:
            raise RegistryError("invalid prelaunch window inventory") from exc
        self.requests[request_id] = LaunchRequest(
            request_id, source, snapshot, deepcopy(recipe), run_id)
        self._active_request_id = request_id

    def mark_running(self, request_id, launch_pid):
        """A launch PID is evidence; it is not a run ID or request ID."""
        request = self._active_request(request_id, "pending")
        if (isinstance(launch_pid, bool) or not isinstance(launch_pid, int)
                or launch_pid <= 0):
            raise RegistryError("invalid launched PID")
        request.launch_pid = launch_pid
        request.state = "running"

    def finish_failed(self, request_id, state, detail=""):
        """Finish an unregistered launch; never create a window implicitly."""
        request = self._active_request(request_id, ("pending", "running"))
        if state not in ("failed", "timeout", "ambiguous"):
            raise RegistryError("invalid failed-request terminal state")
        self._finish(request, state, str(detail))

    def register_match(self, request_id, correlation, *, current_windows,
                       source, synchronized):
        """Register a still-present, uniquely correlated launched window.

        The broker (Step 1.4b) must bind this call to its own BeginCorrelation
        transaction. A client-supplied JSON MATCHED string is NOT trusted proof.
        """
        request = self._active_request(request_id, "running")
        if synchronized is not True or request.source != source:
            raise RegistryError("stale or unsynchronized KWin source")
        if not isinstance(correlation, dict) or not isinstance(current_windows, dict):
            raise RegistryError("invalid correlation or live window inventory")
        if (correlation.get("state") != "MATCHED"
                or correlation.get("request_id") != request_id
                or correlation.get("evidence") != "pid"
                or correlation.get("candidate_history_complete") is not True
                or isinstance(correlation.get("pid"), bool)
                or correlation.get("pid") != request.launch_pid):
            raise RegistryError("correlation is not a unique complete PID match")
        identifier = canonical_uuid(correlation.get("window_uuid"))
        if identifier in request.baseline:
            raise RegistryError("preexisting window cannot be registered")
        observed = current_windows.get(identifier)
        if (not isinstance(observed, dict)
                or canonical_uuid(observed.get("uuid")) != identifier
                or isinstance(observed.get("pid"), bool)
                or observed.get("pid") != request.launch_pid):
            raise RegistryError("matched window is not present with matching PID")
        if identifier in self.managed_windows:
            raise RegistryError("UUID is already registered")
        # All failure checks precede mutation, including alias allocation.
        managed_id = f"win-{self._next_managed_number:03d}"
        record = ManagedWindow(managed_id, identifier, request_id, request.run_id,
                               deepcopy(request.recipe), deepcopy(observed))
        record.restore_intent = deepcopy(request.recipe.get("restore_intent"))
        if record.restore_intent is not None:
            record.recipe.update({k: record.restore_intent[k] for k in ("desktop", "slot", "program", "mode", "target", "layer")})
        self._before_register(record)  # All correlation checks passed; persist before acknowledging a new ID.
        self.managed_windows[identifier] = record
        self.uuid_by_managed_id[managed_id] = identifier
        self._next_managed_number += 1
        self._finish(request, "succeeded", managed_id)
        self._changed()
        return deepcopy(record)

    def get_window(self, identifier):
        """Lookup by UUID or managed ID; return a copy, not writable state."""
        if identifier in self.uuid_by_managed_id:
            identifier = self.uuid_by_managed_id[identifier]
        else:
            identifier = canonical_uuid(identifier)
        record = self.managed_windows.get(identifier)
        return deepcopy(record) if record is not None else None

    def set_presence(self, window_uuid, state, observation=None):
        """Model-only state transition; event wiring belongs to Step 1.4b."""
        if state not in PRESENCE_STATES:
            raise RegistryError("invalid window presence state")
        identifier = canonical_uuid(window_uuid)
        record = self.managed_windows.get(identifier)
        if record is None:
            return False  # Never adopt an unregistered observation.
        if state == "present":
            # After a missing/uncertain transition, re-adoption requires a
            # future explicit verification path, not merely a matching UUID.
            if record.presence != "present" or not isinstance(observation, dict):
                raise RegistryError("present state cannot be restored implicitly")
            if canonical_uuid(observation.get("uuid")) != identifier:
                raise RegistryError("observation UUID mismatch")
            record.observation = deepcopy(observation)
        else:
            record.presence = state
        self._changed()
        return True

    def retire_missing(self, managed_id, *, window_uuid, request_id):
        """Remove one confirmed absent registration, never recycle its alias.

        Native absence/close authentication and sweep confirmation belong to
        the broker. Check both indexes and the original request before mutation;
        ordinary missing observations alone must never call this operation.
        """
        identifier = canonical_uuid(window_uuid)
        record = self.managed_windows.get(identifier)
        if (record is None or record.managed_id != managed_id
                or record.window_uuid != identifier or record.request_id != request_id
                or self.uuid_by_managed_id.get(managed_id) != identifier
                or record.presence != "missing" or record.placement == "pending"):
            raise RegistryError("retirement requires the same inactive missing registration")
        del self.managed_windows[identifier]
        del self.uuid_by_managed_id[managed_id]
        self._changed()
        # Launch and close result histories remain independently bounded.
        return True

    def set_placement(self, window_uuid, state):
        """Track placement separately from registration and window presence."""
        if state not in PLACEMENT_STATES:
            raise RegistryError("invalid placement state")
        record = self._existing_window(window_uuid)
        allowed = {
            "not_requested": ("pending",),
            "pending": ("succeeded", "failed"),
            "succeeded": ("pending",),
            "failed": ("pending",),
        }
        # A disappeared window may finish an already pending placement as
        # failed. Never declare placement succeeded unless presence is present.
        if (state not in allowed[record.placement]
                or (state != "failed" and record.presence != "present")):
            raise RegistryError("invalid placement transition")
        record.placement = state
        self._changed()

    def set_connection(self, window_uuid, state, *, application_reported=False):
        """Store an explicitly reported connection outcome, not inferred SSH.

        Does not create an established application_session. This API is an
        internal model seam; application-specific events are later work.
        """
        if state not in CONNECTION_STATES:
            raise RegistryError("invalid connection state")
        if not application_reported:
            raise RegistryError("connection status requires application reporting")
        self._existing_window(window_uuid).connection = state

    def _existing_window(self, window_uuid):
        record = self.managed_windows.get(canonical_uuid(window_uuid))
        if record is None:
            raise RegistryError("unknown managed-window UUID")
        return record

    def _active_request(self, request_id, allowed_states):
        request = self.requests.get(request_id)
        if (request is None or self._active_request_id != request_id
                or request.state not in (allowed_states if isinstance(allowed_states, tuple)
                                         else (allowed_states,))):
            raise RegistryError("unknown, inactive or incompatible request")
        return request

    def _finish(self, request, state, detail):
        if state not in TERMINAL_REQUEST_STATES:
            raise RegistryError("invalid terminal request state")
        request.state = state
        request.result = detail
        self._active_request_id = None
        self._completed[request.request_id] = None
        while len(self._completed) > self._completed_limit:
            old_id, _ = self._completed.popitem(last=False)
            del self.requests[old_id]
