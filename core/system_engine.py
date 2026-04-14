import time

from config import (
    CONSECUTIVE_LEAVING_THRESHOLD,
    ITEM_MAP_OFFSETS,
    RSSI_WEAK_THRESHOLD,
    STRONG_RSSI_RECOVERY_THRESHOLD,
    WINDOW_SIZE,
)
from core.distance import rssi_to_distance
from core.detector import is_leaving
from core.storage_manager import StorageManager

# Align with sensors/bluetooth.py filtering for normalized scan lists
_RSSI_MIN_EXCLUSIVE = -75


def _address_norm(addr):
    return (addr or "").strip().lower().replace("-", ":")


def is_scan_row_tracked(row, devices):
    """True if a discovered scan row is already in the persisted tracked list."""
    if not isinstance(row, dict) or not devices:
        return False
    r_addr = _address_norm(row.get("address", ""))
    r_name = (row.get("name") or "").strip().lower()
    if not r_addr or not r_name:
        return False
    for d in devices:
        if not isinstance(d, dict):
            continue
        da = _address_norm(d.get("address") or "")
        if da and da == r_addr:
            return True
        ble = (d.get("ble_name") or "").strip().lower()
        dn = (d.get("name") or "").strip().lower()
        if ble and r_name and (ble in r_name or r_name in ble):
            return True
        if dn and dn == r_name:
            return True
    return False


