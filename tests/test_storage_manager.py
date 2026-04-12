import os

from core.storage_manager import StorageManager


def test_add_device(tmp_path):
    file = tmp_path / "test.json"
    sm = StorageManager(file_path=os.fspath(file))

    sm.add_device("Keys", "123")
    sm.flush()

    assert any(d["name"] == "Keys" for d in sm.get_devices())


def test_update_last_seen(tmp_path):
    file = tmp_path / "test.json"
    sm = StorageManager(file_path=os.fspath(file))

    sm.add_device("Keys", "123")
    sm.update_last_seen("Keys", -65)
    sm.flush()

    data = sm.get_last_seen("Keys")
    assert data["rssi"] == -65


def test_rename_device(tmp_path):
    file = tmp_path / "test.json"
    sm = StorageManager(file_path=os.fspath(file))

    sm.add_device("Keys", "123")
    sm.rename_device("Keys", "CarKeys")
    sm.flush()

    assert sm.get_last_seen("Keys") is None
