"""
Centralizes haptic / motor alerts with priority and consolidation.

Higher-priority patterns interrupt lower ones on the motor. Duplicate same-or-lower
priority while a pattern is active is ignored. Cooldown limits repeated warnings when
nothing is currently vibrating.
"""

import time

from hardware.motor_controller import MotorController


class AlertManager:
    PRIORITY = {
        "warning": 1,
        "escalated": 2,
        "lost": 3,
    }

    COOLDOWN_SECONDS = 5.0

    def __init__(self, motor_pin=18):
        self._motor = MotorController(pin=motor_pin)
        self._current_priority = 0
        self._is_active = False
        self._last_vibration_time = 0.0

    def _on_vibration_complete(self):
        self._current_priority = 0
        self._is_active = False

    def trigger_alert(self, item_name, alert_type="warning"):
        if alert_type not in self.PRIORITY:
            alert_type = "warning"

        new_priority = self.PRIORITY[alert_type]
        now = time.time()
        upgrading = self._is_active and new_priority > self._current_priority

        if not upgrading and new_priority == self.PRIORITY["warning"]:
            if now - self._last_vibration_time < self.COOLDOWN_SECONDS:
                print("Suppressed (cooldown)")
                return

        if self._is_active and new_priority <= self._current_priority:
            print("Ignoring duplicate alert")
            return

        if upgrading:
            if alert_type == "escalated":
                print("Upgrading alert to ESCALATED")
            elif alert_type == "lost":
                print("Upgrading alert to LOST")
            else:
                print("Upgrading alert level")
            self._motor.stop()

        if alert_type == "lost":
            print(f"Triggering LOST pattern: [{item_name}]")

        self._current_priority = new_priority
        self._is_active = True
        self._last_vibration_time = time.time()

        done = self._on_vibration_complete

        if alert_type == "warning":
            print(f"ALERT (warning): [{item_name}]")
            self._motor.vibrate(1.0, done)
        elif alert_type == "escalated":
            print(f"ALERT (escalated): [{item_name}]")
            self._motor.vibrate(2.0, done)
        else:
            self._motor.vibrate_pulses(3, 0.15, 0.1, done)

    def cleanup(self):
        self._motor.cleanup()