class SystemEngine:
    def __init__(self, manager, notifier, alert_manager):
        self.manager = manager
        self.notifier = notifier
        self.alert_manager = alert_manager
        self.storage = StorageManager()
        self.detected_devices = []
        self._last_save_time = 0.0
        self.leaving_counter = {}
        self.last_leaving_time = {}
        self.leaving_confirmed = {}
        self.threshold = CONSECUTIVE_LEAVING_THRESHOLD
        self.rssi_history = {}

    def cleanup(self):
        try:
            self.storage.flush()
            if hasattr(self, "alert_manager"):
                self.alert_manager.cleanup()
            print("SystemEngine cleanup complete")
        except Exception as e:
            print(f"Cleanup error: {e}")

    def _display_name_for_ble(self, ble_key):
        """Resolve display name from a scan key (address or legacy name). Used by tests and matching."""
        for d in self.storage.get_devices():
            dn = d.get("name")
            if not dn:
                continue
            mapped = d.get("ble_name")
            da = d.get("address")
            if da and _address_norm(da) == _address_norm(ble_key):
                return dn
            if mapped and mapped == ble_key:
                return dn
            if (not mapped) and dn == ble_key:
                return dn
        return None

    @staticmethod
    def _normalize_scan_results(raw):
        """
        Accept list of {name, address, rssi} (preferred) or legacy dict name -> rssi (e.g. CLI sim).
        """
        if isinstance(raw, list):
            out = []
            for x in raw:
                if not isinstance(x, dict):
                    continue
                try:
                    rssi = int(x["rssi"])
                except (KeyError, TypeError, ValueError):
                    continue
                name = (x.get("name") or "").strip()
                address = (x.get("address") or "").strip()
                if not name or not address:
                    continue
                if rssi <= _RSSI_MIN_EXCLUSIVE:
                    continue
                out.append({"name": name, "address": address, "rssi": rssi})
            out.sort(key=lambda z: -z["rssi"])
            return out
        if isinstance(raw, dict):
            out = []
            for k, v in raw.items():
                try:
                    rssi = int(v)
                except (TypeError, ValueError):
                    continue
                if rssi <= _RSSI_MIN_EXCLUSIVE:
                    continue
                key = str(k)
                out.append(
                    {
                        "name": key,
                        "address": f"sim:{key}",
                        "rssi": rssi,
                    }
                )
            out.sort(key=lambda z: -z["rssi"])
            return out
        return []

    def _match_tracked_device_to_scan(self, device, scan_list):
        """Pick the best scan row for a persisted device (address first, then name / ble_name)."""
        d_addr = _address_norm(device.get("address") or "")
        ble_hint = (device.get("ble_name") or device.get("name") or "").strip().lower()
        disp = (device.get("name") or "").strip().lower()
        candidates = []
        for row in scan_list:
            r_addr = _address_norm(row.get("address", ""))
            r_name = (row.get("name") or "").strip().lower()
            rssi = row["rssi"]
            rank = None
            if d_addr and r_addr == d_addr:
                rank = 3
            elif ble_hint and r_name and (ble_hint in r_name or r_name in ble_hint):
                rank = 2
            elif disp and r_name == disp:
                rank = 1
            if rank is None:
                continue
            candidates.append((rank, rssi, row))
        if not candidates:
            return None
        candidates.sort(key=lambda t: (-t[0], -t[1]))
        return candidates[0][2]

    def _leaving_hysteresis_active(self):
        """True if any item still has leaving counter or recent trend_away activity (<5s)."""
        now = time.time()
        for device in self.storage.get_devices():
            name = device.get("name")
            if not name:
                continue
            if self.leaving_counter.get(name, 0) > 0:
                return True
            t = self.last_leaving_time.get(name)
            if t is not None and (now - t) < 5.0:
                return True
        return False

    def update(self, location, moving, scan_raw):
        scan_list = self._normalize_scan_results(scan_raw)
        self.detected_devices = list(scan_list)

        leaving_items = []
        now_tick = time.time()

        for device in self.storage.get_devices():
            name = device.get("name")
            if not name:
                continue

            match = self._match_tracked_device_to_scan(device, scan_list)
            tracker = self.manager.get_item(name)

            if not match:
                tracker.is_visible = False
                if not tracker.is_lost():
                    tracker.mark_left_behind()
                    self.alert_manager.trigger_alert(name, "lost")
                    self.notifier.on_engine_forced_lost()
                    self.leaving_counter[name] = 0.0
                    self.last_leaving_time.pop(name, None)
                    self.leaving_confirmed[name] = False
                    self.rssi_history.setdefault(name, []).clear()
                continue

            tracker.is_visible = True
            rssi = match["rssi"]
            ble_key = match["address"]

            self.storage.update_last_seen(name, rssi)

            if tracker.is_lost() and rssi > STRONG_RSSI_RECOVERY_THRESHOLD:
                tracker.mark_tracking()
                self.leaving_counter[name] = 0.0
                self.rssi_history[name] = []
                self.last_leaving_time.pop(name, None)
                self.leaving_confirmed.pop(name, None)
            elif (
                tracker.state == "LEAVING"
                and rssi > STRONG_RSSI_RECOVERY_THRESHOLD
            ):
                tracker.state = "WITH YOU"
                self.leaving_counter[name] = 0.0
                self.last_leaving_time.pop(name, None)

            if name not in self.leaving_counter:
                self.leaving_counter[name] = 0.0

            if name not in self.rssi_history:
                self.rssi_history[name] = []

            history = self.rssi_history[name]

            if len(history) > 0 and not tracker.is_lost():
                prev = history[-1]
                if rssi - prev > 10:
                    continue

            distance = rssi_to_distance(rssi)

            lat_offset, lon_offset = ITEM_MAP_OFFSETS.get(
                name, ITEM_MAP_OFFSETS.get(match["name"], (0, 0))
            )

            item_location = {
                "lat": location["lat"] + lat_offset,
                "lon": location["lon"] + lon_offset,
            }

            self.manager.update_item(name, rssi, item_location, distance)

            history.append(rssi)

            if len(history) > WINDOW_SIZE:
                history.pop(0)

            if len(history) >= 2:
                trend_away = is_leaving(history)
            else:
                trend_away = False

            movement_label = "MOVING" if moving else "STILL"
            print(
                f"[ENGINE] {name} (ble={ble_key}) | RSSI: {history} | "
                f"{movement_label} | trend: {trend_away}"
            )

            is_leaving_now = trend_away
            is_weak_signal = rssi <= RSSI_WEAK_THRESHOLD

            prev_counter = self.leaving_counter[name]

            if is_leaving_now:
                self.leaving_counter[name] = self.leaving_counter.get(name, 0.0) + 1.0
                self.last_leaving_time[name] = now_tick
            else:
                self.leaving_counter[name] = max(
                    self.leaving_counter.get(name, 0.0) - 0.25, 0.0
                )

            if (
                self.leaving_counter[name] >= CONSECUTIVE_LEAVING_THRESHOLD
                or is_weak_signal
            ):
                if not tracker.is_lost() and tracker.state != "LEAVING":
                    tracker.state = "LEAVING"

            if self.leaving_counter[name] >= self.threshold:
                if not tracker.is_lost():
                    leaving_items.append(tracker)
                    if prev_counter < self.threshold:
                        self.alert_manager.trigger_alert(name, "warning")

        self.notifier.update(leaving_items, self._leaving_hysteresis_active())

        now = time.time()
        if now - self._last_save_time > 5:
            self.storage.flush()
            self._last_save_time = now
