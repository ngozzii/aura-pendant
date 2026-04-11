import asyncio

from bleak import BleakScanner

from config import TARGET_DEVICES


def _rssi_from_pair(device, adv):
    if adv is not None and getattr(adv, "rssi", None) is not None:
        return adv.rssi
    return getattr(device, "rssi", None)


def _match_device_to_targets(device, adv, result):
    """If device.name matches a target substring, set result[friendly_name] = rssi (first wins per friendly)."""
    if device.name is None:
        return
    dn_lower = device.name.lower()
    rssi = _rssi_from_pair(device, adv)
    if rssi is None:
        return

    for friendly_name, target_name in TARGET_DEVICES.items():
        if friendly_name in result:
            continue
        if target_name.lower() in dn_lower:
            print(f"[BLE] Matched {friendly_name}: {device.name} ({rssi})")
            result[friendly_name] = rssi


async def _scan_rssi_async():
    """Scan ~2s; return friendly_name -> RSSI for matched TARGET_DEVICES only."""
    result = {}

    try:
        discovered = await BleakScanner.discover(timeout=2.0, return_adv=True)
    except TypeError:
        discovered = await BleakScanner.discover(timeout=2.0)
        for device in discovered:
            _match_device_to_targets(device, None, result)
        return result

    for _address, (device, adv) in discovered.items():
        _match_device_to_targets(device, adv, result)

    return result


def scan_rssi():
    """
    Returns only registered BLE peripherals, e.g.:
        {"Keys": -65}
    Missing devices are omitted. Requires: pip install bleak
    """
    return asyncio.run(_scan_rssi_async())
