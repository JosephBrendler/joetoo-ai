// Copyright 2026 Joseph Brendler
// SPDX-License-Identifier: GPL-3.0-or-later
// Exact-version KWin effect. No rendering, shortcuts, placement or app supervisor.
#include "channel.h"
#include <effect/effect.h>
#include <effect/effecthandler.h>
#include <effect/effectwindow.h>
#include <window.h>
#include <x11eventfilter.h>
#include <QDBusConnection>
#include <QCoreApplication>
#include <QFileInfo>
#include <QDBusConnectionInterface>
#include <QDBusContext>
#include <QDBusServiceWatcher>
#include <QDBusPendingCallWatcher>
#include <QDBusPendingReply>
#include <QElapsedTimer>
#include <QJsonDocument>
#include <QJsonObject>
#include <QProcess>
#include <QPointer>
#include <QTimer>
#include <QRandomGenerator>
#include <QSocketNotifier>
#include <fcntl.h>
#include <xcb/xcb.h>
#include <xcb/xcbext.h>
#include <memory>
#include <time.h>

namespace KWin {
static constexpr auto service = "org.joetoo.KWinCloseNative";
static constexpr auto path = "/org/joetoo/KWinCloseNative";
static constexpr auto broker = "org.joetoo.KWinBridge";
static QString json(const QJsonObject &object) { return QString::fromUtf8(QJsonDocument(object).toJson(QJsonDocument::Compact)); }

class ManagedClose : public Effect, protected QDBusContext, public X11EventFilter
{
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "org.joetoo.KWinCloseNative")
public:
    ManagedClose() : X11EventFilter(XCB_CLIENT_MESSAGE), m_bus(QDBusConnection::sessionBus())
    {
        m_clock.start();
        auto *watch = new QDBusServiceWatcher(QString::fromLatin1(broker), m_bus,
            QDBusServiceWatcher::WatchForOwnerChange, this);
        connect(watch, &QDBusServiceWatcher::serviceOwnerChanged, this,
            [this](const QString &, const QString &, const QString &owner) { invalidate(); m_ownerSeen = true; m_owner = owner; });
        auto pending = m_bus.interface()->asyncCall("GetNameOwner", QString::fromLatin1(broker));
        auto *ownerCall = new QDBusPendingCallWatcher(pending, this);
        connect(ownerCall, &QDBusPendingCallWatcher::finished, this, [this, ownerCall] {
            QDBusPendingReply<QString> answer = *ownerCall;
            // A newer owner-change event must never be overwritten by an old reply.
            if (!m_ownerSeen && !answer.isError()) m_owner = answer.value();
            ownerCall->deleteLater();
        });
        connect(effects, &EffectsHandler::windowClosed, this, [this](EffectWindow *w) {
            if (w->internalId() == m_uuid && m_state != "idle") {
                m_gone = true;
                if (m_state == "dispatching") m_state = "closed";
            }
        });
        connect(effects, &EffectsHandler::xcbConnectionChanged, this, [this] { invalidate(); m_guard = 0; m_atom = 0; m_atomSequence = 0; setupGuard(); });
        m_timer.setInterval(20);
        connect(&m_timer, &QTimer::timeout, this, [this] {
            if (m_atomSequence && effects->xcbConnection()) {
                void *raw = nullptr; xcb_generic_error_t *error = nullptr;
                if (xcb_poll_for_reply(effects->xcbConnection(), m_atomSequence, &raw, &error)) {
                    if (!error && raw) m_atom = static_cast<xcb_intern_atom_reply_t *>(raw)->atom;
                    free(raw); free(error); m_atomSequence = 0;
                } else if (m_clock.elapsed() >= m_atomDeadline) {
                    xcb_discard_reply(effects->xcbConnection(), m_atomSequence); m_atomSequence = 0;
                }
            }
            if (m_deadline && m_clock.elapsed() >= m_deadline && m_process) {
                // Kill only our disposable helper; never an application.
                m_process->kill(); m_state = "helper_timeout";
            }
            if (!m_atomSequence && !m_process) m_timer.stop();
        });
        m_timer.start();
        setupGuard();
        if (!m_bus.registerService(QString::fromLatin1(service))) return;
        m_registered = m_bus.registerObject(QString::fromLatin1(path), this,
            QDBusConnection::ExportScriptableSlots);
        if (!m_registered) m_bus.unregisterService(QString::fromLatin1(service));
    }
    ~ManagedClose() override
    {
        invalidate();
        if (m_process) {
            auto *process = m_process.data();
            process->kill();
            if (!process->waitForFinished(500)) {
                // Do not block compositor unload indefinitely. Qt owns this
                // reap-only object after our receiver/lambdas are disconnected.
                process->setParent(nullptr);
                QObject::connect(process, SIGNAL(finished(int,QProcess::ExitStatus)), process, SLOT(deleteLater()));
            }
        }
        if (m_atomSequence && effects->xcbConnection()) xcb_discard_reply(effects->xcbConnection(), m_atomSequence);
        if (m_guard && effects->xcbConnection()) { xcb_destroy_window(effects->xcbConnection(), m_guard); xcb_flush(effects->xcbConnection()); }
        if (m_registered) { m_bus.unregisterObject(QString::fromLatin1(path)); m_bus.unregisterService(QString::fromLatin1(service)); }
    }
    bool isActive() const override { return false; }
    bool event(xcb_generic_event_t *event) override
    {
        auto *e = reinterpret_cast<xcb_client_message_event_t *>(event);
        if (e->window != m_guard || e->type != m_atom || e->format != 32) return false;
        if (!m_process || m_state != "fencing" || m_clock.elapsed() >= m_deadline) return true;
        for (int i = 0; i < 4; ++i) if (e->data.data32[i] != m_nonce[i]) return true;
        // No server round trips here: the helper holds the server. Normal FIFO
        // processing has already applied preceding Destroy/Unmap notifications.
        auto *w = effects->findWindow(m_uuid);
        if (w != m_window || !valid(w) || !w->isX11Client() || w->windowId() != m_xid || w->pid() != m_pid ||
            w->window()->resourceClass() != m_class || !w->window()->isCloseable()) {
            m_state = "identity_lost"; m_process->kill(); return true;
        }
        m_state = "dispatching";
        if (m_channel < 0 || write(m_channel, "GO\n", 3) != 3) { m_state = "helper_channel_lost"; m_process->kill(); }
        return true;
    }
public Q_SLOTS:
    Q_SCRIPTABLE QString Terminal(int pid)
    {
        if (!authorized() || pid <= 0) return json({{"state", "unknown"}});
        EffectWindow *match = nullptr;
        for (auto *w : effects->stackingOrder()) {
            if (valid(w) && w->pid() == pid) {
                if (match) return json({{"state", "unknown"}});
                match = w;
            }
        }
        return match ? json({{"state", "identified"}, {"uuid", match->internalId().toString(QUuid::WithoutBraces)}})
                     : json({{"state", "unknown"}});
    }
    Q_SCRIPTABLE QString Inspect(const QString &uuid)
    {
        if (!authorized()) return json({{"state", "denied"}});
        auto *w = effects->findWindow(QUuid(uuid));
        if (!w || w->isDeleted()) return json({{"state", "missing"}, {"uuid", uuid}});
        if (!valid(w) || w->window()->resourceClass().toUtf8().size() > 256) return json({{"state", "unsupported"}});
        // Authenticated native evidence, never caller-selected PID/class adoption.
        return json({{"state", "present"}, {"uuid", w->internalId().toString(QUuid::WithoutBraces)},
            {"pid", int(w->pid())}, {"class", w->window()->resourceClass()},
            {"backend", w->isX11Client() ? "x11" : "wayland"},
            {"xid", QString::number(w->windowId())}, {"closeable", w->window()->isCloseable()}});
    }
    Q_SCRIPTABLE QString Close(const QString &token, const QString &uuid, int pid, const QString &appClass, int grabMs, const QString &expiresMs)
    {
        if (!authorized()) return json({{"state", "denied"}});
        const auto reject = [&](const QString &reason) {
            return json({{"state", reason}, {"token", token.left(32)},
                {"uuid", QUuid(uuid).toString(QUuid::WithoutBraces)},
                {"helper_reaped", !m_process}, {"gone", false}});
        };
        bool parsed = false;
        const auto expiry = expiresMs.toLongLong(&parsed);
        timespec now{}; clock_gettime(CLOCK_MONOTONIC, &now);
        const qint64 monotonicMs = qint64(now.tv_sec) * 1000 + now.tv_nsec / 1000000;
        if (!parsed || expiry <= monotonicMs || expiry - monotonicMs > 120000)
            return reject(QStringLiteral("expired"));
        grabMs = qMin(grabMs, int(expiry - monotonicMs));
        if (m_process || grabMs < 10 || grabMs > 500 || token.size() != 32 || appClass.toUtf8().size() > 256 || m_used.contains(token))
            return reject(QStringLiteral("busy_or_replay"));
        auto *w = effects->findWindow(QUuid(uuid));
        if (!valid(w) || w->pid() != pid || w->window()->resourceClass() != appClass || !w->window()->isCloseable())
            return reject(QStringLiteral("identity_or_capability_rejected"));
        m_used.append(token); if (m_used.size() > 128) m_used.removeFirst();
        m_token = token; m_uuid = w->internalId(); m_window = w; m_xid = w->windowId(); m_pid = pid;
        m_class = appClass; m_gone = false; m_state = "dispatching";
        // Diagnostics belong to this specific accepted close token, never a prior attempt.
        m_helperExitKnown = false; m_helperExitCode = 0; m_helperExitStatus.clear(); m_helperReceiptOk = false;
        if (w->isWaylandClient() && !w->isX11Client()) {
            // Native Wayland only. X11 closeWindow() is deliberately unreachable.
            w->closeWindow();
            return status();
        }
        if (!w->isX11Client() || !m_guard || !m_atom) { m_state = "unsupported"; return status(); }
        m_state = "fencing"; m_deadline = m_clock.elapsed() + grabMs + 500;
        auto *process = new QProcess(this); m_process = process;
        QStringList args{QString::number(m_guard), QString::number(m_atom), QString::number(m_xid), QString::number(grabMs)};
        for (auto &nonce : m_nonce) nonce = QRandomGenerator::system()->generate();
        int pair[2]{};
        if (socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0, pair)) {
            m_state = "helper_channel_unavailable"; m_process = nullptr; process->deleteLater(); return status();
        }
        m_channel = pair[0]; m_childChannel = pair[1];
        int pass = 1;
        if (setsockopt(m_channel, SOL_SOCKET, SO_PASSCRED, &pass, sizeof(pass)) ||
            setsockopt(m_childChannel, SOL_SOCKET, SO_PASSCRED, &pass, sizeof(pass))) {
            closeChannel(); m_state = "helper_channel_unavailable"; m_process = nullptr; process->deleteLater(); return status();
        }
        // Qt runs this supported hook after stdio setup and before closing
        // extra descriptors. Preserve only the authenticated socket as fd 0.
        // No KWin/XCB/malloc code runs in the forked child before exec.
        const int childChannel = m_childChannel;
        process->setChildProcessModifier([childChannel] { if (dup2(childChannel, STDIN_FILENO) < 0) _exit(127); });
        process->setUnixProcessParameters(QProcess::UnixProcessFlag::CloseFileDescriptors |
                                         QProcess::UnixProcessFlag::ResetSignalHandlers);
        process->setStandardInputFile(QProcess::nullDevice());
        args << expiresMs << QStringLiteral("0");
        m_notifier = std::make_unique<QSocketNotifier>(m_channel, QSocketNotifier::Read, this);
        connect(m_notifier.get(), &QSocketNotifier::activated, this, [this, process = QPointer<QProcess>(process), token] {
            if (!process || m_token != token || m_process != process) return;
            if (m_notifier) m_notifier->setEnabled(false);
            char packet[5]{};
            if (m_state != "fencing" ||
                !receiveOwnedPacket(m_channel, pid_t(process->processId()), packet, sizeof(packet)) || memcmp(packet, "ready", 5)) {
                m_state = "helper_channel_rejected"; process->kill(); return;
            }
            if (write(m_channel, m_nonce, sizeof(m_nonce)) != sizeof(m_nonce)) {
                m_state = "helper_channel_lost"; process->kill();
            }
        });
        connect(process, &QProcess::started, this, [this, process = QPointer<QProcess>(process), token] {
            if (process && m_token == token && m_process == process && m_childChannel >= 0) { close(m_childChannel); m_childChannel = -1; }
        });
        process->setProgram(QString::fromLatin1(JOETOO_CLOSE_HELPER)); process->setArguments(args);
        process->setStandardErrorFile(QProcess::nullDevice());
        connect(process, qOverload<int, QProcess::ExitStatus>(&QProcess::finished), this,
            [this, process = QPointer<QProcess>(process), token](int code, QProcess::ExitStatus exit) {
                if (!process) return;
                const auto receipt = process->readAllStandardOutput();
                if (m_token == token && m_process == process) {
                    // Keep only bounded result facts; never retain raw stdout, stderr or credentials.
                    m_helperExitKnown = true;
                    m_helperExitCode = code;
                    m_helperExitStatus = exit == QProcess::NormalExit ? QStringLiteral("normal") : QStringLiteral("crash");
                    m_helperReceiptOk = receipt == "dispatched\n";
                    if (exit == QProcess::NormalExit && code == 0 && m_helperReceiptOk)
                        m_state = m_gone ? "closed" : "dispatching";
                    else if (m_state == "fencing" || m_state == "dispatching") m_state = "dispatch_failed";
                    closeChannel(); m_process = nullptr; m_deadline = 0;
                }
                process->deleteLater();
            });
        connect(process, &QProcess::errorOccurred, this, [this, process = QPointer<QProcess>(process), token](QProcess::ProcessError error) {
            if (process && m_token == token && m_process == process && error == QProcess::FailedToStart) {
                closeChannel(); m_process = nullptr; m_state = "helper_unavailable"; process->deleteLater();
            }
        });
        m_timer.start();
        process->start();
        return status();
    }
    Q_SCRIPTABLE QString Status(const QString &token)
    {
        if (!authorized() || token != m_token) return json({{"state", "denied"}});
        return status();
    }
