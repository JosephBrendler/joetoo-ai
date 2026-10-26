printf 'Session: %s\n' "${XDG_SESSION_TYPE:-unset}"
printf 'Bus:     %s\n' "${DBUS_SESSION_BUS_ADDRESS:-unset}"
printf 'Runtime: %s\n' "${XDG_RUNTIME_DIR:-unset}"

test -S "$XDG_RUNTIME_DIR/bus" &&
    echo 'Runtime session-bus socket exists'

ps -u "$USER" -o pid,ppid,tty,args |
    grep -E '[d]bus-daemon|[d]bus-broker|[k]win_wayland|[k]win_x11'

qdbus6 org.kde.KWin /KWin
