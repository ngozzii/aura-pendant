"""Tests for core.system_engine."""

from unittest.mock import MagicMock, patch

from core.storage_manager import StorageManager
from core.system_engine import SystemEngine


def test_ble_name_mapping(tmp_path):
    sm = StorageManager(str(tmp_path / "ble_mapping.json"))
    sm.data = {
        "devices": [
            {"name": "CarKeys", "ble_name": "Keys", "id": "1"},
        ],
        "last_seen": {},
        "settings": {"cooldown": 5},
    }

    with patch("core.alert_manager.MotorController", return_value=MagicMock()):
        engine = SystemEngine(MagicMock(), MagicMock(), MagicMock())
    engine.storage = sm

    name = engine._display_name_for_ble("Keys")
    assert name == "CarKeys"
