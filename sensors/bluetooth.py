import asyncio

from bleak import BleakScanner

# Only include advertisements stronger than this (dBm); reduces distant/noisy devices.
_RSSI_MIN_EXCLUSIVE = -75


def _rssi_from_pair(device, adv):
    if adv is not None and getattr(adv, "rssi", None) is not None:
        return adv.rssi
    return getattr(device, "rssi", None)


def _normalize_name(device):
    n = getattr(device, "name", None) or ""
    return n.strip()


def _row_from_device(device, adv):
    name = _normalize_name(device)
    if not name:
        return None
    rssi = _rssi_from_pair(device, adv)
    if rssi is None:
        return None
    if rssi <= _RSSI_MIN_EXCLUSIVE:
        return None
    address = (getattr(device, "address", None) or "").strip()
    if not address:
        return None
    return {
        "name": device.name.strip() if device.name else name,
        "address": address,
        "rssi": int(rssi),
    }


async def _scan_rssi_async():
    """
    Discover nearby BLE peripherals. No filtering by tracked devices.
    Returns sorted list of dicts: name, address, rssi (strongest first).
    """
    rows = []

    try:
        discovered = await BleakScanner.discover(timeout=2.0, return_adv=True)
    except TypeError:
        discovered = await BleakScanner.discover(timeout=2.0)
        for device in discovered:
            row = _row_from_device(device, None)
            if row:
                rows.append(row)
        by_addr = {}
        for row in rows:
            key = row["address"].lower().replace("-", ":")
            if key not in by_addr or row["rssi"] > by_addr[key]["rssi"]:
                by_addr[key] = row
        return sorted(by_addr.values(), key=lambda x: -x["rssi"])

    for _address, (device, adv) in discovered.items():
        row = _row_from_device(device, adv)
        if row:
            rows.append(row)

    by_addr = {}
    for row in rows:
        key = row["address"].lower().replace("-", ":")
        if key not in by_addr or row["rssi"] > by_addr[key]["rssi"]:
            by_addr[key] = row
    return sorted(by_addr.values(), key=lambda x: -x["rssi"])


def scan_rssi():
    """
    Returns all nearby BLE devices with a non-empty name and RSSI > -75 dBm.

    Each entry:
        {"name": str, "address": str, "rssi": int}
    Sorted by RSSI descending (strongest first).

    Requires: pip install bleak
    """
    return asyncio.run(_scan_rssi_async())
