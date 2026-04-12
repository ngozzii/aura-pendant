"""Unit tests for core.alert_manager."""

from unittest.mock import MagicMock, patch

from core.alert_manager import AlertManager


class MockMotor:
    def __init__(self):
        self.triggered = False

    def vibrate(self, duration, on_complete=None):
        self.triggered = True

    def vibrate_pulses(self, count, on_duration, off_duration, on_complete=None):
        self.triggered = True

    def stop(self):
        pass

    def cleanup(self):
        pass


def test_warning_triggers_motor():
    with patch("core.alert_manager.MotorController", return_value=MagicMock()):
        am = AlertManager()
        am._motor = MockMotor()

        am.trigger_alert("Keys", "warning")
        assert am._motor.triggered is True


def test_cooldown_blocks_repeat():
    with patch("core.alert_manager.MotorController", return_value=MagicMock()):
        am = AlertManager()
        am._motor = MockMotor()

        am.trigger_alert("Keys", "warning")
        am._motor.triggered = False

        am.trigger_alert("Keys", "warning")
        assert am._motor.triggered is False


def test_escalation_triggers():
    with patch("core.alert_manager.MotorController", return_value=MagicMock()):
        am = AlertManager()
        am._motor = MockMotor()

        am.trigger_alert("Keys", "warning")
        am._motor.triggered = False

        am.trigger_alert("Keys", "escalated")
        assert am._motor.triggered is True
