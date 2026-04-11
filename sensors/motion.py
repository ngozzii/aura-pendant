"""
MPU6050 accelerometer-based movement detection (I2C address 0x68).
Requires: smbus2 or smbus (typical on Raspberry Pi).
"""

MOVEMENT_DIFF_THRESHOLD = 0.8

MPU6050_ADDR = 0x68
_REG_PWR_MGMT_1 = 0x6B
_REG_ACCEL_XOUT_H = 0x3B

_ACCEL_SCALE = 16384.0  # ±2 g full scale
_I2C_BUS = 1

try:
    from smbus2 import SMBus
except ImportError:
    try:
        from smbus import SMBus
    except ImportError:
        SMBus = None

_bus = None
_prev_x = None
_prev_y = None
_prev_z = None
_init_failed = False


def _read_word_2c(bus, reg):
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    val = (high << 8) | low
    if val >= 0x8000:
        val -= 0x10000
    return val


def _read_accel_g(bus):
    x = _read_word_2c(bus, _REG_ACCEL_XOUT_H) / _ACCEL_SCALE
    y = _read_word_2c(bus, _REG_ACCEL_XOUT_H + 2) / _ACCEL_SCALE
    z = _read_word_2c(bus, _REG_ACCEL_XOUT_H + 4) / _ACCEL_SCALE
    return x, y, z


def _ensure_sensor():
    global _bus
    if _bus is not None:
        return
    if SMBus is None:
        raise RuntimeError("smbus2 or smbus is required for MPU6050")
    bus = SMBus(_I2C_BUS)
    bus.write_byte_data(MPU6050_ADDR, _REG_PWR_MGMT_1, 0)
    _bus = bus


def get_movement():
    """
    Read accelerometer, compare to previous sample (g units).
    Returns True if abs(dx)+abs(dy)+abs(dz) > MOVEMENT_DIFF_THRESHOLD.
    """
    global _prev_x, _prev_y, _prev_z, _init_failed

    if _init_failed:
        return False

    try:
        _ensure_sensor()
    except (OSError, RuntimeError) as e:
        if not _init_failed:
            print(f"[motion] MPU6050 unavailable: {e}")
        _init_failed = True
        return False

    x, y, z = _read_accel_g(_bus)

    if _prev_x is None:
        _prev_x, _prev_y, _prev_z = x, y, z
        return False

    diff = abs(x - _prev_x) + abs(y - _prev_y) + abs(z - _prev_z)

    moving = diff > MOVEMENT_DIFF_THRESHOLD

    # smoothing: require 2 consecutive detections
    if not hasattr(get_movement, "prev_moving"):
        get_movement.prev_moving = False

    final_moving = moving and get_movement.prev_moving

    get_movement.prev_moving = moving

    _prev_x, _prev_y, _prev_z = x, y, z

    return final_moving
