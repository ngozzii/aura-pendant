from flask import Flask, render_template, send_file, request
import threading
import time

from config import USE_SIMULATION
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
notifier = Notifier()
engine = SystemEngine(manager, notifier)


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
    items = list(manager.all_items())

    return render_template(
        "index.html",
        items=items
    )


@app.route("/map")
def map_view():
    focus_item = request.args.get("item")
    center_param = request.args.get("center")
    center_on_user = center_param == "user"

    items = list(manager.all_items())
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
