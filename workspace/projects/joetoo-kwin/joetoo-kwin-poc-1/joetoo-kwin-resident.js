// joetoo-kwin-resident.js
// Resident KWin 6 script: one D-Bus-brokered move operation.
const BRIDGE = "org.joetoo.KWinBridge";
const PATH = "/org/joetoo/KWinBridge";

function moveFromBroker() {
    // Capture focus before the asynchronous D-Bus round trip.
    const win = workspace.activeWindow;

    callDBus(BRIDGE, PATH, BRIDGE, "Take", function (payload) {
        if (!payload) return; // No pending request.

        let request;
        try {
            request = JSON.parse(payload);
        } catch (err) {
            console.warn("joetoo: malformed broker reply: " + err);
            return;
        }

        function finish(result, detail) {
            callDBus(BRIDGE, PATH, BRIDGE, "Complete",
                     request.id, result, String(detail));
        }

        if (!win) {
            finish("ERROR", "No active window at shortcut invocation");
            return;
        }

        const desktop = workspace.desktops[request.desktop - 1];
        if (!desktop) {
            finish("ERROR", "Virtual desktop " + request.desktop + " does not exist");
            return;
        }

        try {
            // save prior geometry
            const before = win.frameGeometry;
            // assing string value of current desktop before move
            const beforeDesktop = win.onAllDesktops ? "all" :
                      win.desktops[0].x11DesktopNumber;
            // compose message describing state before move
            const beforeText = "[" + beforeDesktop +"] " + "(" + before.x + "," + before.y + ") " +
                   before.width + "x" + before.height;

            const wasTiled = win.tile !== null;
            const wasFullscreen = win.fullScreen;

            win.desktops = [desktop];
            win.frameGeometry = {
                x: request.x,
                y: request.y,
                width: request.width,
                height: request.height
            };

            // Report actual readback, not merely successful command delivery.
            const g = win.frameGeometry;
            // get string value of current desktop after move
            const afterDesktop = win.onAllDesktops ? "all" :
                     win.desktops[0].x11DesktopNumber;
            // compose message describing state after move
            const afterText = "[" + afterDesktop + "] " +
                           "(" + g.x + "," + g.y + ") " +
                           g.width + "x" + g.height;
            // verify the window is positioned and sized as requested
            const match = afterDesktop === request.desktop &&
                          g.x === request.x && g.y === request.y &&
                          g.width === request.width && g.height === request.height;

            finish(match ? "OK" : "ERROR",
                   win.caption + ':\n' +
                   " before=" + beforeText + '\n' +
                   " after=" + afterText + '\n' +
                   " tiled=" + wasTiled + " fullscreen=" + wasFullscreen + '\n' +
                   (match ? "" : " (geometry differs from request)"));

        } catch (err) {
            finish("ERROR", "KWin operation failed: " + err);
        }
    });
}

registerShortcut("joetoo_bridge_move", "Joetoo brokered move", "", moveFromBroker);
