# Step 1.5c.5a — Dolphin SFTP implementation review and advisory correction

**Published implementation:** `98e366899a611e000f246b74abb4906f7238db8b` on
`task/joetoo-kwin-step1.5c5-remote-access`. Managed Dolphin SFTP has been natively
demonstrated on gmki91 X11 and q552u01 Wayland; see the [acceptance record](step1.5c5a-native-acceptance.md).
This branch/whole milestone is not declared merged. The newly authorized advisory
correction below is uncommitted and awaits maintainer-native validation.

## Implementation history and source evidence

The approved implementation was prepared from `5dd60d3`, following planning baseline
`099096e`; its prior review/diff and headless results remain historical evidence.
The grammar/security decisions were approved before dispatch was implemented.

The exact release worker was available read-only in local Portage distfiles:
`/var/cache/distfiles/kio-extras-26.04.3.tar.xz`, member
`kio-extras-26.04.3/sftp/kio_sftp.cpp` (inspected temporary copy under /tmp).
Its SSH option/config path, changed/unknown-key dialog and empty-path listing
handling agree with the previously inspected upstream references. The installed
worker's embedded Qt metadata includes the SFTP worker IID and protocol key used
by discovery. No newer ebuild was substituted as installed worker source.
See the [approved contract investigation](step1.5c5a-dolphin-sftp-contract.md) for
source links and the exact grammar. No change to SSH configuration or special
SSH setup was established as necessary; KIO/libssh precedence remains its own.

**Maintainer feasibility evidence (November 1, 2026, gmki91):** entering
`sftp://joe@nuthuvia.brendler/home/joe/` manually in Dolphin connected and navigated
the remote filesystem. Kate opened `/etc/hostname` and showed `nuthuvia`; the
maintainer supplied a screenshot in the review conversation. No passphrase prompt
appeared; a cached key was reported. This is maintainer-executed interactive KIO
feasibility, not agent testing, managed PID/UUID acceptance, proof of a specific
authentication mechanism, changed-key validation, port precedence or Wayland acceptance.
Subsequent managed X11/Wayland acceptance is recorded separately; it does not
retroactively turn this earlier feasibility test into a managed-launch test.

## Published behavior and changed paths

- `libexec/joetoo_kwin_sftp_target.py` is a new pure standard-library validator.
  One raw target arrives on stdin, never argv; JSON stdout contains only a valid
  normalized URL. It implements the approved account/host/IPv4/bracketed-IPv6,
  port, ASCII/UTF-8 percent encoding, absent-vs-root path and rejection rules.
  Paths are decoded once and re-encoded, not resolved on the local filesystem.
  All errors are redacted; parser exceptions never echo rejected userinfo.
- `libexec/joetoo-kwin-plan-functions` admits sftp only for Dolphin and validates
  every target before plan display/confirmation. Invalid record field/control
  diagnostics no longer repeat the entire potentially credential-bearing record.
  Accepted local/SSH/deferred recipes, geometry and logical slots remain unchanged.
- `libexec/joetoo_kwin_sftp_capability.py` is a separate offline metadata detector.
  It checks Qt plugin roots, Gentoo installed kio-extras CONTENTS records, then
  optional Qt6 qtpaths queries. Tool candidates may come from PATH or the Dolphin
  installation's Qt6 tool locations. Actual plugin paths come from environment,
  installed records or Qt's query, never a fixed /usr/lib64 path. ELF/KIO metadata
  is read without dlopen or worker execution. No Qt GUI is started.
- `libexec/joetoo-kwin-launch-functions` preflights Dolphin and confirmed worker-file
  availability for the complete plan; holds canonical remote URIs separately from
  local directories; builds `(dolphin --new-window -- "$validated_sftp_uri")`.
  Existing managed launch, launch PID handoff, exact UUID/slot ownership, grouping,
  Busy/partial-failure rules, lock lifetime and initial stack/focus are reused.
  The notice says the location is being requested and authentication/listing are
  unverified; a placed window does not become a transport success assertion.
- `joetoo-kwin` adds recipe help and effective capability-timeout display;
  `joetoo-kwin-template.conf` documents the setting and a commented SFTP recipe,
  replacing its obsolete statement that no graphical remote transport is supported.
