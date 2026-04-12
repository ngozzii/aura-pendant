"""Unit tests for core.item_status."""

from core.item_status import get_item_display_status, get_status


def test_with_you_status():
    assert get_status(-60) == "With You"


def test_moving_away_status():
    assert get_status(-75) == "Moving Away"


def test_left_behind_rssi_status():
    assert get_status(-90) == "Left Behind"


def test_not_seen_status():
    assert get_status(None) == "Not Seen"


class MockItem:
    def __init__(self, state=None, last_rssi=None):
        self.state = state
        self.last_rssi = last_rssi


def test_left_behind_overrides():
    item = MockItem(state="LEFT BEHIND", last_rssi=-60)
    assert get_item_display_status(item) == "Left Behind"


def test_leaving_overrides():
    item = MockItem(state="LEAVING", last_rssi=-60)
    assert get_item_display_status(item) == "Moving Away"


def test_fallback_to_moving_away_rssi():
    item = MockItem(state=None, last_rssi=-75)
    assert get_item_display_status(item) == "Moving Away"
