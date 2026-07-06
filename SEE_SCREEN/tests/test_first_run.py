"""
First-run / fresh-install scenarios.
"""

import json
import pytest
from conftest import make_app


class TestFirstRunDefaults:
    """What happens when a user runs the app for the very first time."""

    def test_load_settings_returns_defaults_when_no_file(self, app):
        app.load_settings()
        assert app.window_x is None
        assert app.preview_size == 310
        assert app.zoom == 1.0
        assert app.position == "bottom-left"

    def test_no_crash_when_settings_file_missing(self, app):
        app.load_settings()
        assert app.preview_size == 310

    def test_no_crash_on_corrupt_settings(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("}}}}corrupted{{{{")
        app.load_settings()
        assert app.preview_size == 310

    def test_empty_json_object_uses_defaults(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("{}")
        app.load_settings()
        assert app.preview_size == 310
        assert app.zoom == 1.0
        assert app.position == "bottom-left"

    def test_partial_settings_defaults_remaining(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"zoom": 2.0}, f)
        app.load_settings()
        assert app.zoom == 2.0
        assert app.preview_size == 310
        assert app.position == "bottom-left"

    def test_unknown_keys_are_ignored(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": 200, "unexpected": "garbage"}, f)
        app.load_settings()
        assert app.preview_size == 200

    def test_negative_preview_size_clamped_to_minimum(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": -100}, f)
        app.load_settings()
        assert app.preview_size == 50

    def test_huge_preview_size_capped_at_maximum(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": 99999}, f)
        app.load_settings()
        assert app.preview_size == 500

    def test_string_preview_size_falls_back_to_default(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": "huge"}, f)
        app.load_settings()
        assert app.preview_size == 310

    def test_float_preview_size_converted_to_int(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": 200.7}, f)
        app.load_settings()
        assert app.preview_size == 200

    def test_zoom_zero_falls_back_to_one(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"zoom": 0}, f)
        app.load_settings()
        assert app.zoom == 1.0

    def test_zoom_negative_falls_back_to_one(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"zoom": -2.0}, f)
        app.load_settings()
        assert app.zoom == 1.0

    def test_zoom_string_falls_back_to_one(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"zoom": "2x"}, f)
        app.load_settings()
        assert app.zoom == 1.0

    def test_window_x_as_string_discarded(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": "left", "window_y": 100}, f)
        app.load_settings()
        assert app.window_x is None

    def test_window_y_as_float_converted_to_int(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 100, "window_y": 200.9}, f)
        app.load_settings()
        assert app.window_y == 200

    def test_auto_position_saves_position_to_disk(self, app):
        app._update_position()
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert "window_x" in d
        assert "window_y" in d

    def test_position_survives_restart(self, app):
        app.window_x, app.window_y = 500, 300
        app.save_settings()
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.window_x == 500
        assert app2.window_y == 300

    def test_empty_settings_file_does_not_crash(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("")
        app.load_settings()
        assert app.preview_size == 310

    def test_json_array_in_settings_does_not_crash(self, app, settings_file):
        with open(settings_file, 'w') as f:
            f.write("[1, 2, 3]")
        app.load_settings()
        assert app.preview_size == 310

    def test_null_values_fallback_to_defaults(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": None, "zoom": None, "position": None}, f)
        app.load_settings()
        assert app.preview_size == 310
        assert app.zoom == 1.0
        assert app.position == "bottom-left"
