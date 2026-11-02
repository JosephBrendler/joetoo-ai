# Step 1.5c.5a — Dolphin SFTP contract and implementation status

**Current baseline:** `98e366899a611e000f246b74abb4906f7238db8b` on
`task/joetoo-kwin-step1.5c5-remote-access`. The maintainer approved the URL grammar,
encoding/redaction, KIO operator trust policy and offline capability checks and
explicitly authorized implementation. SFTP is implemented and published on this task
branch, with managed native demonstrations on X11 and Wayland. Neither the branch
nor the entire 1.5c.5 milestone is declared merged. See [native evidence](step1.5c5a-native-acceptance.md)
and [implementation/correction review](step1.5c5a-review.md).

## Investigation provenance and resolved decisions

The original investigation used branch/main `5dd60d397d00539ddfc973455e178dfefda80267`,
containing planning baseline `099096e33fe568579b219ffced4131f211af2a3f`.
At that time SFTP dispatch was unsupported and exact worker source retrieval over
the web was unavailable. Those were historical observations, not current limitations.
Implementation subsequently inspected the exact Portage distfile
`/var/cache/distfiles/kio-extras-26.04.3.tar.xz`, member
`kio-extras-26.04.3/sftp/kio_sftp.cpp`. Host-key/config/empty-path handling agreed
with the upstream investigation. The newer ebuild was not used as installed worker source.

Inspected local package metadata identified Dolphin/kio-extras 26.04.3 and libssh
0.11.5; actual worker-file metadata and Qt plugin-path discovery were inspected.
This is distinct from the maintainer's successful interactive gmki91 browsing and
later managed X11/Wayland acceptance. No agent-operated GUI/SSH/SFTP test is claimed.

Source references retained from investigation:

- [Dolphin 26.04.3 main.cpp](https://raw.githubusercontent.com/KDE/dolphin/v26.04.3/src/main.cpp)
  bypasses existing-instance attachment with --new-window.
- [Dolphin validateUris](https://raw.githubusercontent.com/KDE/dolphin/v26.04.3/src/global.cpp)
  consumes QUrl input; joetoo supplies a complete validated URL.
- [KIO SFTP worker](https://raw.githubusercontent.com/KDE/kio-extras/master/sftp/kio_sftp.cpp)
  was an upstream investigation reference; exact release inspection followed locally.
- [libssh API](https://api.libssh.org/stable/group__libssh__session.html) describes
  config parsing; the fetched API version was newer than local 0.11.5, so complete
  OpenSSH directive/precedence equivalence was never asserted.

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

| Accepted TARGET | Meaning / canonicalization |
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
The executable validator implements these rules; native endpoint-variation coverage is qualified in the acceptance record.

## Accepted execution, security and outcomes

Validated URI data is passed as one argument in
`(dolphin --new-window -- "$validated_sftp_uri")`, with no shell evaluation.
Unvalidated targets reach the validator through stdin, not helper argv; invalid
record and target diagnostics are redacted. No target is replaced by local HOME
or another mode when remote access fails. Slots/layers, desktop grouping, locking,
positive PID/new-UUID correlation, exact placement and bounded stack/focus remain
the accepted c4 mechanisms. Delegated/ambiguous windows are never adopted.

Dolphin is local; KIO/libssh owns remote SFTP, not ssh_wrapper or remote GUI
execution. Existing user/system SSH configuration is preferred where supported;
not every OpenSSH directive or override rule is guaranteed. Host-key verification
stays enabled. New fingerprints require independent verification; unexpected
changed-key prompts must be canceled and investigated. KIO may offer a user override,
so this is the explicitly accepted operator policy, not a new non-overridable
launcher enforcement mechanism. No automatic trust, credential store or SSH config
rewriting is implemented. Report material native incompatibilities instead of
weakening that policy.

Offline preflight validates the whole executable plan and confirms local Dolphin/
worker-file capability before confirmation. Qt plugin paths, Gentoo installed-file
records and optional Qt6 queries are used; qtpaths is not unconditional. Inconclusive
discovery is reported honestly, not as proof that a working installation lacks SFTP.
The window/geometry/stack/focus results remain independent of authentication and
remote directory availability. The launcher reports only that browsing was requested;
KIO errors and GUI state remain visible for diagnosis, correction and retry. Broker
connection fields are not SFTP telemetry. No broker/resident API changes were required.

## Approved post-confirmation advisory correction

The newly authorized correction adds two optional, non-enforcing checks immediately
before each confirmed SFTP launch: direct NSS resolution (`getent ahosts`), then a
bounded `nc` zero-I/O TCP probe of returned numeric addresses. Numeric IPv4/IPv6 skip
NSS. The original validated URI always reaches Dolphin unchanged. This reuses the
nc probe approach established for Konsole; the accepted Konsole implementation is
not redesigned here. Python bounds subprocess execution and classifies results.

Defaults in the template/effective configuration:

- `sftp_advisory_enabled=$TRUE`; set `$FALSE` to disable both stages.
- `sftp_advisory_timeout_ms=2000` per stage, supported 1..10000 ms.
- `sftp_advisory_ssh_port=22`, supported 1..65535; an explicit URI port is used instead
  for the advisory only. KIO/libssh configuration may select another endpoint/port.

No lookup/probe runs in -c, URI validation, capability discovery, before confirmation
or after cancellation. A failed lookup produces one qualified warning and skips TCP;
missing tools/unsupported output are uncertainty. Timeouts identify the timeout
setting rather than assert unreachability. A failed nc check is not proof the host
is down; a successful TCP connect proves neither SSH service identity nor SFTP
access/authentication/listing. Warnings do not change launch counts, ownership or
layout classification, and never suppress Dolphin's own connection error. The failed
Dolphin view preserves the mission's purpose and allows immediate manual correction;
configuration can be updated separately. No network monitoring/controller is added.

The advisory correction is headless-tested only until the maintainer runs the
[pending native checks](step1.5c5a-native-acceptance.md#remaining-acceptance-checklist).
Changed-host-key prompts, nondefault-port precedence, additional SSH aliases, IPv6
remote endpoints and active-desktop SFTP focus remain qualified/not tested unless
specifically recorded there. 1.5c.5b/c and 1.5d remain separately gated.