- `tests/test_sftp.py` adds parser/capability and actual orchestration-with-mocks
  tests; `tests/test_step1_5a_plan.py` copies the new helpers into its existing harness.
  Existing installed-header integration is retained and exercised for SFTP too.
- Task evidence: this review, the earlier contract status update, native fixture,
  HANDOFF Section 5 and a complete project-relative candidate diff.

Broker, registry, resident, SSH rcfile, local resource helper, architecture, README,
maintainer scope and protected repositories are unchanged. No D-Bus extension,
transport telemetry, VPN gate, VNC or RDP work was introduced.

## Discovery, timing and outcome limits

`qtpaths6` absence does **not** mean missing SFTP. Installed-file records and explicit
Qt plugin paths can establish the worker's presence independently. The actual
read-only detector run here found `/usr/lib64/qt6/plugins/kf6/kio/sftp.so` through
installed-package/worker metadata. This confirms local file capability, not dynamic
load, authentication, directory listing or either host's managed-native acceptance.
Unknown layouts/no detector yield an explicit **inconclusive** preflight error saying
a working installation is not disproved. Report that compatibility question before
any bypass; do not create windows on uncertain capability or mislabel it a transport
failure. Alternate Qt plugin layouts may require a focused discovery refinement.

New `sftp_capability_timeout_ms=2000`, validated 1..10000 ms in planner and helper,
is displayed and assigned in the template. It bounds optional Qt query subprocess
waiting with a shared remaining-time budget; it is not a remote connection timeout.
Metadata filesystem reads are ordinary local inspection, not KIO network operations.
No remote polling, automatic retry, host-key acceptance, credential storage, SSH
config rewriting or new broker lease was added. KIO's existing GUI prompts/cache
and transport bounds remain KIO behavior, not joetoo-managed telemetry/settings.

The operator must independently verify new fingerprints and cancel unexpected changed
keys. This code cannot enforce cancellation inside KIO's own dialog; that limitation
was explicitly accepted. Authentication dialogs can interfere with correlation or
bounded focus: report partial/failure honestly and seek a separate decision if native
observations require changing the accepted identity/layout contract. Do not weaken it.
Broker connection fields remain uninstrumented, regardless of visible KIO activity.

## Published implementation validation

**301 Python tests PASS** without skips, including retained installed-header
integration; **four Node discovery test files PASS**. The focused SFTP suite has
**14 passing tests**, rerun after the final redacted-error-message refinement.
Bash syntax (including template/native fixture), Python compilation, ShellCheck and
whitespace checks PASS. Template-only lint excludes SC2034 for sourced assignments.
Raw temporary outputs are /tmp/joetoo-sftp-{focused,python,node,shellcheck}.log; no duplicate
historical log bundle is created. Tests perform no real GUI or SSH/SFTP connection.
The focused cases cover URI tables, one-pass normalization, secret redaction/stdin,
missing executable, plugin evidence with/without Qt tools, custom prefixes and failed
queries, full-plan rejection, offline -c, cancellation, captured argv, mixed desktop
groups, ambiguous SFTP identity, independent remote-state notice and installed header.
Existing full suites retain local Dolphin, SSH original Bash, ownership, live-child
lock release, partial failure and group/focus coverage.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_*.js
python3 -m py_compile libexec/joetoo_kwin_sftp_target.py libexec/joetoo_kwin_sftp_capability.py tests/test_sftp.py
bash -n joetoo-kwin
bash -n libexec/joetoo-kwin-plan-functions
bash -n libexec/joetoo-kwin-launch-functions
bash -n joetoo-kwin-template.conf
shellcheck -x -s bash joetoo-kwin libexec/joetoo-kwin-plan-functions libexec/joetoo-kwin-launch-functions
shellcheck -s bash -e SC2034 joetoo-kwin-template.conf
git diff --check
# End of commands

