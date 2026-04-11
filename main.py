
from config import ITEM_MAP_OFFSETS, SIMULATION_ITEM_NAMES, USE_SIMULATION
from core.detector import is_leaving
from core.movement import MovementSimulator
from core.notifier import Notifier
from core.item_manager import ItemManager
from simulation.rssi_simulator import generate_multi_rssi
from utils.logger import log
from core.location import get_current_location
from core.distance import rssi_to_distance
from visualization.run_map import show_map

import time


def main():
    if not USE_SIMULATION:
        print("USE_SIMULATION is False in config.py. Run the Flask app (python app.py) for real hardware.")
        return

    manager = ItemManager()
    notifier = Notifier()
    movement_sim = MovementSimulator()

    while True:
        rssi_data = generate_multi_rssi(SIMULATION_ITEM_NAMES)

        leaving_flags = {}

        for name in SIMULATION_ITEM_NAMES:
            rssi_values = rssi_data[name]
            current_rssi = rssi_values[-1]

            distance = rssi_to_distance(current_rssi)

            base_location = get_current_location()

            lat_offset, lon_offset = ITEM_MAP_OFFSETS.get(name, (0, 0))

            location = {
                "lat": base_location["lat"] + lat_offset,
                "lon": base_location["lon"] + lon_offset
            }

            manager.update_item(name, current_rssi, location, distance)

            log(f"{name} → RSSI: {current_rssi}, Distance: {distance}m")

            leaving = is_leaving(rssi_values)
            leaving_flags[name] = leaving

            log(f"{name} RSSI: {rssi_values} → Leaving: {leaving}")

        moving = movement_sim.is_user_moving()
        log(f"User moving: {moving}")

        # Determine which items are being left
        leaving_items = []

        for name in SIMULATION_ITEM_NAMES:
            tracker = manager.get_item(name)

            if tracker.is_lost():
                log(f"{name} is already lost. Tracking only.")

                # Reconnection logic
                if tracker.last_rssi > -55:
                    tracker.mark_tracking()
                    notifier.reset()

            elif leaving_flags[name] and moving:
                # Only include if RSSI is sufficiently weak
                if tracker.last_rssi < -60:
                    leaving_items.append(tracker)

        # 🚨 Send grouped alert
        if leaving_items:
            log("CONFIRMED: User is leaving items")

            # Sort by weakest signal (most urgent first)
            leaving_items.sort(key=lambda x: x.last_rssi)

            notifier.update(leaving_items)

        else:
            log("No issue detected.")
            notifier.reset()

        print("------")
        time.sleep(2)
        show_map(manager)


if __name__ == "__main__":
    main()
