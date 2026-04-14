
import time

class ItemTracker:
    def __init__(self, name):
        self.name = name
        self.state = "WITH YOU"
        # False until a scan row matches this item; UI may append "(Not Seen)" when False.
        self.is_visible = False
        self.last_seen_time = None
        self.last_rssi = None
        self.last_location = None
        self.history = []
        self.last_distance = None

    def update(self, rssi, location, distance):

        self.last_seen_time = time.time()
        self.last_rssi = rssi
        # Freeze location once item is marked as left behind.
        # This ensures the system preserves where the item was left behind
        # for visualization and recovery purposes.
        if self.state != "LEFT BEHIND":
            self.last_location = location
        self.last_distance = distance

        self.history.append({
            "time": self.last_seen_time,
            "rssi": rssi,
            "distance": distance,
            "location": location if self.state != "LEFT BEHIND" else self.last_location
        })

        if len(self.history) > 50:
            self.history.pop(0)

    def mark_left_behind(self):
        self.state = "LEFT BEHIND"

        info = self.get_last_seen_info()

        print(f"[TRACKER] {self.name} marked as LEFT BEHIND")
        print(f"  → Last seen {info['seconds_ago']}s ago")
        print(f"  → Location: {info['location']}")
        print(f"  → Estimated distance: {self.last_distance}m")

    def mark_tracking(self):
        if self.state == "LEFT BEHIND":
            print(f"[TRACKER] {self.name} RECONNECTED")
        self.state = "WITH YOU"

    def is_lost(self):
        return self.state == "LEFT BEHIND"

    @property
    def status_kind(self):
        """CSS / badge key: left-behind | moving-away | with-you (not the full label)."""
        if self.state == "LEFT BEHIND":
            return "left-behind"
        if self.state == "LEAVING":
            return "moving-away"
        return "with-you"

    @property
    def display_status(self):
        from core.item_status import get_item_display_status

        return get_item_display_status(self)

    def get_last_seen_info(self):
        if not self.last_seen_time:
            return "No data"

        import time
        seconds_ago = int(time.time() - self.last_seen_time)

        return {
            "seconds_ago": seconds_ago,
            "location": self.last_location,
            "rssi": self.last_rssi
        }