```

## Native acceptance and new advisory correction

At published revision 98e3668 the maintainer reports 301 Python and 50 JavaScript
cases passing on both hosts. Two separate Dolphin UUIDs were registered/placed and
stacked on desktop 2 while desktop 1 was active; active-desktop SFTP focus is **NOT
TESTED**. Remote /etc/hostname was opened in Kate on X11 and KWrite on Wayland,
showing nuthuvia. Wayland capability preflight passed for the tested installation.
The [acceptance record](step1.5c5a-native-acceptance.md) preserves precise outcomes
and qualifications, including the X11 negative DNS destination where both windows
succeeded but Dolphin correctly displayed a resolution error.

### Post-confirmation NSS and TCP advisory

Authorized narrowly after that native negative case. New
`libexec/joetoo_kwin_sftp_advisory.py` extracts the host/explicit port from the validated
URI on stdin. It runs bounded `getent ahosts`, then the established `nc -n -z -w`
zero-I/O probe against returned numeric addresses. The nc timeout is derived from
configuration (rounded to tool seconds); Python's subprocess timeout enforces the
remaining per-stage budget across IPv4/IPv6 addresses. No Python socket connection
backend or mandatory new package is introduced. The Konsole SSH probe is unchanged.

Global defaults are `sftp_advisory_enabled=$TRUE` (disable with `$FALSE`),
`sftp_advisory_timeout_ms=2000` per stage (1..10000 ms), and
`sftp_advisory_ssh_port=22` fallback (1..65535). Explicit URI ports override the
probe fallback only. All are validated, assigned in the template and displayed in
effective configuration; KIO/libssh may still select a different endpoint/port.

Only confirmed execution calls the advisory immediately before the SFTP launch.
-c, syntax/capability preflight, invalid plans and confirmation decline remain
network-free apart from arbitrary side effects of the already-trusted Bash config.
Numeric literals bypass NSS. Failure, timeout, absent tools, unsupported nc output
or helper/reporting failure never veto Dolphin. The validated URL and launch/layout
classification are unchanged. A missing NSS key yields one warning and skips TCP;
timeout/uncertainty are qualified instead of asserting the host cannot be reached.
The console explains where to adjust time tolerance and that KIO/SSH configuration
may differ. Debug output exposes stage statuses without repeating the warning.

NSS is not necessarily DNS; an alias may work in KIO even if direct NSS fails.
An nc failure is not definitive host-down proof, and a connected TCP port proves
neither an SSH service nor authentication/listing. No banner/authentication probe,
SSH profile rewriting, DNS-over-TLS/VPN management or monitoring is added. Dolphin
is always launched with its requested URI, including failures: the visible error
retains mission purpose and permits immediate manual correction/retry, with the
config updated separately. Broker, registry, resident and SSH rcfile are unchanged.

### Correction validation and next gate

Correction validation: **312 Python tests PASS, no skips** (including installed-header coverage); **4 Node discovery files PASS**, no skips. Bash syntax, Python compilation, ShellCheck and whitespace checks PASS. Node reports file-level counts on this host; the maintainer’s earlier 50 JavaScript cases remain separately attributed. Resolver/nc commands are mocked;
no real DNS, TCP, SSH or SFTP operation was performed by Codex. Tests cover numeric
IPv4/IPv6, default/explicit ports, NSS failures/timeouts/unavailable utilities,
qualified nc results, advisory disable/helper failure, unchanged argv and mixed-plan
completion, cancellation/offline -c and invalid offline preflight. Existing original
Bash, lock, ownership, placement and layer suites remain intact.

See the [remaining native checklist and exact commands](step1.5c5a-native-acceptance.md#remaining-acceptance-checklist)
for resolvable and unresolvable endpoints. This correction is **PENDING native
acceptance on both hosts**. New/changed-host-key prompts, active-desktop SFTP focus,
nondefault-port/profile precedence and further endpoint variants remain qualified;
do not label them PASS from mocks or normal base runs. No new implementation in
1.5c.5b/c or Step 1.5d is authorized. Maintainer reviews the complete advisory diff,
then runs the narrow native checks and decides acceptance/publication separately.

Complete correction diff, including the new helper, tests and acceptance record: [step1.5c5a-advisory.patch](step1.5c5a-advisory.patch). Concurrent maintainer architecture/scope edits and the preexisting native_joe fixture are excluded.

Documentation checks: new relative file links resolve. Two existing README links to `task_step1.4/HANDOFF.md` are absent locally and unchanged by this correction. Scoped `git diff --check` passes; the full working-tree check reports EOF blank lines in concurrent maintainer edits to ARCHITECTURE.md and Step1.5c5_implementation_scope.md, which the agent leaves untouched.
