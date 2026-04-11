import random

from config import SIMULATION_ITEM_NAMES


def get_location():
    return {
        "lat": 45.4215 + random.uniform(-0.001, 0.001),
        "lon": -75.6972 + random.uniform(-0.001, 0.001)
    }


def is_moving():
    return random.random() > 0.3


def scan_rssi():
    data = {}
    for item in SIMULATION_ITEM_NAMES:
        base = -50
        data[item] = base - random.randint(5, 25)

    return data
