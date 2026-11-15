# Step 1.5c.1–1.5c.3 candidate review

Branch task/joetoo-kwin-step1.5c-configured-launch; baseline
31400fe0d2be05064b898cf520d06d6445e13839 (also local main/cached origin/main).
Existing branch reused; no fetch. Preexisting HANDOFF edits, maintainer clarification
and earlier interface-review evidence preserved. Latest clarification explicitly
permits the bounded broker changes despite the older exclusions table.

## Result

-o loads trusted config using defaults/config/CLI verbosity precedence, validates
shared geometry and the complete executable plan, checks public broker state and
original managed slot associations, displays effective config/plan and overlap
warnings, and calls installed confirm_continue_or_exit before launch. It rechecks
state after confirmation and between entries. -c still describes all planner modes.

Supported execution recipes: konsole|ssh|HOST and konsole|local|EXECUTABLE_BASENAME.
The local executable has no inline argument parsing or eval; graphical, direct,
via-ssh and swr recipes fail preflight. ssh uses ssh_wrapper, not swr; the startup
helper probes nc -z -w 2 on port 22 (stripping optional username for the probe),
retains the same interactive Bash and prints an escaped manual retry command.
Neither transport failure nor logout closes that shell. Startup helpers remain
checkout-relative: existing POC installer is not expanded by this task.

Managed launch reuses SubmitManagedLaunch, exact child PID handoff, registration
polling and placement verification. Entries run sequentially. Definitive isolated
failure marks the layout incomplete and permits independent subsequent entries;
unknown/ambiguous registration, nonterminal placement, transport/query failure or
unresolved Busy stops progression. Already created windows remain untouched.

Broker summary adds intended:{desktop,slot}; RegistryStatus adds the current
placement_transaction:{id,state} snapshot (IDLE when none). Querying does not force
stale work to success or silently release ownership. SubmitManagedLaunch guards
original slot associations before any transaction mutation, including missing and
uncertain presence. No association is released automatically in this increment.
Manual desktop/geometry movement does not reassign logical slots. Recipe targets
and other private fields remain excluded. D-Bus signatures and resident/registry
source are unchanged. Broker transport state is not an SSH session monitor.

## Validation

235 Python tests PASS without skips, including installed-header integration;
3 Node test files PASS. Syntax and ShellCheck results are in accompanying logs.
Initial failures: obsolete -o-not-implemented assertion and mock JSON quoting were
corrected; initial lint findings were corrected. Final regressions rerun.
Coverage includes original association after movement, conservative missing/uncertain
guards, atomic duplicate rejection, distinct-slot repeated-host launches, confirmation,
invalid/unsupported whole plans, sequential progression, partial failure, unresolved
placement/Busy and original-shell SSH failure/unreachable handling with no network.
The existing managed-transaction tests continue checking arm-before-launch/PID handoff.

Whitespace: agent production/tests pass git diff --check. Full diff retains one
preexisting trailing space in maintainer-owned HANDOFF approval text; not altered.
No native tests, SSH connections, installation, service operations or publication.

## Review inventory and next gate

Modified implementation: joetoo-kwin, shared plan-functions, bounded joetoo-kwind.
New implementation: launch-functions and session.bashrc under libexec.
Tests: new test_step1_5c_launch.py; obsolete -o assertion removed from planner test.
Evidence: this report, example configuration, validation logs, complete review patch,
and appended Codex iteration. Earlier interface review is preserved historical evidence.
Maintainer-owned clarification and preexisting HANDOFF changes remain distinct from
agent edits. No temporary files or screenshots included in the review patch.

Maintainer/cloud code review next, then maintainer-operated native X11/Wayland tests:
confirm cancellation, repeated-host windows, offline SSH placeholder/same-shell retry,
manual movement followed by duplicate rejection, and partial failure/contention.
Verify installed daemon supports additive preflight JSON before running -o. No
publication, native test operation or broader graphical work is authorized here.