private:
    bool authorized() const { return calledFromDBus() && !m_owner.isEmpty() && message().service() == m_owner; }
    bool valid(EffectWindow *w) const
    {
        return w && !w->isDeleted() && w->isManaged() && w->isNormalWindow() && w->pid() > 0 &&
            (w->isX11Client() != w->isWaylandClient()) && w->window();
    }
    QString status() const
    {
        auto *live = effects->findWindow(m_uuid);
        const bool gone = m_gone && (!live || live->isDeleted() || !live->isManaged());
        const QString state = m_state == "closed" && !gone ? QStringLiteral("dispatching") : m_state;
        QJsonObject result{{"state", state}, {"token", m_token}, {"uuid", m_uuid.toString(QUuid::WithoutBraces)},
            {"helper_reaped", !m_process}, {"gone", gone}};
        // Optional diagnostics appear only after a known-reaped X11 dispatch failure.
        if (state == "dispatch_failed" && m_helperExitKnown && !m_process) {
            result.insert("helper_exit_code", m_helperExitCode);
            result.insert("helper_exit_status", m_helperExitStatus);
            result.insert("helper_receipt_ok", m_helperReceiptOk);
        }
        return json(result);
    }
    void closeChannel()
    {
        m_notifier.reset();
        if (m_channel >= 0) { close(m_channel); m_channel = -1; }
        if (m_childChannel >= 0) { close(m_childChannel); m_childChannel = -1; }
    }
    void invalidate()
    {
        closeChannel();
        if (m_process) m_process->kill();
        if (!m_token.isEmpty()) m_state = "source_lost";
    }
    void setupGuard()
    {
        auto *c = effects->xcbConnection(); if (!c || !effects->x11RootWindow()) return;
        m_guard = xcb_generate_id(c);
        // Unmapped InputOnly protocol mailbox, not an application/window observer.
        xcb_create_window(c, XCB_COPY_FROM_PARENT, m_guard, effects->x11RootWindow(), 0, 0, 1, 1, 0,
            XCB_WINDOW_CLASS_INPUT_ONLY, XCB_COPY_FROM_PARENT, 0, nullptr);
        auto cookie = xcb_intern_atom(c, false, sizeof("_JOETOO_KWIN_CLOSE_FENCE_V1") - 1, "_JOETOO_KWIN_CLOSE_FENCE_V1");
        m_atomSequence = cookie.sequence; m_atomDeadline = m_clock.elapsed() + 3000;
        m_timer.start();
        xcb_flush(c);
    }
    std::unique_ptr<QSocketNotifier> m_notifier;
    int m_channel = -1, m_childChannel = -1;
    QDBusConnection m_bus;
    QString m_owner, m_token, m_state = "idle", m_class;
    QStringList m_used;
    QUuid m_uuid;
    QPointer<EffectWindow> m_window;
    QPointer<QProcess> m_process;
    QElapsedTimer m_clock;
    QTimer m_timer;
    qint64 m_deadline = 0;
    xcb_window_t m_guard = 0, m_xid = 0;
    xcb_atom_t m_atom = 0;
    uint32_t m_nonce[4]{};
    unsigned int m_atomSequence = 0;
    qint64 m_atomDeadline = 0;
    int m_pid = 0;
    int m_helperExitCode = 0;
    QString m_helperExitStatus;
    bool m_helperExitKnown = false, m_helperReceiptOk = false;
    bool m_gone = false, m_registered = false, m_ownerSeen = false;
};
// Refuse the other compositor variant before constructing native window code.
// The loader separately checks the exact KWin factory IID/version.
KWIN_EFFECT_FACTORY_SUPPORTED_ENABLED(ManagedClose, "metadata.json",
    return effects && QDBusConnection::sessionBus().isConnected() &&
        QFileInfo(QCoreApplication::applicationFilePath()).fileName() == QLatin1StringView(JOETOO_COMPOSITOR_BINARY);,
    return false;)
} // namespace KWin
#include "adapter.moc"
