# Step 1.5c.5a native acceptance

Provenance: **maintainer-reported native results**, not Codex-operated tests.
Published implementation baseline: `98e366899a611e000f246b74abb4906f7238db8b`,
branch `task/joetoo-kwin-step1.5c5-remote-access`. Native logs/screenshots were
supplied in the maintainer review conversation; this summary does not invent
additional artifact paths. The advisory correction following this commit is
uncommitted and has **pending maintainer-native validation**.

| Scenario at published baseline | gmki91 / KWin X11 | q552u01 / KWin Wayland |
| --- | --- | --- |
| Python regressions | PASS: 301 tests, maintainer run | PASS: 301 tests, maintainer run |
| JavaScript regressions | PASS: 50 tests, maintainer run | PASS: 50 tests, maintainer run |
| Local SFTP-worker capability preflight | PASS for tested launch | PASS for tested installation |
| Managed SFTP Dolphin and local underlay | PASS: independent registration, placement and stacking | PASS: independent registration, placement and stacking |
| Remote nuthuvia browsing and hostname file | PASS: remote file opened; earlier interactive feasibility used Kate | PASS: remote /etc/hostname opened in KWrite, content nuthuvia |
| Active-desktop SFTP focus acquisition | NOT TESTED: desktop 2 launch while 1 active | NOT TESTED: desktop 2 launch while 1 active |
| Inactive-desktop focus suppression | PASS for reported layout | PASS for reported layout |
| New DNS/NSS + TCP console advisory | PENDING native correction validation | PENDING native correction validation |

The earlier November 1 interactive gmki91 feasibility test entered
`sftp://joe@nuthuvia.brendler/home/joe/` directly in Dolphin and opened remote
`/etc/hostname` in Kate, showing `nuthuvia`. No passphrase prompt appeared; a cached
SSH identity was reported. That demonstrates the tested KIO environment, not a
particular key/agent mechanism or all supported SSH directives.

## Negative destination — X11

Maintainer test on November 1 used desktop 4 with an SFTP panel targeting
`sftp://joe@raspi23204.brendler/home/joe/` and a local Dolphin underlay.
SFTP window win-003 UUID `9905bc13-3bc8-42b2-8f66-3ac47758e220` and local win-004
UUID `603eb581-7766-4490-b714-6e86126090b8` independently registered and placed.
Geometry and panel/under stack verified; focus was not attempted because desktop 1
was active. The console reported 2/2 windows completed. **Window/layout PASS.**

Dolphin reported `Failed to resolve hostname raspi23204.brendler (Name or service
not known)` and unsuccessful remote loading. **Remote mission FAILED (expected
negative test)**. This is not a placement failure. Dual-stack DNS, encrypted upstream
resolution and intermittent ISP/VPN transport can also affect future cases; none is
claimed as the cause of this observed hostname error. The new advisory neither
manages those services nor replaces Dolphin's failure display.

## Remaining acceptance checklist

- **PENDING correction:** on both hosts test a resolvable, reachable endpoint and an
  unresolvable name, using fresh intended slots and the reviewed corrected version.
  Confirm qualified console advisory on failure and unchanged SFTP URI in Dolphin;
  both managed windows must still launch/register/place. Verify remote browsing or
  Dolphin's own error separately from layout completion.
- **PENDING correction:** optional disable, resolver/probe unavailability and timeout
  are headless-covered. Native timeout/tool manipulation is optional, not a requirement
  to alter system configuration; collect natural failures without weakening SSH policy.
- **NOT TESTED in these SFTP runs:** active-desktop focus, new/changed-key prompts,
  nondefault ports and precedence, extra endpoint/IPv6/SSH-profile variations. Existing
  bounded focus and URI mocks are not a claim of native SFTP coverage for these cases.
- **Separate gates:** TigerVNC/RDP and Step 1.5d are not authorized by this record.

For the correction, inspect the existing maintainer fixture before running it. Use
the same corrected implementation on X11 then Wayland; record its eventual SHA or
HEAD plus reviewed diff. Example desktop numbers below must have fresh logical slots.
The first URI is the demonstrated endpoint; the second intentionally uses a reserved
unresolvable name. Confirm each plan interactively; do not reuse occupied slots.

```bash
TEST_DESKTOP=10 SFTP_TEST_URI='sftp://joe@nuthuvia.brendler/home/joe/' ./joetoo-kwin -vv -o -f task_step1.5/step1.5c5a-native.conf
TEST_DESKTOP=11 SFTP_TEST_URI='sftp://nonexistent.invalid/home/joe/' ./joetoo-kwin -vv -o -f task_step1.5/step1.5c5a-native.conf
# End of commands

```

Record resolution/TCP advisory messages, Dolphin listing/error, exact managed UUIDs,
placement/stack/focus and overall layout count independently. Do not treat a TCP-open
advisory as authentication success. The failed Dolphin view is intentionally retained
as a mission reminder and an opportunity to correct/retry, with config updated separately.
