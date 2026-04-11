from config import (
    CONSECUTIVE_LEAVING_THRESHOLD,
    ITEM_MAP_OFFSETS,
    STRONG_RSSI_RECOVERY_THRESHOLD,
    WINDOW_SIZE,
)
from core.distance import rssi_to_distance
from core.detector import is_leaving


class SystemEngine:
    def __init__(self, manager, notifier):
        self.manager = manager
        self.notifier = notifier
        self.leaving_counter = {}
        # CONSECUTIVE_LEAVING_THRESHOLD: confirmation layer, configurable in config.py
        self.threshold = CONSECUTIVE_LEAVING_THRESHOLD
        self.rssi_history = {}

    def update(self, location, moving, rssi_data):

        leaving_items = []

        for name, rssi in rssi_data.items():
            tracker = self.manager.get_item(name)
            if tracker.is_lost() and rssi > STRONG_RSSI_RECOVERY_THRESHOLD:
                # If the item comes back within range, resume tracking automatically
                tracker.mark_tracking()

                # Reset detection state to avoid false triggers after recovery
                self.leaving_counter[name] = 0
                self.rssi_history[name] = []

            distance = rssi_to_distance(rssi)

            lat_offset, lon_offset = ITEM_MAP_OFFSETS.get(name, (0, 0))

            item_location = {
                "lat": location["lat"] + lat_offset,
                "lon": location["lon"] + lon_offset
            }

            # Update tracker with latest reading
            self.manager.update_item(name, rssi, item_location, distance)

            # Initialize structures if needed
            if name not in self.leaving_counter:
                self.leaving_counter[name] = 0

            if name not in self.rssi_history:
                self.rssi_history[name] = []

            # Maintain rolling RSSI history (WINDOW_SIZE from config.py)
            history = self.rssi_history[name]
            history.append(rssi)

            if len(history) > WINDOW_SIZE:
                history.pop(0)

            # Only evaluate trend when enough data exists
            if len(history) >= WINDOW_SIZE:
                trend_away = is_leaving(history)
            else:
                trend_away = False

            movement_label = "MOVING" if moving else "STILL"
            print(f"[ENGINE] {name} | RSSI: {history} | {movement_label} | trend: {trend_away}")

            # Leaving signal: RSSI trend only (accelerometer passed as `moving` for logs / future use)
            is_leaving_now = trend_away

            # Use counter as a confirmation layer to avoid noise
            if is_leaving_now:
                self.leaving_counter[name] += 1
            else:
                # gradual decay instead of full reset (BLE noise / brief trend dips)
                self.leaving_counter[name] = max(0, self.leaving_counter[name] - 1)

            # If confirmed over consecutive updates → mark as leaving
            if self.leaving_counter[name] >= self.threshold:
                if not tracker.is_lost():
                    leaving_items.append(tracker)

        # Pass grouped leaving items to notifier
        self.notifier.update(leaving_items)
