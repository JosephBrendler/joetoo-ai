# Step 1.5c.5a — Dolphin SFTP implementation candidate

## Baseline, authority and source evidence

Branch `task/joetoo-kwin-step1.5c5-remote-access`, HEAD/local main
`5dd60d397d00539ddfc973455e178dfefda80267`, descendant of planning baseline
`099096e33fe568579b219ffced4131f211af2a3f`. The starting dirty work was the prior
contract report and HANDOFF row 21; both were preserved. The maintainer also added
approval annotations/native evidence to that report and an explicit authorization
subsection in HANDOFF Section 4 during this iteration; those were retained. Agent
HANDOFF edits add only row 22. The full candidate diff includes these maintainer notes. Latest explicit maintainer
approval resolves the grammar/security gate, including native KIO operator trust
policy and optional rather than mandatory qtpaths discovery. No branch, staging,
commit, publication, installation or service operation was performed.

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
No corresponding managed SFTP native acceptance is yet claimed on either host.

## Candidate behavior and changed paths

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

## Validation

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

## Maintainer native acceptance — NOT TESTED by Codex

Use the same reviewed implementation on gmki91 X11 and q552u01 Wayland; record the
exact implementation SHA (or HEAD plus reviewed diff before the first commit), host,
capability result, window UUID/slot and independent layout/remote results. Existing
broker/resident contracts are unchanged. Run the checkout CLI with its colocated new helpers. If testing an installed CLI,
the maintainer must supply the matching helpers through the existing candidate
procedure. No broker/resident reload is required by this increment. Do not bypass
an inconclusive detector.

The [native fixture](step1.5c5a-native.conf) has one SFTP panel and a local Dolphin
underlay. Choose an unused intended desktop/slot pair and manually display that
desktop for a focus check. Example 10 below is not a claim that it is currently free.
Keep an unrelated Dolphin open to test new-window isolation. Inspect the trusted
fixture before sourcing it. No configuration/host files are changed by -c.

```bash
TEST_DESKTOP=10 ./joetoo-kwin -c -f task_step1.5/step1.5c5a-native.conf
TEST_DESKTOP=10 ./joetoo-kwin -vv -o -f task_step1.5/step1.5c5a-native.conf
# End of commands

```

First decline: no desktop provisioning/application launch. Then approve with fresh
slots: expect separate positively registered UUIDs, exact placement, panel above
under, preferred panel focus where permitted, and a requested/unverified SFTP notice.
Manually verify the remote listing in Dolphin (and the known remote hostname file
if desired). Record any dialog, cancellation, error or later navigation separately
from KWin placement/stack/focus. No secret screenshot/log content should be published.

On further fresh desktops, override SFTP_TEST_URI with the approved endpoint and a
percent-encoded directory containing spaces/UTF-8, omitted path, explicit `/`, and
nondefault user/port/alias where actually used. Verify URI/profile precedence instead
of assuming OpenSSH behavior. Exercise a known missing directory and a reserved
unreachable `.invalid` host; observe KIO errors without relabeling placed windows as
successful remote connections. Do not tamper with production known_hosts or keys.
Test naturally required authentication prompts and cancel safely. An unsupported
IPv6 test environment is NOT TESTED natively, with parser coverage retained.

An invalid URI should reject before confirmation and without spawning Dolphin:

```bash
TEST_DESKTOP=10 SFTP_TEST_URI='sftp://files.example:0/' ./joetoo-kwin -o -f task_step1.5/step1.5c5a-native.conf
# End of commands

```

Confirm the unrelated Dolphin is not adopted and duplicate logical slots still
reject. Reuse c4 evidence for unchanged geometry/manual-control/SSH behavior; do not
repeat its entire battery. Native prompt/delegation/security incompatibilities must
be reported for focused review, not solved through unsafe fallbacks.

Next actor: maintainer reviews the [complete diff](step1.5c5a-implementation.patch),
independently validates, then runs native X11 acceptance before publishing the exact
candidate for Wayland testing. Publication requires separate authorization. Stop here;
1.5c.5b/c and 1.5d remain outside this implementation.
