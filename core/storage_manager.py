"""JSON file persistence for devices, last seen, and settings."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class StorageManager:
    def __init__(self, file_path="data/storage.json"):
        self.file_path = file_path
        self._dirty = False
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            self.load()
        else:
            self.data = self._default_structure()
            self.save()
            print("Loaded storage data")

    @staticmethod
    def _default_structure():
        return {
            "devices": [],
            "last_seen": {},
            "settings": {
                "cooldown": 5,
            },
        }

    def _ensure_structure(self, raw):
        if not isinstance(raw, dict):
            raise ValueError("root must be an object")
        base = self._default_structure()
        devices = raw.get("devices")
        last_seen = raw.get("last_seen")
        settings = raw.get("settings")
        base["devices"] = devices if isinstance(devices, list) else []
        base["last_seen"] = last_seen if isinstance(last_seen, dict) else {}
        if isinstance(settings, dict):
            base["settings"] = {**base["settings"], **settings}
        return base

    def load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.data = self._ensure_structure(raw)
        except FileNotFoundError:
            self.data = self._default_structure()
            self.save()
        except (json.JSONDecodeError, OSError, ValueError, TypeError) as e:
            print(
                f"[StorageManager] Warning: corrupted or invalid JSON ({e}); "
                "resetting to default structure."
            )
            self.data = self._default_structure()
            self.save()
        print("Loaded storage data")
        return self.data

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        print("Saved storage data")

    def flush(self):
        if self._dirty:
            self.save()
            self._dirty = False

    def get_devices(self):
        return self.data["devices"]

    def create_device(self, name, ble_name=None):
        name = (name or "").strip()
        ble_name = (ble_name or "").strip() or name
        if not name:
            print("Device name cannot be empty")
            return False
        if not ble_name:
            print("BLE name cannot be empty")
            return False
        if any(d.get("name") == name for d in self.data["devices"]):
            print("Device already exists")
            return False
        eff_ble = ble_name
        if any((d.get("ble_name") or d.get("name")) == eff_ble for d in self.data["devices"]):
            print("This BLE device is already registered")
            return False
        device_id = uuid.uuid4().hex
        self.data["devices"].append(
            {"name": name, "ble_name": eff_ble, "id": device_id}
        )
        self._dirty = True
        print(f"Created device: [{name}] (BLE: {eff_ble})")
        return True

    def add_device(self, name, device_id):
        for d in self.data["devices"]:
            if d.get("name") == name:
                return
        self.data["devices"].append({"name": name, "device_id": device_id})
        self._dirty = True
        print(f"Added device: [{name}]")

    def update_last_seen(self, name, rssi):
        self.data["last_seen"][name] = {
            "rssi": rssi,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._dirty = True
        print(f"Updated last seen for [{name}] (RSSI: {rssi})")

    def get_last_seen(self, name):
        return self.data["last_seen"].get(name)

    def remove_device(self, name):
        name = (name or "").strip()
        if not name:
            print("Device name cannot be empty; nothing removed.")
            return False
        devices = self.data["devices"]
        idx = None
        for i, d in enumerate(devices):
            if d.get("name") == name:
                idx = i
                break
        if idx is None:
            print(f"No device named [{name}] in storage; nothing removed.")
            return False
        devices.pop(idx)
        self.data["last_seen"].pop(name, None)
        self._dirty = True
        print(f"Removed device: [{name}]")
        return True

    def rename_device(self, old_name, new_name):
        old_name = (old_name or "").strip()
        new_name = (new_name or "").strip()
        if not old_name or not new_name:
            print("Rename requires non-empty old and new names.")
            return False
        if old_name == new_name:
            print("Old and new name are the same; nothing to do.")
            return False
        if any(d.get("name") == new_name for d in self.data["devices"]):
            print(
                f"A device named [{new_name}] already exists; "
                "choose a different name or remove the existing device first."
            )
            return False
        for d in self.data["devices"]:
            if d.get("name") == old_name:
                d["name"] = new_name
                if old_name in self.data["last_seen"]:
                    self.data["last_seen"][new_name] = self.data["last_seen"].pop(
                        old_name
                    )
                self._dirty = True
                print(f"Renamed device: {old_name} -> {new_name}")
                return True
        print(f"No device named [{old_name}] in storage; rename cancelled.")
        return False
