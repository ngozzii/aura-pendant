from config import RSSI_TOTAL_CHANGE_THRESHOLD


def is_leaving(history):
    """
    Detect overall movement away (weaker RSSI) over the window.

    Tolerant of small upward fluctuations: uses net change and fraction of
    step-to-step drops, not strict monotonic decrease.
    """
    # Fast detection for sudden signal drop (single step)
    if len(history) >= 2:
        if history[-1] - history[-2] <= -6:
            return True

    if len(history) < 2:
        return False

    first = history[0]
    last = history[-1]
    total_change = last - first

    drops = sum(1 for i in range(1, len(history)) if history[i] < history[i - 1])
    drop_ratio = drops / (len(history) - 1)

    return total_change <= RSSI_TOTAL_CHANGE_THRESHOLD and drop_ratio >= 0.4
