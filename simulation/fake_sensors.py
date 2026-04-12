import random

from config import SIMULATION_ITEM_NAMES

_RSSI_CLOSE = -30.0
_RSSI_FAR = -100.0


def get_location():
    return {
        "lat": 45.4215 + random.uniform(-0.001, 0.001),
        "lon": -75.6972 + random.uniform(-0.001, 0.001),
    }


def is_moving():
    return random.random() > 0.3


def _init_state(name, store):
    if name not in store:
        store[name] = {
            "rssi": float(random.uniform(-68, -48)),
            "direction": random.choice(["toward", "away", "stable"]),
            "ticks_to_direction_roll": random.randint(5, 10),
            "away_streak_left": 0,
        }


# Per-device RSSI simulation state (persists across scan_rssi calls)
_rssi_sim_state = {}


def scan_rssi():
    """
    Simulate RSSI with directional trends so leaving / lost detection can fire.
    Each call is one "update" (~2s apart in the app loop).
    """
    data = {}

    for item in SIMULATION_ITEM_NAMES:
        _init_state(item, _rssi_sim_state)
        s = _rssi_sim_state[item]

        forced_away = s["away_streak_left"] > 0
        if forced_away:
            s["direction"] = "away"
        else:
            s["ticks_to_direction_roll"] -= 1
            if s["ticks_to_direction_roll"] <= 0:
                s["ticks_to_direction_roll"] = random.randint(5, 10)
                r = random.random()
                if r < 0.6:
                    pass
                elif r < 0.8:
                    s["direction"] = "away"
                else:
                    s["direction"] = "toward"
                if random.random() < 0.35:
                    s["away_streak_left"] = random.randint(5, 10)

        d = s["direction"]
        if d == "away":
            s["rssi"] -= random.uniform(2, 5)
        elif d == "toward":
            s["rssi"] += random.uniform(2, 5)
        else:
            s["rssi"] += random.uniform(-1.5, 1.5)

        s["rssi"] = max(_RSSI_FAR, min(_RSSI_CLOSE, s["rssi"]))

        if forced_away:
            s["away_streak_left"] -= 1

        rssi_out = int(round(s["rssi"]))
        data[item] = rssi_out
        print(f"[SIM] {item} -> {d} -> RSSI: {rssi_out}")

    return data
