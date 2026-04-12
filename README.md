# Aura Pendant — Wearable Item Awareness System

## 1. Project title and overview

**Aura Pendant** is a wearable-computing prototype that helps people notice when they may be **walking away from personal items** (keys, wallet, bag, and similar). The system continuously estimates proximity using **Bluetooth-style signal strength (RSSI)**, combines it with **movement context**, and drives **alerts plus haptic-style feedback** when the trend suggests separation.

**Real-world use case:** reduce forgotten or left-behind items by warning the wearer *before* they have fully walked away—useful for campus, commuting, or daily routines where small items are easy to misplace.

**What this repository delivers:**

- **Tracking** — periodic RSSI updates per item, with status labels on the dashboard.
- **Alerts** — staged text alerts and coordinated motor patterns when leaving is inferred.
- **Web UI** — Flask dashboard to register devices, see status, and open a map.
- **Persistence** — registered devices stored in JSON under `data/` (created at runtime; folder is gitignored).

The default configuration runs in **simulation mode** (no physical BLE radio required), which is appropriate for coursework demos and repeatable evaluation.

---

## 2. Features

- **Device detection (simulated BLE)** — `simulation/fake_sensors.py` produces RSSI readings with directional trends (toward / away / stable) so leaving behavior can be demonstrated without hardware.
- **Intelligent alerting (trend-based)** — the engine and notifier use RSSI history, movement, and configurable thresholds (`config.py`) rather than a single weak reading.
- **Haptic feedback (motor simulation)** — `hardware/motor_controller.py` drives a GPIO vibration motor on Raspberry Pi when available; on laptops it **falls back to console messages** so the pipeline still runs.
- **Device registration via UI** — add, rename, and remove tracked items from the dashboard; optional BLE name hints for matching when using real hardware paths.
- **Persistent storage (JSON)** — `data/storage.json` holds the device list (auto-created; not committed to version control).
- **Interactive dashboard and map** — HTML dashboard plus a **Folium** map with color-coded pins by item status.
- **Unit testing (pytest)** — automated tests for core logic, storage, alerts, motor behavior, and the system engine.

---

## 3. Tech stack

| Area | Technology |
|------|------------|
| Language | **Python 3** |
| Web server / UI | **Flask**, **Jinja2** templates |
| Map | **Folium** (generates **Leaflet**-based HTML maps) |
| Testing | **pytest** (see `requirements-dev.txt`) |
| Data | **JSON** file storage |
| Optional hardware | **RPi.GPIO** on Raspberry Pi for motor output; **simulated fallback** when GPIO is unavailable |
| Sensors (demo) | **`simulation/fake_sensors.py`** — simulated GPS jitter, movement, and BLE RSSI |

---

## 4. Project structure

| Path | Role |
|------|------|
| `app.py` | Flask application: background sensor loop, routes for dashboard, add/rename/remove, and map image. |
| `main.py` | Optional **CLI** runner for simulation / device management without the browser. |
| `config.py` | Central thresholds, timing, simulation item names, map offsets, and **`USE_SIMULATION`** toggle. |
| `core/` | Domain logic: **`system_engine.py`** (main update loop), **`alert_manager.py`**, **`notifier.py`**, **`item_manager.py`**, **`tracker.py`**, **`storage_manager.py`**, **`device_manager.py`**, **`item_status.py`**. |
| `hardware/` | **`motor_controller.py`** — GPIO motor control with simulation fallback. |
| `simulation/` | **`fake_sensors.py`** — fake location, movement, and RSSI for demo mode. |
| `sensors/` | Real-hardware stubs / modules (GPS, motion, Bluetooth) used when **`USE_SIMULATION`** is `False`. |
| `visualization/` | **`map_view.py`** — builds the Folium map file served by `/map`. |
| `templates/` | **`index.html`** — dashboard layout, forms, and status display. |
| `data/` | Runtime **`storage.json`** (ignored by git). |
| `tests/` | **pytest** suite (`test_*.py`, `conftest.py`). |
| `requirements-dev.txt` | Pin for **pytest** (dev / CI). |

---

## 5. Installation and setup

### Prerequisites

- **Python 3.10+** recommended (any recent Python 3.x should work).
- A modern web browser for the dashboard and map.

### Install dependencies

From the project root:

```bash
pip install flask folium
```

For **tests** (and optional CI):

```bash
pip install -r requirements-dev.txt
```

On a **Raspberry Pi** where you intend to use GPIO for the motor (optional):

```bash
pip install RPi.GPIO
```

If `RPi.GPIO` is missing or setup fails, the motor controller **automatically uses simulation mode** (console output only).

### Run the system

```bash
python app.py
```

The app binds to **all interfaces** on port **5000** with Flask debug enabled.

### Open the dashboard

In your browser:

- **http://127.0.0.1:5000**

Other devices on the same network can use your machine’s LAN IP and port **5000** if firewall rules allow it.

---

## 6. Simulation mode

### `USE_SIMULATION` in `config.py`

`USE_SIMULATION` is the **single source of truth** for whether the app imports **`simulation.fake_sensors`** or the **`sensors.*`** hardware modules.

