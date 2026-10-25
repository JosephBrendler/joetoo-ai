js=/home/joe/scratch/joetoo-kwin-resident.js
id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript  "$js" "joetoo-resident")
qdbus6 org.kde.KWin "/Scripting/Script$id" org.kde.kwin.Script.run
qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.shortcutNames | grep -i joetoo

echo "if you see \"joetoo_test_move\" then run --> "
echo "qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut \"joetoo_test_move\""
