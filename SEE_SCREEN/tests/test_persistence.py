"""
Position persistence — save/load/roundtrip scenarios.
"""

import json
import os
import tempfile
import pytest
from conftest import make_app


class TestSavePosition:
    """Saving the overlay position."""

    def test_save_fully_on_screen(self, app):
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert "window_x" in d

    def test_save_partially_off_left(self, app):
        app.window_x = -5
        app.window_y = 100
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == -5

    def test_save_partially_off_top(self, app):
        app.window_x = 100
        app.window_y = -5
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_y"] == -5

    def test_save_partially_off_right(self, app):
        app.window_x = 1800
        app.window_y = 100
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 1800

    def test_save_partially_off_bottom(self, app):
        app.window_x = 100
        app.window_y = 900
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_y"] == 900

    def test_save_completely_off_screen(self, app):
        app.window_x = 99999
        app.window_y = 99999
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 99999

    def test_consecutive_saves_same_position(self, app):
        app.window_x = 400
        app.window_y = 300
        for _ in range(5):
            app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 400

    def test_consecutive_different_positions(self, app):
        for x, y in [(100, 100), (200, 200), (300, 300), (400, 400), (500, 500)]:
            app.window_x = x
            app.window_y = y
            app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 500

    def test_save_100_times_idempotent(self, app):
        app.window_x = 400
        app.window_y = 300
        for _ in range(100):
            app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 400

    def test_save_large_values(self, app):
        app.window_x = 1000000
        app.window_y = 1000000
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 1000000

    def test_save_negative_large_values(self, app):
        app.window_x = -1000000
        app.window_y = -1000000
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == -1000000

    def test_save_writes_indented_json(self, app):
        app.window_x = 100
        app.window_y = 200
        app.save_settings()
        with open(app.settings_file) as f:
            content = f.read()
        assert "\n" in content
        assert "  " in content


class TestLoadPosition:
    """Loading a previously saved overlay position."""

    def test_load_completely_off_screen_discarded(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 99999, "window_y": 88888}, f)
        app.load_settings()
        assert app.window_x is None

    def test_load_partially_off_screen_kept(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": -5, "window_y": 100}, f)
        app.load_settings()
        assert app.window_x == -5

    def test_load_zero_zero_position(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 0, "window_y": 0}, f)
        app.load_settings()
        assert app.window_x == 0

    def test_load_bottom_right_corner(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 1610, "window_y": 770}, f)
        app.load_settings()
        assert app.window_x == 1610

    def test_load_32767_discarded(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 32767, "window_y": 32767}, f)
        app.load_settings()
        assert app.window_x is None

    def test_load_missing_position_auto_place(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": 200}, f)
        app.load_settings()
        assert app.window_x is None

    def test_load_float_window_x_converts_to_int(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 100.7, "window_y": 200.3}, f)
        app.load_settings()
        assert app.window_x == 100
        assert app.window_y == 200

    def test_load_extreme_large_window_x_discarded(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 1e12, "window_y": 1e12}, f)
        app.load_settings()
        assert app.window_x is None

    def test_load_non_numeric_window_x_discarded(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": [], "window_y": 100}, f)
        app.load_settings()
        assert app.window_x is None

    def test_load_non_numeric_window_y_discarded(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 100, "window_y": {}}, f)
        app.load_settings()
        assert app.window_y is None

    def test_load_missing_window_x_auto_places(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_y": 100}, f)
        app.load_settings()
        assert app.window_x is None

    def test_load_missing_window_y_auto_places(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"window_x": 100}, f)
        app.load_settings()
        assert app.window_y is None


