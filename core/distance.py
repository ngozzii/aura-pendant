
import math

def rssi_to_distance(rssi, rssi_0=-50, n=2.5):
    """
    Convert RSSI to estimated distance (meters)
    """
    return round(10 ** ((rssi_0 - rssi) / (10 * n)), 2)