"""
Multi-monitor scenarios.
"""

import pytest


class TestMonitorSelection:
    """Selecting the correct monitor based on cursor position."""

    def test_cursor_on_primary_returns_primary(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(100, 500)
        assert m["left"] == 0

    def test_cursor_on_secondary_returns_secondary(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(2000, 500)
        assert m["left"] == 1920

    def test_three_monitors_left_to_right(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 3840, "top": 0, "width": 1920, "height": 1080},
        ]
        for mx, expected_left in [(100, 0), (2000, 1920), (4000, 3840)]:
            m = app._get_current_monitor(mx, 500)
            assert m["left"] == expected_left

    def test_vertical_stack(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 1080, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(500, 1500)
        assert m["top"] == 1080

    def test_different_resolutions(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 3840, "height": 2160},
        ]
        m = app._get_current_monitor(2000, 100)
        assert m["left"] == 1920

    def test_ultrawide_monitor(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 3440, "height": 1440}]
        m = app._get_current_monitor(2000, 500)
        assert m["width"] == 3440

    def test_cursor_outside_all_monitors_falls_back(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        m = app._get_current_monitor(50000, 50000)
        assert m["left"] == 0

    def test_cursor_on_first_pixel(self, app):
        m = app._get_current_monitor(0, 0)
        assert m["left"] == 0

    def test_cursor_on_last_pixel(self, app):
        m = app._get_current_monitor(1919, 1079)
        assert m["left"] == 0

    def test_cursor_at_monitor_boundary_secondary(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(1920, 500)
        assert m["left"] == 1920


class TestMonitorArrangementChanges:
    """Reconfiguring monitors at runtime."""

    def test_add_second_monitor_right(self, app):
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        app.load_settings()
        assert app.window_x == 500

    def test_remove_second_monitor(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        app.window_x = 100
        app.window_y = 100
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2._monitors = app._monitors
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.window_x == 100

    def test_position_on_disconnected_monitor_auto_places(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        assert not app._overlaps_any_monitor(3000, 500, 310, 310)

    def test_laptop_dock_undock_position_falls_back(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        assert not app._overlaps_any_monitor(1500, 500, 310, 310)

    def test_laptop_docked_smaller_monitor(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        assert app._overlaps_any_monitor(300, 300, 310, 310)


class TestComplexMultiMonitor:
    """More complex multi-monitor arrangements."""

    def test_four_monitors_grid(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 1080, "width": 1920, "height": 1080},
            {"left": 1920, "top": 1080, "width": 1920, "height": 1080},
        ]
        tests = [(100, 100), (2000, 100), (100, 1500), (2000, 1500)]
        for mx, my in tests:
            m = app._get_current_monitor(mx, my)
            assert m is not None

    def test_cursor_in_gap_between_monitors(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1940, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(1930, 500)
        # Falls back to first monitor
        assert m is not None

    def test_monitor_with_gap_overlap_check(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 2000, "top": 0, "width": 1920, "height": 1080},
        ]
        assert not app._overlaps_any_monitor(1950, 500, 10, 10)
        assert app._overlaps_any_monitor(100, 500, 310, 310)

    def test_mixed_portrait_landscape(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1080, "height": 1920},
        ]
        m = app._get_current_monitor(2500, 500)
        assert m["width"] == 1080
        assert m["height"] == 1920

    def test_negative_coordinates_monitor(self, app):
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        m = app._get_current_monitor(-1000, 500)
        assert m["left"] == -1920

    def test_overlap_with_negative_monitor(self, app):
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        assert app._overlaps_any_monitor(-1900, 100, 100, 100)
        assert not app._overlaps_any_monitor(-2000, 100, 10, 10)
