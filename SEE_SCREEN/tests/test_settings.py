"""
Settings panel interactions.
"""

import json
import pytest


class TestSettingsToggle:
    """Opening and closing the settings panel."""

    def test_settings_starts_hidden(self, app):
        assert not app.settings_visible

    def test_toggle_opens_settings(self, app):
        app._toggle_settings()
        assert app.settings_visible

    def test_toggle_closes_settings(self, app):
        app._toggle_settings()
        app._toggle_settings()
        assert not app.settings_visible

    def test_toggle_three_times_ends_open(self, app):
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        assert app.settings_visible

    def test_toggle_four_times_ends_closed(self, app):
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        assert not app.settings_visible

    def test_repeated_toggle_50_times(self, app):
        for i in range(50):
            app._toggle_settings()
            expected = (i % 2 == 0)
            assert app.settings_visible == expected, f"Failed at i={i}"


class TestSizeChanges:
    """Changing the overlay size."""

    def test_smallest_size(self, app):
        app.preview_size = 100
        assert app.preview_size == 100

    def test_largest_size(self, app):
        app.preview_size = 500
        assert app.preview_size == 500

    def test_size_saves_immediately(self, app):
        app.preview_size = 200
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 200

    def test_size_100_roundtrip(self, app):
        app.preview_size = 100
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 100

    def test_size_200_roundtrip(self, app):
        app.preview_size = 200
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 200

    def test_size_300_roundtrip(self, app):
        app.preview_size = 300
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 300

    def test_size_400_roundtrip(self, app):
        app.preview_size = 400
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 400

    def test_all_sizes_roundtrip(self, app):
        sizes = [50, 100, 150, 200, 250, 300, 400, 500]
        for s in sizes:
            app.preview_size = s
            app.save_settings()
            from conftest import make_app
            app2 = make_app()
            app2.settings_file = app.settings_file
            app2.load_settings()
            assert app2.preview_size == s

    def test_size_change_preserves_zoom_and_position(self, app):
        app.preview_size = 200
        app.zoom = 2.0
        app.position = "top-left"
        app._on_size_change()
        assert app.zoom == 2.0
        assert app.position == "top-left"


class TestPositionChanges:
    """Changing the position preset."""

    def test_top_right(self, app):
        app.position = "top-right"
        assert app.position == "top-right"

    def test_top_left(self, app):
        app.position = "top-left"
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.position == "top-left"

    def test_bottom_right(self, app):
        app.position = "bottom-right"
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.position == "bottom-right"

    def test_bottom_left(self, app):
        app.position = "bottom-left"
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.position == "bottom-left"

    def test_all_four_positions(self, app):
        for pos in ["bottom-left", "bottom-right", "top-left", "top-right"]:
            app.position = pos
            assert app.position == pos

    def test_unknown_position_preset(self, app):
        app.position = "center-of-universe"
        app._update_position()
        assert app.window_x is not None

    def test_position_change_preserves_size_and_zoom(self, app):
        app.preview_size = 150
        app.zoom = 1.5
        app.position = "bottom-left"
        app._on_position_change()
        assert app.preview_size == 150
        assert app.zoom == 1.5


class TestZoomChanges:
    """Changing the zoom level."""

    def test_zoom_to_2x(self, app):
        app.zoom = 2.0
        assert app.zoom == 2.0

    def test_zoom_to_05x(self, app):
        app.zoom = 0.5
        assert app.zoom == 0.5

    def test_zoom_survives_restart(self, app):
        app.zoom = 2.0
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.zoom == 2.0

    def test_zoom_025_roundtrip(self, app):
        app.zoom = 0.25
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.zoom == 0.25

    def test_all_zoom_levels_work(self, app):
        steps = [0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.0, 4.0]
        for z in steps:
            app.zoom = z
            assert app.zoom == z

    def test_all_zoom_levels_roundtrip(self, app):
        steps = [0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.0, 4.0]
        for z in steps:
            app.zoom = z
            app.save_settings()
            from conftest import make_app
            app2 = make_app()
            app2.settings_file = app.settings_file
            app2.load_settings()
            assert abs(app2.zoom - z) < 0.01

    def test_zoom_to_4x_then_back_to_1x(self, app):
        app.zoom = 4.0
        app.zoom = 1.0
        assert app.zoom == 1.0

    def test_zoom_to_025_then_back_to_1x(self, app):
        app.zoom = 0.25
        app.zoom = 1.0
        assert app.zoom == 1.0

    def test_zoom_change_preserves_size_and_position(self, app):
        app.preview_size = 150
        app.position = "top-right"
        app.zoom = 1.0
        app._on_zoom_change()
        assert app.preview_size == 150
        assert app.position == "top-right"


class TestSettingsAndOverlay:
    """Interaction between settings panel and overlay behavior."""

    def test_hide_while_settings_open(self, app):
        app._toggle_settings()
        assert app.settings_visible
        app._hidden_by_us = True
        app._hide_area = (10, 760, 310, 310)
        assert app._hidden_by_us

    def test_drag_with_settings_open(self, app):
        app._toggle_settings()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        assert app.settings_visible
        assert app.window_x == 500 + 24 - 310

    def test_close_settings_after_drag(self, app):
        app._toggle_settings()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app._toggle_settings()
        assert not app.settings_visible
        with open(app.settings_file) as f:
            d = json.load(f)
        assert "window_x" in d
