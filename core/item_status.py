"""User-facing status labels: strict tracker states plus optional (Not Seen) tag."""


from config import RSSI_DISPLAY_LOST_MAX, STRONG_RSSI_RECOVERY_THRESHOLD


def get_status(rssi):
    """
    RSSI band helper (e.g. CLI). Does not return \"Not Seen\"; invalid/missing RSSI maps to \"With You\".
    """
    if rssi is None:
        return "With You"
    try:
        r = float(rssi)
    except (TypeError, ValueError):
        return "With You"
    if r >= STRONG_RSSI_RECOVERY_THRESHOLD:
        return "With You"
    if r > RSSI_DISPLAY_LOST_MAX:
        return "Moving Away"
    return "Left Behind"


def get_item_display_status(item):
    """
    Primary label from tracker state only: Left Behind / Moving Away / With You.
    Appends \" (Not Seen)\" when is_visible is False (not a separate state).
    """
    if item.state == "LEFT BEHIND":
        base = "Left Behind"
    elif item.state == "LEAVING":
        base = "Moving Away"
    else:
        base = "With You"

    if getattr(item, "is_visible", True) is False:
        return f"{base} (Not Seen)"
    return base