- **`True` (default)** — uses simulated location, movement, and RSSI. No physical BLE adapter is required. Ideal for coursework and consistent demos.
- **`False`** — switches imports to real sensor modules (`gps`, `motion`, `bluetooth`). You must implement or connect actual hardware for meaningful results.

### How fake BLE signals are generated

`simulation/fake_sensors.py` maintains **per-item state**: current RSSI, a **direction** (`toward`, `away`, `stable`), and occasional **forced “away” streaks**. Each background tick adjusts RSSI within a realistic clamp (roughly **-100 dBm** to **-30 dBm**) and prints a **`[SIM]`** line per item.

### Why simulation is used

Simulation makes the project **runnable on any laptop**, **deterministic enough to grade**, and **safe** for classroom use—while keeping the same software architecture you would use with real RSSI streams later.

---

## 7. How to use the system

1. **Start the app** — `python app.py` and wait for the background thread to begin (about every **2 seconds** per update).
2. **Open the dashboard** — visit `http://127.0.0.1:5000`.
3. **Review detected devices** — simulated scans surface names from `SIMULATION_ITEM_NAMES` in `config.py` (e.g. Keys, Wallet, Bag).
4. **Add a device** — use the form to register a display name (and optional BLE substring when moving to real hardware). Persisted to `data/storage.json`.
5. **Watch status updates** — statuses such as *With You*, *Moving Away*, *Left Behind*, and *Not Seen* refresh as RSSI and movement change.
6. **Observe alerts and motor simulation** — watch the **terminal** for alert lines and **`[SIMULATION] Motor ON/OFF`** when GPIO is not available.
7. **Use the map** — follow the dashboard link to **`/map`** (or embedded controls) to see the user and items on a Folium map with **status-colored markers**.

Optional: run **`python main.py`** for a **terminal-oriented** simulation loop and commands without starting Flask.

---

## 8. Understanding logs

Logs are written to the **console** (terminal where `app.py` or `main.py` runs). Typical prefixes:

| Prefix / pattern | Meaning |
|------------------|---------|
| `[SIM] Item -> direction -> RSSI: …` | **Simulated BLE scan** — one line per simulated item per tick; `direction` is `toward`, `away`, or `stable`. |
| `[ENGINE] … \| RSSI: …` | **System engine** — high-level snapshot of inferred state and RSSI history for an item. |
| `[ALERT 1]`, `[ALERT 2]`, `[ALERT 3]` | **Notifier escalation sequence** — staged “might be leaving” → stronger warnings (see `core/notifier.py`). |
| `ALERT (warning): [name]` / `ALERT (escalated): [name]` | **Alert manager** — motor-driving path for item-specific alerts. |
| `[SIMULATION] Motor ON` / `[SIMULATION] Motor OFF` | **Haptic path without GPIO** — same logical “vibrate” events, printed instead of toggling a pin. |
| `[MotorController] GPIO setup failed; using simulation mode.` | Motor fell back because GPIO was unavailable or misconfigured. |
| `[ERROR] Sensor update failed: …` | Exception in the background loop; the thread keeps running after the message. |

**RSSI in plain terms:** RSSI (Received Signal Strength Indicator) is a **rough proxy for distance** in radio systems—**higher** values (closer to **0**) usually mean **stronger** signal / **closer**; **lower** (more negative) usually mean **weaker** / **farther**. It is **not** an exact meter measurement.

**Trend:** the system cares about **how RSSI changes over several samples** (e.g. getting consistently weaker while you appear to be moving), not a single noisy reading—this reduces false alarms compared to a simple threshold.

---

## 9. Testing

Run the full suite from the project root:

```bash
python -m pytest -q
```

**Current scope:** **17** tests (collected via `pytest`).

They exercise, among others:

- **`core/item_status`** — display strings and status logic.
- **`core/alert_manager`** — alert coordination with a mock motor.
- **`core/notifier`** — escalation and timing behavior.
- **`core/storage_manager`** — JSON persistence helpers.
- **`core/system_engine`** — engine updates and BLE name mapping.
- **`hardware/motor_controller`** — simulation vs GPIO paths (mocked where needed).
- **Smoke** — light integration checks.

---

## 10. Limitations

- **RSSI is approximate** — environment, body blocking, multipath, and device power all distort “distance” from signal strength.
- **Simulation simplifies reality** — random trends stand in for radio physics; results are for **demonstration**, not certified safety or security.
- **No full production BLE stack in this repo** — the default path is simulated; real BLE integration depends on your platform and `sensors/bluetooth.py` implementation.
- **Single-machine demo** — the Flask app and storage are oriented toward **one running instance** and local JSON, not a cloud-backed multi-user product.

---

## 11. Future improvements

- **Real BLE integration** — pair stable device IDs, calibration, and background scanning on embedded Linux / mobile.
- **Better distance estimation** — sensor fusion (IMU + RSSI + optional UWB), per-environment calibration.
- **Mobile companion app** — notifications and quick “ping item” actions.
- **UI/UX** — onboarding, accessibility, historical charts, and calmer alert policies for daily wear.

---

## License and course use

This project is intended as a **university wearable computing** submission: clear architecture, runnable simulation, visible logs, and automated tests for reproducible evaluation. Adapt the prose or add your course name, authors, and license as required by your syllabus.