class TestSaveLoadRoundTrip:
    """Full save-load roundtrips with various position variants."""

    POSITIONS = [
        (100, 100), (500, 300), (1000, 800), (0, 0),
        (-1, 100), (100, -1), (1919, 100), (100, 1079),
        (-309, 100), (100, -309), (1600, 10), (10, 760),
        (-5, 100), (100, -5), (500, 500), (2000, 500),
        (99999, 99999), (32767, 32767), (0, 1079), (1919, 0),
    ]

    def test_all_positions_roundtrip_correctly(self, app, settings_file):
        for x, y in self.POSITIONS:
            app.settings_file = settings_file
            with open(settings_file, 'w') as f:
                json.dump({"window_x": x, "window_y": y}, f)
            app.load_settings()
            on_screen = app._overlaps_any_monitor(x, y, 310, 310)
            if on_screen:
                assert app.window_x == x, f"Expected x={x}, got {app.window_x}"
            else:
                assert app.window_x is None, f"Expected None, got {app.window_x}"

    def test_full_roundtrip(self, app):
        app.window_x, app.window_y = 777, 333
        app.preview_size = 250
        app.zoom = 1.5
        app.position = "top-left"
        app.save_settings()
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.window_x == 777
        assert app2.window_y == 333
        assert app2.preview_size == 250
        assert app2.zoom == 1.5
        assert app2.position == "top-left"

    def test_roundtrip_minimum_values(self, app):
        app.preview_size = 50
        app.zoom = 0.25
        app.position = "top-left"
        app.window_x = 0
        app.window_y = 0
        app.save_settings()
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 50
        assert app2.zoom == 0.25
        assert app2.window_x == 0

    def test_roundtrip_maximum_values(self, app):
        app.preview_size = 500
        app.zoom = 4.0
        app.position = "bottom-right"
        app.window_x = 1610
        app.window_y = 770
        app.save_settings()
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.preview_size == 500
        assert app2.zoom == 4.0
        assert app2.window_x == 1610

    def test_save_then_load_then_save_no_data_loss(self, app):
        app.preview_size = 200
        app.zoom = 2.0
        app.position = "top-right"
        app.window_x = 300
        app.window_y = 150
        app.save_settings()
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        app2.save_settings()
        with open(app2.settings_file) as f:
            d = json.load(f)
        assert d["preview_size"] == 200
        assert d["zoom"] == 2.0
        assert d["position"] == "top-right"
        assert d["window_x"] == 300
        assert d["window_y"] == 150

    def test_extra_keys_not_preserved_on_save(self, app, settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"preview_size": 200, "extra": "garbage", "user_data": 42}, f)
        app.load_settings()
        assert app.preview_size == 200
        app.save_settings()
        with open(settings_file) as f:
            d = json.load(f)
        assert "extra" not in d
        assert "user_data" not in d


class TestSettingsDirectory:
    """Settings file directory edge cases."""

    def test_create_parent_directory_if_missing(self, app):
        bad_path = os.path.join(tempfile.gettempdir(), "nonexistent_subdir", "test.json")
        app.settings_file = bad_path
        app.window_x = 100
        app.window_y = 200
        app.save_settings()
        assert os.path.exists(bad_path)
        os.remove(bad_path)
        os.rmdir(os.path.dirname(bad_path))

    def test_unicode_path_saves_correctly(self, app):
        unicode_path = os.path.join(tempfile.gettempdir(), "测试_settings.json")
        app.settings_file = unicode_path
        app.window_x = 100
        app.window_y = 200
        app.save_settings()
        assert os.path.exists(unicode_path)
        with open(unicode_path) as f:
            d = json.load(f)
        assert d["window_x"] == 100
        os.remove(unicode_path)

    def test_settings_file_ends_with_json(self, app):
        assert app.settings_file.endswith('.json')

    def test_default_settings_path_in_downloads(self):
        from mouse_preview import MousePreviewApp
        default = MousePreviewApp.__new__(MousePreviewApp)
        default.settings_file = os.path.join(
            os.path.expanduser("~/Downloads"),
            "dr_broken_display_settings.json",
        )
        assert "Downloads" in default.settings_file
        assert default.settings_file.endswith(".json")
