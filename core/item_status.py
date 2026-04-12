"""User-facing status labels from RSSI and tracker state."""

from config import RSSI_DISPLAY_LOST_MAX, STRONG_RSSI_RECOVERY_THRESHOLD


def get_status(rssi):
    """
    Map RSSI (dBm) to a coarse status. Stronger signal = higher numeric value.
    Bands use STRONG_RSSI_RECOVERY_THRESHOLD as the inclusive lower bound for "With You"
    (same nominal level as recovery in system_engine, which uses strict > for GPIO logic).
    """
    if rssi is None:
        return "Not Seen"
    try:
        r = float(rssi)
    except (TypeError, ValueError):
        return "Not Seen"
    if r >= STRONG_RSSI_RECOVERY_THRESHOLD:
        return "With You"
    if r > RSSI_DISPLAY_LOST_MAX:
        return "Moving Away"
    return "Left Behind"


def get_item_display_status(item):
    """Tracker state overrides RSSI when the engine has marked leaving / lost."""
    if item.state == "LEFT BEHIND":
        return "Left Behind"
    if item.state == "LEAVING":
        return "Moving Away"
    return get_status(item.last_rssi)
