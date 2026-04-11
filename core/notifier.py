import time

from config import ALERT_INTERVAL_SECONDS, COOLDOWN_SECONDS, MAX_ALERTS
from sensors.vibration import vibrate


class Notifier:
    def __init__(self):
        self.alert_count = 0
        self.state = "IDLE"

        self.last_alert_time = 0
        # ALERT_INTERVAL_SECONDS: spacing between escalations, configurable in config.py
        self.alert_interval = ALERT_INTERVAL_SECONDS

        self.cooldown_until = 0
        # Items that received LEAVING this session (cleared on reset for dashboard)
        self._tracked_alert_items = []

    def reset(self):
        for item in self._tracked_alert_items:
            if item.state == "LEAVING":
                item.state = "WITH YOU"
        self._tracked_alert_items = []
        self.alert_count = 0
        self.state = "IDLE"

    def update(self, leaving_items):
        now = time.time()

        # 🚫 Cooldown state
        if self.state == "COOLDOWN":
            if now < self.cooldown_until:
                return
            else:
                self.reset()

        # 🚫 No leaving → reset
        if not leaving_items:
            if self.state != "IDLE":
                print("[INFO] Leaving stopped → resetting alerts")
            self.reset()
            return

        # 🚫 Not enough time passed → do nothing
        if now - self.last_alert_time < self.alert_interval:
            return

        # 🚀 Start alert sequence
        if self.state == "IDLE":
            self.state = "ALERTING"
            self.alert_count = 1
            self._send_alert(leaving_items)
            self.last_alert_time = now
            return

        # 🔁 Continue alert sequence (MAX_ALERTS from config.py)
        if self.state == "ALERTING":
            self.alert_count += 1

            if self.alert_count <= MAX_ALERTS:
                self._send_alert(leaving_items)
                self.last_alert_time = now
            else:
                print(f"[FINAL] Marking items as LEFT BEHIND: {self._names(leaving_items)}")

                for item in leaving_items:
                    item.mark_left_behind()

                self.state = "COOLDOWN"
                # COOLDOWN_SECONDS: post-final wait, configurable in config.py
                self.cooldown_until = now + COOLDOWN_SECONDS

    def _send_alert(self, items):
        names = self._names(items)

        if self.alert_count == 1:
            print(f"[ALERT 1] You might be leaving: {names}")
        elif self.alert_count == 2:
            print(f"[ALERT 2] You ARE leaving: {names}")
        elif self.alert_count == MAX_ALERTS:
            print(f"[ALERT 3] FINAL WARNING for: {names}")

        # Dashboard: at-risk items show as LEAVING (vibration level still follows alert tier)
        by_name = {i.name: i for i in self._tracked_alert_items}
        for item in items:
            item.state = "LEAVING"
            by_name[item.name] = item
        self._tracked_alert_items = list(by_name.values())

        vibrate("warning" if self.alert_count == 1 else "alert")

    def _names(self, items):
        return ", ".join([item.name for item in items])
