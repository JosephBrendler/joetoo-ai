js="$PWD/joetoo-kwin-resident.js"
id=$(qdbus6 org.kde.KWin /Scripting  org.kde.kwin.Scripting.loadScript "$js" joetoo-bridge)
echo "Loaded script ID: $id"
qdbus6 org.kde.KWin "/Scripting/Script$id" org.kde.kwin.Script.run
qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.shortcutNames | grep -Fx joetoo_bridge_move
echo "if you see \"joetoo_bridge_move\", then run -->"
echo "./joetoo-kwin move 3 100 80 850 700"
