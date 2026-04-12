import shlex
import sys
import time

from config import SIMULATION_ITEM_NAMES, USE_SIMULATION
from core.alert_manager import AlertManager
from core.device_manager import DeviceManager
from core.item_manager import ItemManager
from core.movement import MovementSimulator
from core.notifier import Notifier
from core.storage_manager import StorageManager
from core.system_engine import SystemEngine
from core.location import get_current_location
from simulation.rssi_simulator import generate_multi_rssi
from visualization.run_map import show_map


def run_device_cli():
    storage = StorageManager()
    dm = DeviceManager(storage)
    print(
        "Device manager - commands: list | remove <name> | rename <old> <new> | quit"
    )
    print("(Use quotes for names with spaces, e.g. remove \"My Wallet\")")
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                print()
                break
            if not line:
                continue
            lowered = line.lower()
            if lowered in ("quit", "exit", "q"):
                break
            try:
                parts = shlex.split(line)
            except ValueError as e:
                print(f"Could not parse command: {e}")
                continue
            if not parts:
                continue
            cmd = parts[0].lower()
            if cmd == "list":
                dm.list_devices()
            elif cmd == "remove":
                if len(parts) < 2:
                    print("Usage: remove <name>")
                    continue
                dm.remove_device(" ".join(parts[1:]))
            elif cmd == "rename":
                if len(parts) != 3:
                    print(
                        'Usage: rename <old> <new>  '
                        '(example: rename Keys CarKeys  or  rename "My Keys" CarKeys)'
                    )
                    continue
                dm.rename_device(parts[1], parts[2])
            else:
                print(f"Unknown command: {cmd!r}. Try list, remove, or rename.")
    except KeyboardInterrupt:
        print("\nExiting device manager.")
    finally:
        storage.flush()


def main():
    if not USE_SIMULATION:
        print(
            "USE_SIMULATION is False in config.py. "
            "Run the Flask app (python app.py) for real hardware."
        )
        return

    manager = ItemManager()
    alert_manager = AlertManager()
    notifier = Notifier(alert_manager)
    engine = SystemEngine(manager, notifier, alert_manager)
    movement_sim = MovementSimulator()

    def run_loop():
        while True:
            rssi_raw = generate_multi_rssi(SIMULATION_ITEM_NAMES)
            rssi_data = {name: seq[-1] for name, seq in rssi_raw.items()}
            location = get_current_location()
            moving = movement_sim.is_user_moving()
            engine.update(location, moving, rssi_data)
            print("------")
            time.sleep(2)
            show_map(manager)

    try:
        run_loop()
    except KeyboardInterrupt:
        print("Shutting down system safely...")
    finally:
        engine.cleanup()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manage":
        run_device_cli()
    else:
        main()
