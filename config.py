# =========================
# RSSI Detection
# =========================

WINDOW_SIZE = 5

# Net RSSI change (last - first) must be <= this (dBm) for is_leaving(); paired with drop_ratio in detector.py
RSSI_TOTAL_CHANGE_THRESHOLD = -5


# =========================
# Timing (seconds)
# =========================

ALERT_INTERVAL_SECONDS = 6
COOLDOWN_SECONDS = 10


# =========================
# Notification
# =========================

MAX_ALERTS = 3


# =========================
# System Engine
# =========================

# Number of consecutive detections required before confirming "leaving"
CONSECUTIVE_LEAVING_THRESHOLD = 3

# RSSI level at which an item is considered "back with user"
STRONG_RSSI_RECOVERY_THRESHOLD = -60

# At or below this (weaker signal), SystemEngine may set LEAVING even if trend is noisy
RSSI_WEAK_THRESHOLD = -65

# Below this (weaker signal) user-facing status shows "Left Behind" when not overridden by tracker state
RSSI_DISPLAY_LOST_MAX = -85

# =========================
# Movement (MPU6050)
# =========================

# Threshold for accelerometer-based movement detection
MOVEMENT_THRESHOLD = 0.8


# =========================
# BLE (real hardware)
# =========================

# Friendly name (system) → BLE advertised name substring (case-insensitive partial match)
TARGET_DEVICES = {
    "Keys": "3119 AP Keys",
}


# =========================
# Simulation (only when USE_SIMULATION is True)
# =========================

# Friendly names used by fake_sensors.scan_rssi() and the demo CLI (main.py)
SIMULATION_ITEM_NAMES = ["Keys", "Wallet", "Bag"]

# When USE_SIMULATION is True and storage has no devices yet, seed tracked items (testing only).
# Real hardware mode never auto-seeds; tracked list is only what is loaded from storage.json.
SIMULATION_SEED_TRACKED_IF_EMPTY = True


# =========================
# Map UI (simulation + real)
# =========================

# Small lat/lon offsets so pins stay visible when locations share a base point
ITEM_MAP_OFFSETS = {
    "Keys": (0.0001, 0.0001),
    "Wallet": (-0.0001, 0.0001),
    "Bag": (0.0001, -0.0001),
}


# =========================
# Mode Toggle (single source of truth)
# =========================

# False = use REAL hardware (BLE + MPU6050); no simulation code path in app.py
# True  = use simulation.fake_sensors only
USE_SIMULATION = False