const { app, BrowserWindow, screen, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

// App icon (taskbar + window title bar). Keep icon.ico next to main.js.
const APP_ICON = path.join(__dirname, "icon.ico");

let mainWindow = null;
let overlayWindow = null;
let isQuitting = false;

const OVERLAY_SIZE = 90;
const EDGE_GAP = 0;

// Keep track of the edge where the orb is attached.
let overlayEdge = "right";

// Create the main GLACIER chat window.
function createMainWindow() {
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.show();
        mainWindow.focus();
        return;
    }

    mainWindow = new BrowserWindow({
        width: 1100,
        height: 750,
        minWidth: 800,
        minHeight: 550,
        title: "GLACIER",
        icon: APP_ICON,
        show: false,

        webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
            backgroundThrottling: false // keep voice polling fast when minimized
        }
    });

    mainWindow.loadFile(path.join(__dirname, "index.html"));

    mainWindow.once("ready-to-show", () => {
        if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.show();
        }
    });

    mainWindow.on("closed", () => {
        mainWindow = null;
    });
}

// Find the display closest to a given screen position.
function getDisplayArea(x, y) {
    const display = screen.getDisplayNearestPoint({ x, y });

    return {
        display,
        area: display.workArea
    };
}

// Keep the orb vertically within the usable display area.
function clampOverlayY(y, area) {
    const maxY = area.y + area.height - OVERLAY_SIZE;

    return Math.max(
        area.y,
        Math.min(y, maxY)
    );
}

