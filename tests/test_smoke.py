"""Sanity checks: imports and minimal behavior."""

from core.item_status import get_status


def test_core_import_path():
    assert get_status(-50) == "With You"
