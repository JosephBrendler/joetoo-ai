# Joetoo KWin — Step 0.2–0.5 SSH/TCP integration test (Option B)

This is **the netcat version**, replacing the earlier `swr`-based SSH test driver.
It exercises `ssh_wrapper` directly after a short TCP port probe using `nc -z -w 2`.
There is **no ICMP prerequisite**, no `pur` and no `swr` retry loop.

## Contents

- `joetoo-kwin_ssh_test_driver.sh` — one-shot Bash test driver. It **does not** initialize KWin or the D-Bus broker.

**Do not overwrite your working** `joetoo-kwin-broker.py`, `joetoo-kwin-resident.js`, `joetoo-kwin_start_test_driver.sh`, or `joetoo-kwin_stop_test_driver.sh`. Those are unchanged.

## Prerequisites: launch bridge already running

On gmki91 (KWin X11), and subsequently q552u01 (KWin Wayland):

1. Ensure the extended Python broker from the successful launch test is running **as the desktop user** (`joetoo-kwin-broker.py`, not the earlier move-only broker).
2. If not already loaded, start the resident JavaScript using **your existing** `./joetoo-kwin_start_test_driver.sh` in its directory. The launch test driver is NOT a replacement for this initialization step.
3. Verify that a *fresh* interactive Bash has your function:

       bash -ic 'type -t ssh_wrapper'

   Expected: `function`. If missing, fix how `~/.bashrc` loads your joetoo functions before testing.
4. Check that `nc` points to the variant you intend (you restored `net-analyzer/netcat`):

       command -v nc
       nc -z -w 2 nuthuvia 22; echo "nc status: $?"

5. Copy the driver into `~/scratch/joetoo-kwin-launch-poc/` (or run it in this extracted folder; it only needs the resident services), and make it executable:

       chmod +x joetoo-kwin_ssh_test_driver.sh

## Positive test: reachable SSH service

    ./joetoo-kwin_ssh_test_driver.sh nuthuvia

Expected:

- A new Konsole appears on desktop 3, at `(100,80)`, size `850x700`.
- **Inside that new Konsole**, `nc -z -w 2 nuthuvia 22` tests TCP port 22 and the real `ssh_wrapper -p 22 nuthuvia` is invoked only when the probe succeeds.
- After SSH logout or failure, Konsole **remains open** at a local interactive Bash prompt with a printed session status and retry command.
- In the original Konsole, an `OK launch:` response means **window placement succeeded**, not that SSH authentication or remote login succeeded.

## Negative test: closed SSH port

    ./joetoo-kwin_ssh_test_driver.sh nuthuvia 65000

Use a genuinely closed test port (substitute a different port as needed). The new window should still be created and placed. It should print `SSH unavailable` and skip `ssh_wrapper`, then retain an interactive Bash prompt and manual retry command. This also works for an offline host without invoking `pur`'s lengthy retry loop.

## Regression tests

Run your existing `./joetoo-kwin move 1 200 80 850 700` from a Konsole with focus. Repeat both SSH tests on q552u01 under Wayland; the window-placement and SSH connection outcomes are independent.

## Scope and limitations

- Existing bridge: unchanged. This is a CLI and terminal-behavior integration test, **not** the final configuration-driven open-windows module.
- The test driver assumes `ssh_wrapper` is a function loaded by `bash -ic` from the user's interactive shell startup. It tests that assumption before launching a window.
- A successful TCP connect does not prove the remote server speaks SSH or that SSH authentication will succeed. `ssh_wrapper` handles SSH itself and its exit status is displayed.
- A single unsuccessful short TCP probe is not conclusive proof that a host is offline. Later policy can provide a user-selected longer timeout or manual retry.
- Launch placement is single-flight: don't launch two copies of this driver simultaneously against the current broker.
- As tested with `net-analyzer/netcat`, `nc -z -w 2 HOST PORT` performs a TCP port probe. This driver does not depend on `jping`'s other output parsing or the divergent diagnostic flags of other netcat implementations.
- The Bash command inside Konsole ends with `exec bash -i` to keep the terminal usable. It creates a *new* local interactive shell after the SSH attempt; this is intentional for the prototype.
