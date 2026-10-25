# joetoo KWin — single interactive Bash `--rcfile` SSH experiment

**Scope:** Step 0.6 (process relationship and cleanup). Do not replace the proven
`joetoo-kwin-broker.py` or `joetoo-kwin-resident.js`. This POC only replaces
the **SSH test driver**, and adds a separate Bash startup file.

## Why this experiment

The previous SSH driver launched `konsole -e bash -ic '...; exec bash -i'`.
That runs one shell for the connection and replaces it with a second one after
SSH exits. Here, `konsole -e ... bash --rcfile FILE -i` starts **one interactive
Bash**. Its rcfile sources `~/.bashrc`, runs the familiar `ssh_wrapper` as a
foreground shell function, then lets the original Bash reach its prompt.

No sensitive Konsole D-Bus API, `runCommand`, `sendText`, `tmux`, or second shell.

## Preconditions

- Use the proven extended Python broker (`joetoo-kwin-broker.py`) and resident
  JavaScript from the successful **launch** prototype.
- Start the broker as your graphical user; load the KWin JavaScript with your
  existing `joetoo-kwin_start_test_driver.sh` if needed. **This driver does not
  initialize the bridge.**
- Have `konsole`, `qdbus6`, `net-analyzer/netcat` (`nc -z -w 2`), and an
  interactive `~/.bashrc` that defines the existing `ssh_wrapper` function.
- Restore/keep `EnableSecuritySensitiveDBusAPI=false` in `konsolerc`. No
  Konsole command injection is needed. Manually disable any previously enabled
  in-memory permission in older running Konsole instances.

## Tests

Keep both new files in the same directory:

    chmod +x joetoo-kwin_ssh_rcfile_test_driver.sh
    ./joetoo-kwin_ssh_rcfile_test_driver.sh nuthuvia

Expected: a new Konsole at desktop 3, `(100,80) 850x700`, displays its target
and **local Bash PID**, and connects using `ssh_wrapper`. Run `exit` on the
remote host. The **same** local Bash PID should remain and its normal prompt
should appear, preceded by a connection-ended message.

Test a nonexistent DNS name (such as the example `nubogus`) or a known closed
port without creating SSH:

    ./joetoo-kwin_ssh_rcfile_test_driver.sh nubogus
    ./joetoo-kwin_ssh_rcfile_test_driver.sh nuthuvia 65000

Expected: Konsole still appears in its slot, displays the intended target and
"SSH unavailable", and retains its original local Bash at a prompt.

### Important: exact-PID process cleanup test

**While nuthuvia SSH is still connected**, note the file path printed by the
launch driver, then from the control Konsole A:

    pidfile='/run/user/1000/joetoo-kwin-ssh.XXXXXXXX/bash.pid'  # REPLACE with actual path
    shell_pid=$(cat "$pidfile")
    echo "Local Bash PID: $shell_pid"
    pgrep -a -P "$shell_pid" ssh

Record the exact SSH PID from that output, e.g.:

    ssh_pid=$(pgrep -P "$shell_pid" -x ssh | head -n 1)
    ps -o pid,ppid,pgid,sid,stat,args -p "$shell_pid","$ssh_pid"

Now **close only that new Konsole window** while SSH is still active.
Verify the **same exact PIDs** have gone away:

    ps -o pid,ppid,pgid,sid,stat,args -p "$shell_pid","$ssh_pid"

No output apart from the header means those PIDs no longer exist. Check for
possible PID reuse if results are surprising; `ps` status `Z` means a process
is a zombie pending reaping. **Do not broadly kill all SSH processes.**

Repeat the above on gmki91 (X11) and q552u01 (Wayland). A successful KWin
`OK launch:` result only proves that window placement succeeded; the terminal
itself reports SSH success/failure.

## Notes

- During SSH, Bash is waiting for the **foreground** `ssh_wrapper` function,
  which calls `command ssh` as an external child. This is the relationship to
  inspect; it does not by itself prove closing Konsole will kill SSH.
- `bash --rcfile` reads this file **instead of** `~/.bashrc`, hence the explicit
  `source "$HOME/.bashrc"` at the top. It executes the startup code and then
  continues as the **same interactive Bash**.
- The Bash PID file is placed under a private directory made by `mktemp -d`
  in `XDG_RUNTIME_DIR` (or an ordinary temp directory if that variable is
  absent). It is for test observation only; delete it after testing.
- A TCP port check is not authentication. We keep `ssh_wrapper` responsible for
  the actual connection and exit status. Offline and ambiguous failures remain
  visible without removing the planned window.
- `--tabs-from-file` controls **tabs inside a Konsole window**, not separate
  desktop-positioned windows. It's worth retaining as a future per-window
  multi-tab launch mode, but it does not simplify the one-window-one-slot test.
