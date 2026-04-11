from config import MIN_DROP_COUNT, RSSI_TOTAL_CHANGE_THRESHOLD


def is_leaving(rssi_values):
    drops = 0

    for i in range(1, len(rssi_values)):
        if rssi_values[i] < rssi_values[i - 1]:
            drops += 1

    total_change = rssi_values[-1] - rssi_values[0]

    # MIN_DROP_COUNT / RSSI_TOTAL_CHANGE_THRESHOLD: configurable in config.py
    return drops >= MIN_DROP_COUNT and total_change < RSSI_TOTAL_CHANGE_THRESHOLD
