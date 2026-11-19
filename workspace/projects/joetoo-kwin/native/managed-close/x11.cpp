// Copyright 2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Disposable helper: no application signals, XKillClient or DestroyWindow.
// A private credentialed socket gates one WM_DELETE_WINDOW under a short server
// grab. Every reply wait and the GO wait share one monotonic absolute deadline.
#include "channel.h"
#include <xcb/xcb.h>
#include <xcb/xcbext.h>
#include <poll.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <signal.h>
#include <chrono>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <time.h>
#include <algorithm>
#include <cerrno>
#include <limits>
#include <string>

using Clock = std::chrono::steady_clock;
static Clock::time_point deadline;
static int remaining()
{
    return int(std::chrono::duration_cast<std::chrono::milliseconds>(deadline - Clock::now()).count());
}
static void *reply(xcb_connection_t *c, unsigned int sequence)
{
    while (remaining() > 0 && !xcb_connection_has_error(c)) {
        void *r = nullptr;
        xcb_generic_error_t *e = nullptr;
        if (xcb_poll_for_reply(c, sequence, &r, &e)) {
            if (e) { free(e); free(r); return nullptr; }
            return r;
        }
        pollfd fd{xcb_get_file_descriptor(c), POLLIN, 0};
        if (poll(&fd, 1, std::max(0, remaining())) < 0) return nullptr;
    }
    return nullptr;
}
static bool sync(xcb_connection_t *c)
{
    auto cookie = xcb_get_input_focus(c);
    xcb_flush(c);
    auto *r = reply(c, cookie.sequence);
    free(r);
    return r != nullptr;
}
static uint32_t number(const char *s)
{
    if (!s || !*s || *s == '-') return 0;
    char *end = nullptr;
    auto n = strtoull(s, &end, 10);
    return end && !*end && n <= UINT32_MAX ? uint32_t(n) : 0;
}
int main(int argc, char **argv)
{
    // Parent death disconnects this connection even if KWin crashes mid-grab.
    const auto parent = getppid();
    if (prctl(PR_SET_PDEATHSIG, SIGKILL) || prctl(PR_SET_DUMPABLE, 0) || getppid() != parent || argc != 7) return 2;
    const uint32_t guard = number(argv[1]), atom = number(argv[2]), xid = number(argv[3]);
    const auto budget = number(argv[4]);
    uint32_t nonce[4]{};
    if (!guard || !atom || !xid || budget < 10 || budget > 500) return 2;
    // Independent monotonic watchdog also bounds blocking setup/library calls.
    // It terminates only this helper and releases any grab by disconnection.
    struct sigaction alarmAction{}; alarmAction.sa_handler = SIG_DFL;
    sigemptyset(&alarmAction.sa_mask);
    sigset_t alarmMask; sigemptyset(&alarmMask); sigaddset(&alarmMask, SIGALRM);
    if (sigaction(SIGALRM, &alarmAction, nullptr) || sigprocmask(SIG_UNBLOCK, &alarmMask, nullptr)) return 2;
    timer_t watchdog;
    sigevent notification{}; notification.sigev_notify = SIGEV_SIGNAL; notification.sigev_signo = SIGALRM;
    if (timer_create(CLOCK_MONOTONIC, &notification, &watchdog)) return 2;
    itimerspec timer{};
    timer.it_value.tv_sec = (budget + 10) / 1000;
    timer.it_value.tv_nsec = ((budget + 10) % 1000) * 1000000;
    if (timer_settime(watchdog, 0, &timer, nullptr)) return 2;
    char *expiryEnd = nullptr;
    errno = 0;
    const auto expiryMs = strtoll(argv[5], &expiryEnd, 10);
    const auto nowMs = std::chrono::duration_cast<std::chrono::milliseconds>(Clock::now().time_since_epoch()).count();
    if (errno || !expiryEnd || *expiryEnd || expiryMs <= 0 || expiryMs > nowMs + 120000) return 2;
    deadline = std::min(Clock::now() + std::chrono::milliseconds(budget),
                        Clock::time_point(std::chrono::milliseconds(expiryMs)));
    if (remaining() <= 0) return 4;
    // The socketpair is inherited, not a named endpoint or a reopenable pipe.
    // SCM_CREDENTIALS authenticates the actual sender after fork/exec.
    const int channel = int(number(argv[6]));
    int type = 0; socklen_t typeLength = sizeof(type);
    if (channel < 0 || getsockopt(channel, SOL_SOCKET, SO_TYPE, &type, &typeLength) || type != SOCK_SEQPACKET) return 2;
    int pass = 1;
    if (setsockopt(channel, SOL_SOCKET, SO_PASSCRED, &pass, sizeof(pass))) return 2;
    if (write(channel, "ready", 5) != 5) return 4;
    pollfd authorization{channel, POLLIN, 0};
    if (poll(&authorization, 1, std::max(0, remaining())) != 1 || !receiveOwnedPacket(channel, parent, nonce, sizeof(nonce))) return 4;
#ifdef JOETOO_CLOSE_TEST_FD
    // Offline ABI tests supply a socketpair, never DISPLAY or an X server.
    auto *c = xcb_connect_to_fd(int(number(getenv("JOETOO_CLOSE_TEST_FD"))), nullptr);
#else
    auto *c = xcb_connect(nullptr, nullptr); // Compositor-owned DISPLAY authorization.
#endif
    if (!c || xcb_connection_has_error(c)) { if (c) xcb_disconnect(c); return 3; }
    // Disconnect is the unconditional ungrab backstop, including every error.
    struct Owner { xcb_connection_t *c; ~Owner() { xcb_disconnect(c); } } owner{c};
    auto protocolsCookie = xcb_intern_atom(c, false, 12, "WM_PROTOCOLS");
    auto deleteCookie = xcb_intern_atom(c, false, 16, "WM_DELETE_WINDOW");
    xcb_flush(c);
    auto *p = static_cast<xcb_intern_atom_reply_t *>(reply(c, protocolsCookie.sequence));
    auto *d = static_cast<xcb_intern_atom_reply_t *>(reply(c, deleteCookie.sequence));
    if (!p || !d) { free(p); free(d); return 3; }
    const auto protocols = p->atom, remove = d->atom;
    free(p); free(d);
    xcb_grab_server(c);
    // Fence event goes to the creating KWin connection, through its ordinary
    // FIFO native-event processing, after pre-grab destruction notifications.
    xcb_client_message_event_t fence{};
    fence.response_type = XCB_CLIENT_MESSAGE; fence.format = 32;
    fence.window = guard; fence.type = atom;
    memcpy(fence.data.data32, nonce, sizeof(nonce));
    xcb_send_event(c, false, guard, XCB_EVENT_MASK_NO_EVENT, reinterpret_cast<char *>(&fence));
    xcb_flush(c);
    if (!sync(c)) return 3; // Server has processed the grab and marker.
    pollfd fd{channel, POLLIN, 0};
    char go[3]{};
    if (remaining() <= 0 || poll(&fd, 1, std::max(0, remaining())) != 1 || !receiveOwnedPacket(channel, parent, go, 3) || memcmp(go, "GO\n", 3)) return 4;
    // Only the post-fence original UUID/object check in KWin can send GO.
    auto cookie = xcb_get_property(c, false, xid, protocols, XCB_ATOM_ATOM, 0, 1024);
    xcb_flush(c);
    auto *property = static_cast<xcb_get_property_reply_t *>(reply(c, cookie.sequence));
    if (!property) return 5;
    bool supports = false;
    if (property->type == XCB_ATOM_ATOM && property->format == 32 && !property->bytes_after) {
        auto *values = static_cast<uint32_t *>(xcb_get_property_value(property));
        for (int i = 0; i < xcb_get_property_value_length(property) / 4; ++i) supports |= values[i] == remove;
    }
    free(property);
    if (!supports || remaining() <= 0) return 5;
    xcb_client_message_event_t event{};
    event.response_type = XCB_CLIENT_MESSAGE; event.format = 32;
    event.window = xid; event.type = protocols;
    event.data.data32[0] = remove; event.data.data32[1] = XCB_CURRENT_TIME;
    // Checked request, followed by bounded reply processing, before release.
    auto send = xcb_send_event_checked(c, false, xid, XCB_EVENT_MASK_NO_EVENT, reinterpret_cast<char *>(&event));
    xcb_flush(c);
    if (!sync(c)) return 6;
    auto *error = xcb_request_check(c, send); // Sync above makes this nonblocking.
    if (error) { free(error); return 6; }
    xcb_ungrab_server(c); xcb_flush(c);
    if (!sync(c)) return 6;
    puts("dispatched");
    return 0;
}
