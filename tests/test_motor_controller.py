"""Unit tests for hardware.motor_controller."""

from unittest.mock import patch

from hardware.motor_controller import MotorController


@patch("hardware.motor_controller._GPIO_AVAILABLE", False)
def test_simulation_mode():
    mc = MotorController()
    assert mc.simulation_mode is True


def test_vibrate_sets_flag():
    mc = MotorController()
    try:
        mc.vibrate(0.1)
        assert mc._is_vibrating is True
    finally:
        mc.cleanup()
