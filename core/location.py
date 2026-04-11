import random

def get_current_location():
    """
    Simulated location (replace later with GPS or phone location)
    """
    return {
        "lat": round(45.4215 + random.uniform(-0.001, 0.001), 6),
        "lon": round(-75.6972 + random.uniform(-0.001, 0.001), 6)
    }