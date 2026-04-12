# =========================
# RSSI Detection
# =========================

WINDOW_SIZE = 5
MIN_DROP_COUNT = 3

# RSSI must decrease by at least this amount over the window
RSSI_TOTAL_CHANGE_THRESHOLD = -10


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
CONSECUTIVE_LEAVING_THRESHOLD = 2

# RSSI level at which an item is considered "back with user"
STRONG_RSSI_RECOVERY_THRESHOLD = -60

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
USE_SIMULATION = True