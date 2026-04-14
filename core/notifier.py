import time

from config import ALERT_INTERVAL_SECONDS, COOLDOWN_SECONDS, MAX_ALERTS


class Notifier:
    """Alert escalation only; item LEAVING / WITH YOU state is owned by SystemEngine."""

    def __init__(self, alert_manager):
        self._alert_manager = alert_manager
        self.alert_count = 0
        self.state = "IDLE"

        self.last_alert_time = 0
        self.alert_interval = ALERT_INTERVAL_SECONDS

        self.cooldown_until = 0

    def on_engine_forced_lost(self):
        """Engine marked item LEFT BEHIND; align notifier cooldown."""
        now = time.time()
        self.state = "COOLDOWN"
        self.cooldown_until = now + COOLDOWN_SECONDS
        self.alert_count = 0

    def reset(self):
        """Reset notifier machine only — does not change ItemTracker.state."""
        self.alert_count = 0
        self.state = "IDLE"

    def update(self, leaving_items, leaving_hysteresis_active=False):
        now = time.time()

        if self.state == "COOLDOWN":
            if now < self.cooldown_until:
                return
            self.reset()

        if not leaving_items:
            if leaving_hysteresis_active:
                return
            if self.state != "IDLE":
                print("[INFO] Leaving stopped → resetting alerts")
            self.reset()
            return

        if now - self.last_alert_time < self.alert_interval:
            return

        if self.state == "IDLE":
            self.state = "ALERTING"
            self.alert_count = 1
            self._send_alert(leaving_items)
            self.last_alert_time = now
            return

        if self.state == "ALERTING":
            self.alert_count += 1

            if self.alert_count <= MAX_ALERTS:
                self._send_alert(leaving_items)
                self.last_alert_time = now
            else:
                print(f"[FINAL] Marking items as LEFT BEHIND: {self._names(leaving_items)}")

                names = self._names(leaving_items)
                for item in leaving_items:
                    item.mark_left_behind()

                self._alert_manager.trigger_alert(names, "lost")

                self.state = "COOLDOWN"
                self.cooldown_until = now + COOLDOWN_SECONDS

    def _send_alert(self, items):
        names = self._names(items)

        if self.alert_count == 1:
            print(f"[ALERT 1] You might be leaving: {names}")
        elif self.alert_count == 2:
            print(f"[ALERT 2] You ARE leaving: {names}")
            self._alert_manager.trigger_alert(names, "escalated")
        elif self.alert_count == MAX_ALERTS:
            print(f"[ALERT 3] FINAL WARNING for: {names}")
            self._alert_manager.trigger_alert(names, "escalated")

    def _names(self, items):
        return ", ".join([item.name for item in items])
