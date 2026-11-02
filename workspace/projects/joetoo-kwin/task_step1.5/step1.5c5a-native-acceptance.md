# Step 1.5c.5a native acceptance

Provenance: **maintainer-reported native results**, not Codex-operated tests.
Published advisory implementation baseline: `b8120f7c9aad608e26b5c147561a5eee5756a8e9`,
branch `task/joetoo-kwin-step1.5c5-remote-access`. Native logs/screenshots were
supplied in the maintainer review conversation; this summary does not invent
additional artifact paths. Earlier base SFTP results below were recorded at
`98e3668`; the subsequent advisory evidence is distinguished separately. The final
debug-label cleanup is uncommitted; **maintainer acceptance/closure is still to be decided**.

| Earlier base SFTP evidence at 98e3668 | gmki91 / KWin X11 | q552u01 / KWin Wayland |
| --- | --- | --- |
| Python regressions | PASS: 301 tests, maintainer run | PASS: 301 tests, maintainer run |
| JavaScript regressions | PASS: 50 tests, maintainer run | PASS: 50 tests, maintainer run |
| Local SFTP-worker capability preflight | PASS for tested launch | PASS for tested installation |
| Managed SFTP Dolphin and local underlay | PASS: independent registration, placement and stacking | PASS: independent registration, placement and stacking |
| Remote nuthuvia browsing and hostname file | PASS: remote file opened; earlier interactive feasibility used Kate | PASS: remote /etc/hostname opened in KWrite, content nuthuvia |
| Active-desktop SFTP focus acquisition | NOT TESTED: desktop 2 launch while 1 active | NOT TESTED: desktop 2 launch while 1 active |
| Inactive-desktop focus suppression | PASS for reported layout | PASS for reported layout |
| Post-advisory evidence at b8120f7 | Negative advisory reported; positive tcp=open still PENDING | Positive and negative advisory PASS; details below |

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

## Post-advisory native evidence — published b8120f7

**gmki91 / X11:** the maintainer reports the negative-advisory check and continued
managed Dolphin launches despite remote failure. Preserve this separately from the
earlier positive browsing and detailed desktop-4 negative test above. No documented
post-advisory X11 `tcp=open` transcript was found in the current task records;
that positive observation remains **PENDING**, not inferred from earlier browsing.

**q552u01 / Wayland negative destination — PASS for advisory/window behavior:**
maintainer-reported `resolution=failed`, `tcp=skipped`, with the correct qualified
console warning. Both managed windows launched successfully; Dolphin independently
reported hostname-resolution failure. This is an expected remote mission failure,
not a failure of the managed-window launch. No additional IDs or desktop numbers
are inferred for this negative run.

**q552u01 / Wayland positive destination — PASS:** maintainer-reported
`resolution=resolved`, `tcp=open`, `port=22`. Managed SFTP Dolphin `win-003` and
local underlay `win-004` were independently placed on desktop 4; stacking and
placement verified and the console reported **2/2 completed**. The maintainer
visually confirmed successful remote browsing of `nuthuvia.brendler`. TCP-open is
only an advisory result; browsing success is a separate human observation, not
launcher telemetry. UUIDs, focus outcomes and timings were not supplied for this
new run and are not invented here.

## Remaining acceptance checklist

- **PENDING native evidence:** post-advisory X11 positive `resolution=resolved`,
  `tcp=open` using the reviewed published implementation and fresh logical slots.
  Earlier X11 successful browsing is retained but does not establish that result.
- **Completed:** Wayland positive/negative advisory and retained launch behavior;
  X11 negative advisory as reported. No mandatory repeat of these checks is implied.
- **Headless covered, NOT TESTED natively:** advisory disable, absent resolver/probe
  and timeouts. Native tool manipulation is optional, not a requirement to alter
  system configuration or weaken SSH policy.
- **NOT TESTED in these SFTP runs:** active-desktop focus, new/changed-key prompts,
  nondefault ports and precedence, extra endpoint/IPv6/SSH-profile variations.
  Existing focus and URI mocks do not establish native coverage for these cases.
- **Decision pending:** maintainer reviews this cleanup and decides Step 1.5c.5a
  acceptance/closure. TigerVNC/RDP and Step 1.5d remain separately gated.

For the remaining X11 positive observation, inspect the existing fixture and choose
an unused intended desktop/slot. Record HEAD plus any reviewed diff, advisory JSON,
Dolphin browsing and managed placement/stack/focus separately.

```bash
TEST_DESKTOP=10 SFTP_TEST_URI='sftp://joe@nuthuvia.brendler/home/joe/' ./joetoo-kwin -vv -o -f task_step1.5/step1.5c5a-native.conf
# End of commands

```

The failed Dolphin view remains intentional: it preserves mission purpose and the
opportunity for immediate correction/retry, with configuration updated separately.
