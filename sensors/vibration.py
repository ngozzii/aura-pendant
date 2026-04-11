# Set False when integrating a real vibration motor (GPIO / driver).
USE_SIMULATION_VIBRATION = True


def vibrate(level):
    """
    Trigger haptic feedback for the given alert level.

    level: "warning" | "alert"
    """
    if level not in ("warning", "alert"):
        print(f"[VIBRATION] Unknown level: {level}")
        return

    if USE_SIMULATION_VIBRATION:
        print(f"VIBRATE: {level}")
    else:
        # Future: GPIO — pulse motor / PWM pattern according to `level` (e.g. short bursts vs long).
        pass