// Create the floating orb.
function createOverlayWindow() {
    if (overlayWindow && !overlayWindow.isDestroyed()) {
        return;
    }

    const { workArea } = screen.getPrimaryDisplay();

    overlayWindow = new BrowserWindow({
        width: OVERLAY_SIZE,
        height: OVERLAY_SIZE,

        x: workArea.x + workArea.width - OVERLAY_SIZE,
        y: workArea.y + Math.round(
            (workArea.height - OVERLAY_SIZE) / 2
        ),

        frame: false,
        transparent: true,
        backgroundColor: "#00000000",
        resizable: false,
        movable: false,
        minimizable: false,
        maximizable: false,
        fullscreenable: false,
        skipTaskbar: true,
        icon: APP_ICON,
        alwaysOnTop: true,
        hasShadow: false,
        show: false,

        webPreferences: {
            preload: path.join(__dirname, "overlay_preload.js"),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    overlayWindow.setAlwaysOnTop(true, "floating");

    overlayWindow.loadFile(
        path.join(__dirname, "overlay.html")
    );

    overlayWindow.once("ready-to-show", () => {
        if (!overlayWindow || overlayWindow.isDestroyed()) {
            return;
        }

        overlayWindow.webContents.send(
            "glacier:edge",
            overlayEdge
        );

        overlayWindow.showInactive();
    });

    overlayWindow.on("closed", () => {
        overlayWindow = null;

        if (!isQuitting) {
            createOverlayWindow();
        }
    });
}

// Open the main chat window when the orb is clicked.
ipcMain.on("glacier:open-chat", () => {
    createMainWindow();
});

// Send pointer debugging information to the terminal.
ipcMain.on("glacier:debug-pointer", (_event, eventName) => {
    console.log("[GLACIER POINTER]", eventName);
});

// Helper: keep a value between a minimum and maximum.
function clamp(value, min, max) {
    return Math.max(min, Math.min(value, max));
}

// True while the orb is being dragged.
let isDragging = false;

// Drag start.
ipcMain.on("glacier:drag-start", () => {
    if (!overlayWindow || overlayWindow.isDestroyed()) return;

    isDragging = voiceMode === "stable";
});

// Drag move: keep the orb's CENTER under the cursor.
ipcMain.on("glacier:drag-move", () => {
    if (!isDragging || !overlayWindow || overlayWindow.isDestroyed()) return;

    const cursor = screen.getCursorScreenPoint();
    const { area } = getDisplayArea(cursor.x, cursor.y);
    const half = OVERLAY_SIZE / 2;

    // setBounds with a fixed size avoids Windows DPI size drift.
    overlayWindow.setBounds({
        x: Math.round(clamp(cursor.x - half, area.x, area.x + area.width - OVERLAY_SIZE)),
        y: Math.round(clamp(cursor.y - half, area.y, area.y + area.height - OVERLAY_SIZE)),
        width: OVERLAY_SIZE,
        height: OVERLAY_SIZE
    });
});

// Snap the orb to the nearest display edge: left, right, top or bottom.
ipcMain.on("glacier:finish-move", () => {
    isDragging = false;

    if (!overlayWindow || overlayWindow.isDestroyed()) {
        return;
    }

    const [x, y] = overlayWindow.getPosition();

    const { area } = getDisplayArea(
        x + OVERLAY_SIZE / 2,
        y + OVERLAY_SIZE / 2
    );

    const left = area.x + EDGE_GAP;
    const right = area.x + area.width - OVERLAY_SIZE - EDGE_GAP;
    const top = area.y + EDGE_GAP;
    const bottom = area.y + area.height - OVERLAY_SIZE - EDGE_GAP;

    const distances = {
        left: Math.abs(x - left),
        right: Math.abs(x - right),
        top: Math.abs(y - top),
        bottom: Math.abs(y - bottom)
    };

    // Pick the closest edge.
    overlayEdge = Object.keys(distances).reduce((a, b) =>
        distances[a] <= distances[b] ? a : b
    );

    let snappedX = clamp(x, left, right);
    let snappedY = clamp(y, top, bottom);

    if (overlayEdge === "left") snappedX = left;
    if (overlayEdge === "right") snappedX = right;
    if (overlayEdge === "top") snappedY = top;
    if (overlayEdge === "bottom") snappedY = bottom;

    overlayWindow.setBounds({
        x: snappedX,
        y: snappedY,
        width: OVERLAY_SIZE,
        height: OVERLAY_SIZE
    });

    overlayWindow.webContents.send("glacier:edge", overlayEdge);
});

// ---------------- Voice mode: stable / listening / executing / responding ----------------
const BACKEND_URL = "http://127.0.0.1:8000";
const LABEL_H = 36;
const GLOW_MARGIN = 56; // transparent room around the orb so the glow fades out
let voiceMode = "stable";
let restoreBounds = null;

// Grow the overlay downward to make room for the status label, then restore it.
function setOverlayExpanded(expanded) {
    if (!overlayWindow || overlayWindow.isDestroyed()) return;

    const b = overlayWindow.getBounds();

    if (expanded) {
        restoreBounds = b;
        const { area } = getDisplayArea(b.x + b.width / 2, b.y + b.height / 2);
        const cellH = OVERLAY_SIZE + LABEL_H;
        const cellY = Math.min(b.y, area.y + area.height - cellH);

        // Grow the window on every side so the glow never reaches its edge.
        overlayWindow.setBounds({
            x: b.x - GLOW_MARGIN,
            y: cellY - GLOW_MARGIN,
            width: OVERLAY_SIZE + GLOW_MARGIN * 2,
            height: cellH + GLOW_MARGIN * 2
        });
    } else if (restoreBounds) {
        overlayWindow.setBounds(restoreBounds);
        restoreBounds = null;
    }
}

// Ask the Python backend for the current mode and mirror it on the overlay.
async function pollVoiceState() {
    try {
        const res = await fetch(`${BACKEND_URL}/voice-state`);
        const { mode } = await res.json();

        if (mode !== voiceMode) {
            const wasActive = voiceMode !== "stable";
            voiceMode = mode;
            if (wasActive !== (mode !== "stable")) setOverlayExpanded(mode !== "stable");
        }

        if (overlayWindow && !overlayWindow.isDestroyed()) {
            overlayWindow.webContents.send("glacier:mode", voiceMode);
        }
    } catch (_) {
        // Backend not running yet; try again.
    }

    setTimeout(pollVoiceState, 100);
}

// ---------------- Voice listener (Python) is started and stopped with GLACIER ----------------
// Paths are relative to this UI folder. Adjust them if your folders are different.
const VOICE_PYTHON = path.join(__dirname, "..", ".venv", "Scripts", "python.exe");
const VOICE_SCRIPT = path.join(__dirname, "..", "Wake Word", "voice_listener.py");

let voiceProcess = null;

function startVoiceListener() {
    if (voiceProcess) return;

    voiceProcess = spawn(VOICE_PYTHON, ["-u", VOICE_SCRIPT], {
        cwd: path.dirname(VOICE_SCRIPT),
        windowsHide: true
    });

    voiceProcess.stdout.on("data", (d) => process.stdout.write(`[voice] ${d}`));
    voiceProcess.stderr.on("data", (d) => process.stderr.write(`[voice] ${d}`));

    voiceProcess.on("error", (err) => {
        console.error("[voice] could not start:", err.message);
        voiceProcess = null;
    });

    voiceProcess.on("exit", (code) => {
        console.log("[voice] stopped with code", code);
        voiceProcess = null;

        // Restart automatically if it crashed while GLACIER is still open.
        if (!isQuitting) setTimeout(startVoiceListener, 3000);
    });
}

function stopVoiceListener() {
    if (voiceProcess) {
        voiceProcess.kill();
        voiceProcess = null;
    }
}

// Start GLACIER.
app.whenReady().then(() => {
    createMainWindow();
    createOverlayWindow();
    pollVoiceState();
    startVoiceListener();

    app.on("activate", () => {
        createMainWindow();
    });
});

// Keep the application alive while the overlay exists.
app.on("window-all-closed", () => {
    if (process.platform === "darwin") {
        return;
    }

    if (!overlayWindow && !isQuitting) {
        createOverlayWindow();
    }
});

// Mark the application as exiting.
app.on("before-quit", () => {
    isQuitting = true;
    stopVoiceListener();
});