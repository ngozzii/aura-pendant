"""
Vibration motor via GPIO (BCM). Falls back to simulation when RPi.GPIO is unavailable
(e.g. development on Windows/Mac without a Pi), so the rest of the app never crashes.

Supports cooperative stop() so higher-priority alerts can interrupt an in-flight pattern.
"""

import threading
import time

try:
    import RPi.GPIO as GPIO

    _GPIO_AVAILABLE = True
except ImportError:
    GPIO = None
    _GPIO_AVAILABLE = False


class MotorController:
    _SLEEP_STEP = 0.01

    def __init__(self, pin=18):
        self.pin = pin
        self.simulation_mode = not _GPIO_AVAILABLE
        self._cleaned = False
        self._is_vibrating = False
        self._vibrate_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._motor_thread = None

        if not self.simulation_mode:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(self.pin, GPIO.OUT)
                GPIO.output(self.pin, GPIO.LOW)
            except Exception:
                self.simulation_mode = True
                print("[MotorController] GPIO setup failed; using simulation mode.")

    def _sleep_chunked(self, total_seconds):
        """Sleep in small steps so stop_event can interrupt."""
        elapsed = 0.0
        while elapsed < total_seconds:
            if self._stop_event.is_set():
                return False
            chunk = min(self._SLEEP_STEP, total_seconds - elapsed)
            time.sleep(chunk)
            elapsed += chunk
        return True

    def on(self):
        if self.simulation_mode:
            print("[SIMULATION] Motor ON")
        else:
            try:
                GPIO.output(self.pin, GPIO.HIGH)
                print("Motor ON")
            except Exception as e:
                print(f"[ERROR] GPIO ON failed: {e}")

    def off(self):
        if self.simulation_mode:
            print("[SIMULATION] Motor OFF")
        else:
            try:
                GPIO.output(self.pin, GPIO.LOW)
                print("Motor OFF")
            except Exception as e:
                print(f"[ERROR] GPIO OFF failed: {e}")

    def stop(self):
        """Stop in-flight vibration and release the busy flag so a new pattern can start."""
        self._stop_event.set()
        self.off()
        t = self._motor_thread
        if t is not None and t.is_alive():
            t.join(timeout=3.0)
        self._motor_thread = None
        with self._vibrate_lock:
            self._is_vibrating = False

    def vibrate(self, duration=1.0, on_complete=None):
        self._stop_event.clear()

        with self._vibrate_lock:
            if self._is_vibrating:
                print("Motor already active")
                return
            self._is_vibrating = True

        def _pulse():
            try:
                self.on()
                self._sleep_chunked(duration)
                self.off()
            finally:
                with self._vibrate_lock:
                    self._is_vibrating = False
                self._stop_event.clear()
                if on_complete:
                    try:
                        on_complete()
                    except Exception:
                        pass

        self._motor_thread = threading.Thread(target=_pulse, daemon=True)
        self._motor_thread.start()

    def vibrate_pulses(self, count=3, on_duration=0.15, off_duration=0.1, on_complete=None):
        self._stop_event.clear()

        with self._vibrate_lock:
            if self._is_vibrating:
                print("Motor already active")
                return
            self._is_vibrating = True

        def _pulses():
            try:
                for i in range(count):
                    if self._stop_event.is_set():
                        break
                    self.on()
                    if not self._sleep_chunked(on_duration):
                        break
                    self.off()
                    if i < count - 1 and not self._sleep_chunked(off_duration):
                        break
                self.off()
            finally:
                with self._vibrate_lock:
                    self._is_vibrating = False
                self._stop_event.clear()
                if on_complete:
                    try:
                        on_complete()
                    except Exception:
                        pass

        self._motor_thread = threading.Thread(target=_pulses, daemon=True)
        self._motor_thread.start()

    def cleanup(self):
        """Release GPIO resources; safe to call more than once."""
        if self._cleaned:
            return
        self.stop()
        if self.simulation_mode:
            self._cleaned = True
            return
        try:
            GPIO.cleanup()
        except Exception:
            pass
        self._cleaned = True


if __name__ == "__main__":
    motor = MotorController()
    try:
        motor.vibrate(2.0)
        time.sleep(2.2)
    finally:
        motor.cleanup()
