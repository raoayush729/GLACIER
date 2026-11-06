const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("glacierOverlay", {
    // Open the main GLACIER chat window.
    openChat: () => {
        ipcRenderer.send("glacier:open-chat");
    },

    // Tell the main process a drag has started.
    dragStart: () => {
        ipcRenderer.send("glacier:drag-start");
    },

    // Tell the main process to move the window to the cursor.
    dragMove: () => {
        ipcRenderer.send("glacier:drag-move");
    },

    // Snap the overlay to the nearest display edge.
    finishMove: () => {
        ipcRenderer.send("glacier:finish-move");
    },

    // Receive the voice mode: stable, listening, executing or responding.
    onModeChange: (callback) => {
        ipcRenderer.on("glacier:mode", (_event, mode) => {
            callback(mode);
        });
    },

    // Receive the edge selected by the main process.
    onEdgeChange: (callback) => {
        ipcRenderer.on("glacier:edge", (_event, edge) => {
            callback(edge);
        });
    }
});