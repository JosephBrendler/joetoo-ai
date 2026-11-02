# Step 1.5c.5a — Dolphin SFTP contract recommendation

**Status: Maintainer-approved contract; executable implementation authorized for Step 1.5c.5a.**

The maintainer approved the proposed URL-only SFTP grammar, percent-encoding and diagnostic-redaction requirements, native KIO/libssh authentication and operator-managed host trust, and offline capability discovery with independent window/transport reporting.

KIO/libssh compatibility with the established joetoo SSH configuration must be verified where relevant; full OpenSSH configuration equivalence is not assumed. `ssh_wrapper` is not required for Dolphin SFTP. An unexpected changed-host-key warning must be canceled and investigated; the launcher does not technically enforce this operator decision.

The maintainer also approved offline Dolphin/SFTP-worker capability checks, without requiring `qtpaths6` unconditionally or initiating a network connection during preflight.

The detailed proposed grammar and validation rules below are now accepted as the implementation contract, subject to reporting any material incompatibility discovered during development.

## Baseline and inspected evidence

Verified clean branch `task/joetoo-kwin-step1.5c5-remote-access`, HEAD/local main
`5dd60d397d00539ddfc973455e178dfefda80267`. Intended planning baseline
`099096e33fe568579b219ffced4131f211af2a3f` is its ancestor. The additional commit
installs the active HANDOFF and archives the c4 closure handoff; it changes no
implementation. This is consistent with the requested maintainer-created branch,
not an unexpected source baseline. No fetch or remote-synchronization claim.

Read root/workspace/project AGENTS, workspace workflow, current architecture/README,
[c5 scope](Step1.5c5_implementation_scope.md) and active HANDOFF. Their historical
“proposed”/pending-branch wording does not override the current explicit investigation
authorization; executable dispatch still requires a grammar/security decision.
Relevant header/AAR skills and actual installed j_msg/handle_result conventions were
consulted. No protected repository edits or development workflows are needed.

| Inspected local source | Current behavior / reuse |
| --- | --- |
| [planner](../libexec/joetoo-kwin-plan-functions), `validate_plan`/`calculate_plan` | Rejects sftp mode today; already owns slots, layers, budgets, grouped geometry |
| [launcher](../libexec/joetoo-kwin-launch-functions), `launch_preflight`/`open_plan` | Accepts Dolphin local only; builds array `(dolphin --new-window -- directory)`; confirms complete plan before provisioning/launch |
| [resource helper](../libexec/joetoo_kwin_launch_resources.py), `local_path` | HOME-relative existing local directories; rejects URL targets; leave unchanged |
| [CLI](../joetoo-kwin), `launch_managed_window`/`plan_stage` | Arms managed request, launches independently with FD9 closed, hands actual launch PID to broker, preserves action vs reporting status |
| [broker](../libexec/joetoo-kwind), `SubmitManagedLaunch`/initial-layout methods | Positive PID/new-UUID registration, original slot guard and bounded group finalization; recipe/connection fields do not establish SFTP state |
| [resident](../joetoo-kwin-resident.js), `placeWindow`/`initialLayoutFromBroker` | Exact UUID placement/stack/focus; no knowledge of remote directory listing |
| [template](../joetoo-kwin-template.conf), local-Dolphin/resource/launch tests | Accepted c4 defaults and preservation cases; extend, do not replace |

Read-only local package metadata shows Dolphin **26.04.3**, kio-extras **26.04.3**
with `sftp` enabled, and libssh **0.11.5**. The regular SFTP worker exists at
`/usr/lib64/qt6/plugins/kf6/kio/sftp.so`; readelf shows a libssh dependency.
`/usr/lib64/qt6/bin/qtpaths6 --query QT_INSTALL_PLUGINS` returned
`/usr/lib64/qt6/plugins`. These are observations of this agent environment, not a
verified package inventory on both native hosts. No Dolphin/kioclient, GUI or SFTP
worker was executed. Installed English SFTP help was read.

Primary upstream sources:

- [Dolphin 26.04.3 main.cpp](https://raw.githubusercontent.com/KDE/dolphin/v26.04.3/src/main.cpp):
  `--new-window` skips existing-instance attachment; the main window is created in
  that process with multiple-instance D-Bus service behavior.
- [Dolphin validateUris](https://raw.githubusercontent.com/KDE/dolphin/v26.04.3/src/global.cpp)
  uses QUrl::fromUserInput. Supply a complete validated URL, not ambiguous shorthand.
- [KIO SFTP worker](https://raw.githubusercontent.com/KDE/kio-extras/master/sftp/kio_sftp.cpp):
  `sftpOpenConnection` sets host/user/port and parses SSH config via libssh;
  `openConnectionWithoutCloseOnError` checks server keys and offers authentication
  dialogs/cache. Unknown **and changed** keys can reach a user override dialog.
  `listDir` canonicalizes an empty path as `.`; explicit `/` is different.
- [libssh configuration API](https://api.libssh.org/stable/group__libssh__session.html):
  the library parses SSH configuration, not the OpenSSH executable. Do not assume
  complete OpenSSH-option equivalence or explicit-URI precedence: that API warns
  config parsing may overwrite prior options. The fetched API page describes 0.12, newer
  than local 0.11.5; native alias/authentication behavior needs verification.

Exact kio-extras 26.04.3 source retrieval was unavailable; master and the accessible
25.12.3 source snapshot were inspected as upstream references, not represented as
an exact audit of the installed binary. c4 native evidence supports local Dolphin
identity on X11/Wayland, not untested SFTP/dialog behavior.

## Target grammar

**URL only for this increment:** `sftp://[USER@]HOST[:PORT][/ABSOLUTE/PATH]`.
No scp-style `host:path`, bare-host convenience, relative remote path, query, fragment
or sixth field. A future convenience syntax needs its own explicit decision; URL-only
avoids colon ambiguity with ports/IPv6 and has no extra syntax to synchronize.

- Scheme exactly `sftp://`; require a nonempty authority. USER, when present, is an
  ASCII account token `[A-Za-z0-9_][A-Za-z0-9_.-]*`. Reject colon/password syntax,
  empty user, multiple @ signs and percent-encoded userinfo. Unusual account names
  outside this deliberate first grammar need an explicit future extension.
- HOST: ASCII DNS name or SSH alias token using letters/digits/underscore/dot/hyphen,
  starting with letter/digit/underscore, no empty dotted components (one final dot
  permitted). A numeric/dotted address must be a valid full IPv4 literal. Do not
  resolve DNS/aliases during preflight. Preserve host spelling for SSH alias matching;
  internationalized hostnames must be supplied as ASCII IDNA, not auto-converted.
- IPv6 must be bracketed and validated as a literal; retain brackets in output.
  Reject unbracketed IPv6 and scoped/zone-ID addresses in this increment.
- PORT: optional decimal 1..65535, no leading zeros or empty colon. Omit it in output
  when omitted in input, allowing supported SSH config defaults; never silently add
  port 22. Explicit user/port are URI requests; recommend delegating effective
  precedence to KIO/libssh. Do not promise OpenSSH-style command-line overrides;
  deployed profile-versus-URI precedence needs native verification. If explicit
  endpoint pinning is required instead, resolve that policy before coding.
- An **absent path stays absent**, requesting the server login directory (usually
  account home, potentially chroot-relative), not local HOME. `/` explicitly means
  remote root. Supplied paths must start with `/`; no local HOME/cwd/config-relative
  resolution and no tilde/environment/glob expansion. A tilde component is literal.
- Require ASCII URL input; whitespace, non-ASCII characters and literal percent in
  names use UTF-8 percent escapes (`%20`, `%E2%82%AC`, `%25`). Reject malformed escapes,
  invalid UTF-8 and decoded C0/DEL controls. Reject raw backslash and encoded slash or
  backslash (`%2F`, `%5C`) to avoid separator ambiguity. Actual `/` separates segments.
  Reject decoded dot/dot-dot path segments rather than rely on QUrl normalization.
- Reject raw `?`, `#`, and the configuration delimiter `|`; use path `%3F`, `%23`,
  `%7C` for literal filenames. Reject encoded username/host tricks as above.
  Decode the path exactly once, then percent-encode UTF-8 with `/` and unreserved
  `-._~` safe. Preserve case of path, trailing/repeated slashes and absent-vs-root;
  normalize escapes to uppercase. No recursive decoding or double encoding.

| Valid proposed TARGET | Meaning / canonicalization |
| --- | --- |
| `sftp://nuthuvia` | Alias/hostname, configured/default account/port, login directory |
| `sftp://joe@files.example:2222/home/joe/` | Explicit account/port and absolute directory |
| `sftp://192.0.2.10/` | IPv4, explicit remote root |
| `sftp://joe@[2001:db8::10]:2222/srv/Project%20Files` | Bracketed IPv6 and space in directory name |
| `sftp://files.example/srv/%E2%82%AC%23data` | UTF-8 name containing literal # |
| `sftp://files.example/srv/100%25` | One literal percent, not an escape on a second pass |

Reject: empty target; `nuthuvia`; `joe@nuthuvia:docs`; `sftp:///path`;
`sftp://joe:SECRET@host/` (never echo this target); `sftp://@host/`;
`sftp://2001:db8::1/`; `sftp://[fe80::1%25eth0]/`; ports `0`, `65536`, `022`;
`ftp://host/`; `sftp://host/Project Files`; `sftp://host/x?token=...`;
`sftp://host/x#section`; malformed `%`, `%00`, `%2f`, invalid UTF-8, `/../`.
These are proposed cases, not assertions that a parser has already passed tests.

## Dispatch, credentials and outcome contract

After validation, construct the existing **argument array** with exactly one URL:
`(dolphin --new-window -- "$validated_sftp_uri")`. It is a local Dolphin browsing
through local KIO, never remote Dolphin, SSH X forwarding or shell-evaluated text.
Continue using the existing launch PID/new UUID registration; neither a successful
process spawn nor `--new-window` alone proves identity. A delegating process,
multiple qualifying windows, or an auth dialog winning ambiguous correlation must
fail conservatively. Do not weaken the broker or adopt a title/class-only match.

Use single-quoted recipe examples in trusted Bash configs. Feed the *unvalidated*
TARGET to a pure validator through structured **stdin**, not helper argv. Invalid
userinfo could otherwise expose a password even on a rejected launch. Current
field-count/control diagnostics echo the whole record: narrowly replace that raw
record with an entry-index diagnostic before enabling SFTP. Validator errors must
name the rule/entry, not echo rejected URI/parser exceptions. Valid targets may be
shown in the plan, but contain no credentials, query tokens or fragment secrets.
This is a proposed diagnostic correction for the feature's trust boundary, not an
opportunity to rewrite the planner or its AAR/status infrastructure.

**Security decision:** recommend native KIO authentication, inherited user credentials
facilities and manually verified host trust, with no launcher credential storage,
agent/key management, SSH option rewriting or automatic acceptance. KIO is not
`ssh_wrapper`; successful Konsole SSH does not guarantee the same KIO configuration
semantics. Supported libssh aliases/identity settings may work unchanged; no special
SSH configuration change is established as necessary by this investigation. Agent
visibility in the GUI/KIO environment, optional user/port precedence, key prompts and
any required ProxyJump/ProxyCommand setup need native verification. If the normal
profile does not work, report it and obtain a separate decision; never silently
create a proxy, change SSH config, disable validation or copy private keys.

**Important limitation:** a KIO changed-key override is not OpenSSH strict mismatch
rejection. Proposed operator policy is to cancel unexpected/mismatched-key prompts
and verify/repair trust separately through the maintainer's existing trusted procedure;
new-host fingerprints require independent verification before acceptance. The launcher
cannot technically enforce that operator decision inside KIO's dialog. If strict
non-overridable rejection is required, do **not** approve this minimal route as meeting
that policy: an additional design decision is needed. Existing KIO wallet/credential
prompts are application behavior; they are not a new joetoo credential manager.

| Outcome | Observable by unchanged joetoo interfaces? | Proposed reporting |
| --- | --- | --- |
| Syntax/local executable/worker-file presence | Yes, offline preflight; plugin presence is not load/authentication proof | Reject whole invalid/unsupported executable plan before confirmation |
| Spawn and positively registered UUID | Existing PID/new-UUID transaction and bounded registration | Report launch/registration independently |
| Desktop, geometry, stack, preferred focus | Existing observed broker/resident results | Keep existing verified/partial/incomplete outcomes |
| KIO auth accepted, directory listing, missing remote path, connection timeout | Not reliably through current broker/CLI APIs; visible in Dolphin/KIO | “SFTP location requested; authentication/listing not verified by launcher” |
| Later closure/navigation | UUID lifecycle remains observable; new location/transport is not tracked | Keep registry presence separate from remote state |

Do not run nc/ssh/kioclient as an SFTP health probe during preflight or wait for remote
listing inside the placement transaction. KIO owns its transport timeouts/dialogs;
no new joetoo timeout is proposed. A modal auth dialog can make initial focus or
registration incomplete; preserve truthful terminal results rather than extending
leases or retrying activation while a human types. If native dialogs reveal a required
identity/layout contract change, stop and request approval before altering c4.
Broker `connection:not_attempted` remains an uninstrumented legacy field, not proof
that KIO made no attempt. No new broker telemetry or method signatures are proposed.

## Minimal implementation preparation

| Anticipated path/function | Bounded change |
| --- | --- |
| `libexec/joetoo-kwin-plan-functions::validate_plan` | Admit `sftp` only for Dolphin; validate target offline before display, redact raw bad-record diagnostics; retain deferred -c recipes and all layout logic |
| New `libexec/joetoo_kwin_sftp_target.py` | Pure stdin-to-JSON URI validator/normalizer, importable by tests; fixed redacted errors; no DNS, SSH, GUI or filesystem remote operations |
| `libexec/joetoo-kwin-launch-functions::launch_preflight/open_plan` | Accept only approved dolphin:sftp, cache validated URI separately from local_path, select existing Dolphin argv and independent outcome notice |
| `joetoo-kwin` usage and `joetoo-kwin-template.conf` comments/examples | Document approved recipe/limitations; retain launch_managed_window and configuration discovery |
| Relevant tests / task evidence | Add pure URI cases plus extend real orchestration mocks/installed-header tests; record native evidence after maintainer execution |

Existing resource helper, broker, registry, resident and SSH rcfile remain unchanged.
The new helper avoids modifying the existing read-only resource helper under current
HANDOFF permissions. Reuse plan_stage/report_action, j_msg notice/info/debug and
existing pseudo-boolean conventions; no replacement CLI/reporting framework.

Proposed local capability preflight: require Dolphin and a readable KF6 SFTP worker
under the **resolved Qt6 plugin directory**, not a hardcoded lib64 path. Approve use
of the installed Qt6 `qtpaths6 --query QT_INSTALL_PLUGINS` tool (not necessarily on
PATH here) for that resolution, with a clearly documented executable selection at
implementation review. If the detector is absent or plugin layout cannot be resolved,
fail with an actionable capability error rather than claiming support. This adds a
local discovery dependency, not proof that KIO can load/connect. Confirm the discovery
route on both hosts before accepting code; if alternate Qt plugin search roots are
needed, resolve that narrow compatibility question rather than hardcoding a host path.

## Verification plan, not executed acceptance

| Headless extension | Expected assertion |
| --- | --- |
| URI table | Host/alias/IPv4/IPv6/user/port, absent vs root, escaping, UTF-8, percent literal, malformed/credential/query/control/separator/dot-segment rejection |
| argv/redaction | Single URI argument after --, no eval/glob/substitution, no raw rejected target in diagnostics or helper argv; reserved-character filenames remain data |
| Full-plan preflight | Invalid last entry/missing Dolphin or worker prevents confirmation, provisioning and all launches; -c stays offline; decline causes zero application/network effects |
| Identity/error lifecycle | Positive new PID/UUID; old/delegated/ambiguous/auth-dialog-like candidates never adopted; definite failure continues safely, unresolved state stops |
| Preservation | Mixed local Dolphin/SFTP/Konsole, interleaved groups, slots/layers, pending lock and live-child FD closure; mock remote failure does not fabricate placement/auth success |
| Reporting/header | Existing installed-header integration retained; independent launch vs unverified remote state, action and reporting statuses remain distinct |

After implementation approval and headless review, maintainer runs a small new
battery on gmki91 X11 and q552u01 Wayland **at the same implementation SHA**:

1. Record installed Dolphin/KIO/libssh capability on each host. Use an already trusted,
   reachable endpoint and a fresh intended slot; confirm visible directory listing,
   exact new managed UUID/PID, placement and layer outcome with old Dolphin still open.
2. Exercise omitted path vs explicit `/`, explicit directory with spaces/UTF-8, required
   user/nondefault port, and an SSH alias actually used by the maintainer. Include a
   controlled profile-versus-explicit-URI comparison if precedence matters; do not
   modify production SSH configuration to manufacture it. IPv6 is a
   native case only where an approved reachable IPv6 test endpoint exists; otherwise
   retain parser coverage and record NOT TESTED, not a fictitious native PASS.
3. Exercise normal key/agent use and any real authentication prompt; manually confirm
   which window is managed. Cancel a prompt and use unavailable/missing remote directory
   cases; record GUI/KIO result separately from registration/placement/stack/focus.
   Do not manipulate production known_hosts to manufacture a changed-key case.
4. Cancel -o and reject an invalid complete plan; observe no new managed applications
   or provisioning. Repeat occupied-slot request and one mixed grouped plan. Reuse the
   accepted c4 battery for unchanged geometry/lifecycle rather than rerun everything.

No native command/config fixture is supplied as executable support today: sftp is
still rejected. No implementation suites were rerun for this proposal. Performed
read-only source/package/ELF/Qt-path inspection, ancestry/status checks and final
documentation link/whitespace checks only. No SFTP/SSH connections, GUI launches, service or
package changes, source edits, commits or publication.

## Maintainer decisions made

1. Approved [20261101-18:51:06] URL-only grammar, its restricted account/host tokens and rejection table;
   no shorthand this increment; absent path means login directory, `/` means root.
2. Approved [20261101-18:51:06]  percent-encoded ASCII input and the single decode/re-encode rules, including
   no encoded separators/dot segments; approve stdin validation and redacted errors.
3. Accepted [20261101-18:51:06] with clarification - approved focused offline SFTP capability checks,
   within narrowly bounded task of implementing a reliable discovery mechanism that works on both development hosts.
   Do not perform a network connection as part of preflight. 
   joetoo ssh/sshd configuration requires strict-host-key, ask design. Approved delegation
   of effective URI/profile precedence to KIO/libssh, or require a pinned-endpoint
   contract and deployed evidence first. Do not assume OpenSSH
   strict behavior or require nonstandard SSH changes without host-specific evidence.
4. Approved [20261101-18:51:06] “remote outcome unverified” reporting with no broker telemetry and the
   proposed local Qt6 plugin capability discovery dependency/compatibility check.

## Maintainer decisions required before executable work



Recommended next actor: maintainer/cloud review of these decisions, followed by an
explicit implementation instruction. This proposal itself grants none of them.

## Maintainer-native SFTP feasibility evidence:

On November 1, 2026, the maintainer successfully used Dolphin on `gmki91` (KWin X11) to browse `sftp://joe@nuthuvia.brendler/home/joe/`, navigate to the remote `/etc/hostname`, and open it in Kate. The displayed file contained `nuthuvia`. No passphrase prompt appeared; the maintainer reported that the SSH identity was already cached.

This establishes functional Dolphin/KIO SFTP browsing for the tested destination and authentication environment. It does not establish managed-launch correlation or placement, compatibility with every OpenSSH configuration directive, changed-host-key handling, or native functionality on `q552u01`.

The maintainer also supplied Portage build evidence confirming that `kio-extras-26.04.3` on `gmki91` was built with SFTP support. Worker installation and actual successful remote browsing are separate, complementary evidence.
