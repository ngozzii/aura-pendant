import atexit
import threading
import time

from flask import Flask, render_template, send_file, request, redirect

from config import USE_SIMULATION
from core.alert_manager import AlertManager
from core.item_manager import ItemManager
from core.notifier import Notifier
from core.system_engine import SystemEngine
from visualization.map_view import generate_map

if USE_SIMULATION:
    from simulation.fake_sensors import get_location, is_moving, scan_rssi
else:
    from sensors.gps import get_location
    from sensors.motion import get_movement
    from sensors.bluetooth import scan_rssi

# -----------------------------
# Flask app
# -----------------------------
app = Flask(__name__)

# -----------------------------
# System setup
# -----------------------------
manager = ItemManager()
alert_manager = AlertManager()
notifier = Notifier(alert_manager)
engine = SystemEngine(manager, notifier, alert_manager)

atexit.register(engine.cleanup)


def _registered_trackers():
    names = [d["name"] for d in engine.storage.get_devices() if d.get("name")]
    return [manager.get_item(n) for n in names]


# -----------------------------
# Background system loop (REAL SYSTEM BEHAVIOR)
# -----------------------------
def background_update():
    while True:
        try:
            location = get_location()
            moving = is_moving() if USE_SIMULATION else get_movement()
            rssi_data = scan_rssi()

            engine.update(location, moving, rssi_data)

        except Exception as e:
            print(f"[ERROR] Sensor update failed: {e}")

        time.sleep(2)  # update interval


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def dashboard():
    # IMPORTANT: DO NOT update system here anymore
    items = _registered_trackers()

    registered_ble = {
        d.get("ble_name") or d.get("name")
        for d in engine.storage.get_devices()
    }

    detected_devices = engine.detected_devices

    return render_template(
        "index.html",
        items=items,
        detected_devices=detected_devices,
        registered_ble=registered_ble,
    )


@app.route("/add", methods=["POST"])
def add_device():
    name = request.form.get("name", "").strip()
    ble_name = request.form.get("ble_name", "").strip()
    display_name = name or ble_name
    if display_name:
        if ble_name:
            engine.storage.create_device(display_name, ble_name)
        else:
            engine.storage.create_device(display_name)
        engine.storage.flush()
    return redirect("/")


@app.route("/rename", methods=["POST"])
def rename_device():
    old = request.form.get("old_name", "").strip()
    new = request.form.get("new_name", "").strip()
    if old and new:
        if engine.storage.rename_device(old, new):
            manager.rename_item(old, new)
        engine.storage.flush()
    return redirect("/")


@app.route("/remove", methods=["POST"])
def remove_device():
    name = request.form.get("name", "").strip()
    if name:
        engine.storage.remove_device(name)
        manager.discard_item(name)
        engine.storage.flush()
    return redirect("/")


@app.route("/map")
def map_view():
    focus_item = request.args.get("item")
    center_param = request.args.get("center")
    center_on_user = center_param == "user"

    items = _registered_trackers()
    pendant_location = get_location()

    map_center = None

    if center_on_user:
        map_center = pendant_location
    elif focus_item:
        for item in items:
            if item.name == focus_item and item.last_location:
                map_center = item.last_location
                break

    if not map_center:
        for item in items:
            if item.last_location:
                map_center = item.last_location
                break

    if not map_center:
        map_center = pendant_location

    filename = generate_map(
        map_center,
        pendant_location,
        items,
        focus_item=focus_item,
        center_on_user=center_on_user,
    )

    return send_file(filename)


# -----------------------------
# Start system
# -----------------------------
if __name__ == "__main__":
    # Start background sensor loop
    thread = threading.Thread(target=background_update)
    thread.daemon = True
    thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
