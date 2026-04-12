
from core.tracker import ItemTracker


class ItemManager:
    def __init__(self):
        self.items = {}

    def get_item(self, name):
        if name not in self.items:
            self.items[name] = ItemTracker(name)
        return self.items[name]

    def update_item(self, name, rssi, location, distance):
        self.get_item(name).update(rssi, location, distance)

    def all_items(self):
        return self.items.values()

    def discard_item(self, name):
        self.items.pop(name, None)

    def rename_item(self, old_name, new_name):
        if old_name not in self.items:
            return
        tracker = self.items.pop(old_name)
        tracker.name = new_name
        self.items[new_name] = tracker

    def get_leaving_items(self, leaving_flags):
        """
        Returns list of items currently being left behind
        """
        return [item for item, is_leaving in leaving_flags.items() if is_leaving]
