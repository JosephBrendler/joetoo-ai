# Unload the previously running implementation - test exit status and capture resulting text string
if result=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "joetoo-bridge"); then
    echo "result: [$result]; exited 0; stopped"
else
    echo "result: [$result]; exited non-zero [$?]"
fi
