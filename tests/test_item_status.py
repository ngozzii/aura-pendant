"""Unit tests for core.item_status."""

from core.item_status import get_item_display_status, get_status


def test_with_you_status():
    assert get_status(-60) == "With You"


def test_moving_away_rssi_band():
    assert get_status(-75) == "Moving Away"


def test_left_behind_rssi_band():
    assert get_status(-90) == "Left Behind"


def test_missing_rssi_maps_to_with_you_not_not_seen():
    assert get_status(None) == "With You"


class MockItem:
    def __init__(self, state="WITH YOU", is_visible=True):
        self.state = state
        self.is_visible = is_visible


def test_left_behind_label():
    item = MockItem(state="LEFT BEHIND", is_visible=True)
    assert get_item_display_status(item) == "Left Behind"


def test_leaving_label():
    item = MockItem(state="LEAVING", is_visible=True)
    assert get_item_display_status(item) == "Moving Away"


def test_with_you_default_state():
    item = MockItem(state="WITH YOU", is_visible=True)
    assert get_item_display_status(item) == "With You"


def test_not_seen_tag_appended():
    item = MockItem(state="LEFT BEHIND", is_visible=False)
    assert get_item_display_status(item) == "Left Behind (Not Seen)"


def test_with_you_not_seen_tag():
    item = MockItem(state="WITH YOU", is_visible=False)
    assert get_item_display_status(item) == "With You (Not Seen)"
