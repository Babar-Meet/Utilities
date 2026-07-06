"""
Error recovery — how the app handles unexpected situations.
"""

import json
import pytest


class TestSettingsCorruption:
    """Malformed or corrupted settings files."""

    def test_corrupt_json_does_not_crash(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("}}}}broken{{{{")
        app.load_settings()
        assert app.preview_size == 310

    def test_empty_file_does_not_crash(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("")
        app.load_settings()
        assert app.preview_size == 310

    def test_json_array_does_not_crash(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("[1, 2, 3]")
        app.load_settings()
        assert app.preview_size == 310

    def test_null_values_use_defaults(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": None, "zoom": None}, f)
        app.load_settings()
        assert app.preview_size == 310
        assert app.zoom == 1.0

    def test_bool_preview_size_clamped(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": True}, f)
        app.load_settings()
        assert app.preview_size == 50

    def test_missing_file_is_fine(self, app):
        if hasattr(app, 'settings_file') and app.settings_file:
            import os
            if os.path.exists(app.settings_file):
                os.remove(app.settings_file)
        app.load_settings()
        assert app.preview_size == 310


class TestUIOperations:
    """UI operations that should not crash."""

    def test_double_right_click_no_break(self, app):
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        assert not app.settings_visible

    def test_rapid_setting_changes(self, app):
        for s in [100, 500, 200, 400, 300]:
            app.preview_size = s
            app.save_settings()
        assert app.preview_size == 300

    def test_preview_update_does_not_crash(self, app):
        app.photo = None
        app._preview_image_id = None
        try:
            app._update_preview()
        except Exception:
            pytest.fail("_update_preview raised unexpectedly")

    def test_mss_grab_mocked_works(self, app):
        app.sct.grab.return_value = type('Screenshot', (), {
            'size': (310, 310),
            'rgb': b'\xff' * (310 * 310 * 3)
        })()
        result = app.sct.grab((0, 0, 310, 310))
        assert result.size == (310, 310)


class TestOverlapEdgeCases:
    """Overlap check with extreme or invalid inputs."""

    def test_zero_width_returns_false(self, app):
        assert not app._overlaps_any_monitor(100, 100, 0, 310)

    def test_zero_height_returns_false(self, app):
        assert not app._overlaps_any_monitor(100, 100, 310, 0)

    def test_negative_size_returns_false(self, app):
        assert not app._overlaps_any_monitor(100, 100, -10, -10)

    def test_no_monitors_returns_false(self, app):
        app._monitors = []
        assert not app._overlaps_any_monitor(100, 100, 310, 310)

    def test_window_larger_than_monitor(self, app):
        assert app._overlaps_any_monitor(-500, -500, 3000, 3000)

    def test_window_1px_off_left_edge(self, app):
        assert app._overlaps_any_monitor(-1, 0, 310, 310)

    def test_window_1px_off_right_edge(self, app):
        assert app._overlaps_any_monitor(1920, 0, 310, 310)

    def test_window_1px_off_top_edge(self, app):
        assert app._overlaps_any_monitor(0, -1, 310, 310)

    def test_window_1px_off_bottom_edge(self, app):
        assert app._overlaps_any_monitor(0, 1080, 310, 310)

    def test_window_exactly_monitor_sized(self, app):
        assert app._overlaps_any_monitor(0, 0, 1920, 1080)

    def test_window_just_beyond_right(self, app):
        assert app._overlaps_any_monitor(1919, 0, 2, 1080)

    def test_infinity_sized_window(self, app):
        assert app._overlaps_any_monitor(-1e9, -1e9, 2e9, 2e9)

    def test_one_pixel_window(self, app):
        assert app._overlaps_any_monitor(500, 300, 1, 1)

    def test_window_outside_all_monitors(self, app):
        app._monitors = [{"left": 1920, "top": 0, "width": 1920, "height": 1080}]
        assert not app._overlaps_any_monitor(100, 100, 310, 310)
