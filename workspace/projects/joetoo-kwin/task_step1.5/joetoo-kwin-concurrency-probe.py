#!/usr/bin/env python3
# Copyright 2026 Joseph Brendler and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
# Native, maintainer-run PTY preflight contention probe. Never sends an affirmative answer.
import argparse
import errno
import os
from pathlib import Path
import pty
import select
import signal
import tempfile
import time

PROMPT = b"Do you want to continue?"
LAUNCH = (b"Launching desktop [", b"Armed managed launch [")


def spawn(project, config):
    pid, fd = pty.fork()  # Child gets a controlling TTY; yn_prompt reads /dev/tty.
    if pid == 0:
        os.chdir(project)
        os.execv(str(project / "joetoo-kwin"),
                 [str(project / "joetoo-kwin"), "-o", "-f", str(config)])
    return {"pid": pid, "fd": fd, "data": bytearray(), "exit": None}


def collect(p, timeout=0.15):
    if p["fd"] is not None and select.select([p["fd"]], [], [], timeout)[0]:
        try:
            buf = os.read(p["fd"], 65536)
        except OSError as e:
            if e.errno != errno.EIO:
                raise
            buf = b""
        if buf:
            p["data"].extend(buf)
        else:
            os.close(p["fd"])
            p["fd"] = None
    if p["exit"] is None:
        done, status = os.waitpid(p["pid"], os.WNOHANG)
        if done:
            p["exit"] = os.waitstatus_to_exitcode(status)


def await_prompt_or_exit(p, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        collect(p)
        if PROMPT in p["data"]:
            return "PROMPT"
        if p["exit"] is not None:
            return "EXIT"
    return "TIMEOUT"


def cancel_and_reap(p):
    if p["exit"] is None and p["fd"] is not None:
        try:
            os.write(p["fd"], b"n\n")  # Never sends 'y'.
        except OSError as e:
            if e.errno not in (errno.EIO, errno.EBADF):
                raise
    deadline = time.monotonic() + 3
    while p["exit"] is None and time.monotonic() < deadline:
        collect(p)
    if p["exit"] is None:
        os.killpg(p["pid"], signal.SIGTERM)  # Only our own PTY session.
        deadline = time.monotonic() + 2
        while p["exit"] is None and time.monotonic() < deadline:
            collect(p)
    if p["fd"] is not None:
        os.close(p["fd"])


def main():
    parser = argparse.ArgumentParser(description="Probe whole--o contention without launching windows")
    parser.add_argument("--project", default=".")
    parser.add_argument("--desktop-a", type=int, required=True)
    parser.add_argument("--desktop-b", type=int, required=True)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--timeout", type=float, default=12)
    a = parser.parse_args()
    project = Path(a.project).resolve()
    if a.desktop_a == a.desktop_b or min(a.desktop_a, a.desktop_b) < 1:
        parser.error("choose distinct, existing virtual desktops without occupied managed slots")
    if not (1 <= a.width <= 32768 and 1 <= a.height <= 32768):
        parser.error("invalid display dimensions")
    if not (project / "joetoo-kwin").is_file():
        parser.error("--project does not contain joetoo-kwin")

    logdir = Path(tempfile.mkdtemp(prefix="joetoo-kwin-concurrency-"))
    for label, desktop in (("A", a.desktop_a), ("B", a.desktop_b)):
        (logdir / f"{label}.conf").write_text(
            f'screen_width={a.width}\nscreen_height={a.height}\n'
            f'desktop_session_list=("{desktop}|konsole|local|bash")\n')
    print(f"Test transcripts/configs: {logdir}", flush=True)
    print("No 'yes' responses; no application windows should be created.", flush=True)
    processes = []
    try:
        first = spawn(project, logdir / "A.conf")
        processes.append(("A", first))
        state_a = await_prompt_or_exit(first, a.timeout)
        if state_a != "PROMPT":
            print(f"INCONCLUSIVE: A returned {state_a} instead of confirmation.")
            return 2
        print("A awaits confirmation; starting B now.", flush=True)
        second = spawn(project, logdir / "B.conf")
        processes.append(("B", second))
        state_b = await_prompt_or_exit(second, a.timeout)
        collect(first, 0)
        if first["exit"] is not None:
            print("INCONCLUSIVE: A exited unexpectedly during contention.")
            return 2
        if state_b == "PROMPT":
            print("FAIL (for pre-confirmation lock policy): B also reached confirmation.")
            return 1
        if state_b != "EXIT":
            print(f"INCONCLUSIVE: B returned {state_b}.")
            return 2
        output = bytes(second["data"]).lower()
        if not any(word in output for word in (b"busy", b"lock", b"another launch", b"concurrent")):
            print("INCONCLUSIVE: B exited without an identifiable Busy/lock refusal.")
            return 2
        print("PASS: B refused the competing run before confirmation.")
        return 0
    finally:
        for _, p in reversed(processes):
            cancel_and_reap(p)
        for label, p in processes:
            (logdir / f"{label}.log").write_bytes(p["data"])
            if any(text in p["data"] for text in LAUNCH):
                print(f"WARNING: {label} includes a launch indicator; inspect its log.")
        print(f"Logs preserved at {logdir}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
