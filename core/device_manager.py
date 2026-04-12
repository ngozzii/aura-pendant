"""CLI-oriented helpers for registered devices in StorageManager."""

from datetime import datetime

from core.item_status import get_status


def _format_display_timestamp(iso_ts):
    if not iso_ts or not isinstance(iso_ts, str):
        return str(iso_ts)
    try:
        normalized = iso_ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        return dt.strftime("%b %d, %H:%M")
    except (ValueError, TypeError, OSError):
        return iso_ts


class DeviceManager:
    def __init__(self, storage):
        self.storage = storage

    def list_devices(self):
        devices = self.storage.get_devices()
        if not devices:
            print("No devices registered.")
            return
        for d in devices:
            name = d.get("name", "?")
            dev_id = d.get("id") or d.get("device_id") or "?"
            seen = self.storage.get_last_seen(name)
            if (
                seen
                and isinstance(seen, dict)
                and "timestamp" in seen
                and "rssi" in seen
            ):
                ts_raw = seen["timestamp"]
                ts_display = _format_display_timestamp(ts_raw)
                status = get_status(seen["rssi"])
                tail = f"status: {status} | last seen: {ts_display}"
            else:
                tail = "status: Not Seen | No recent data"
            print(f"  {name} (id: {dev_id}) | {tail}")

    def remove_device(self, name):
        self.storage.remove_device(name)

    def rename_device(self, old_name, new_name):
        self.storage.rename_device(old_name, new_name)
