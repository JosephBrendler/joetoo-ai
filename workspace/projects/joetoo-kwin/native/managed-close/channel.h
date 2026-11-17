// Copyright 2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <sys/socket.h>
#include <unistd.h>
#include <cstring>

// Per-message kernel credentials, not SO_PEERCRED's pre-fork socket creator.
// Unix sockets cannot be reopened as byte streams through /proc/PID/fd, unlike
// pipes. No secret is placed in argv/environment or the QProcess stdout pipe.
inline bool receiveOwnedPacket(int fd, pid_t expectedPid, void *buffer, size_t size)
{
    char control[CMSG_SPACE(sizeof(ucred))]{};
    iovec io{buffer, size};
    msghdr msg{};
    msg.msg_iov = &io; msg.msg_iovlen = 1;
    msg.msg_control = control; msg.msg_controllen = sizeof(control);
    const auto count = recvmsg(fd, &msg, MSG_DONTWAIT);
    if (count != ssize_t(size) || msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) return false;
    for (auto *header = CMSG_FIRSTHDR(&msg); header; header = CMSG_NXTHDR(&msg, header)) {
        if (header->cmsg_level == SOL_SOCKET && header->cmsg_type == SCM_CREDENTIALS &&
            header->cmsg_len == CMSG_LEN(sizeof(ucred))) {
            ucred peer{}; memcpy(&peer, CMSG_DATA(header), sizeof(peer));
            return peer.pid == expectedPid && peer.uid == geteuid();
        }
    }
    return false;
}
