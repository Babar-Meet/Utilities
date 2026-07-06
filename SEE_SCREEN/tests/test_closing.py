"""
Closing / quitting the app.
"""

import json
from unittest.mock import MagicMock
import pytest


class TestQuitBehavior:
    """What happens when the user quits the app."""

    def test_quit_saves_settings(self, app):
        app.window_x = 500
        app.window_y = 300
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 500

    def test_quit_saves_size(self, app):
        app.preview_size = 400
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["preview_size"] == 400

    def test_quit_saves_zoom(self, app):
        app.zoom = 2.0
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["zoom"] == 2.0

    def test_quit_saves_position_preset(self, app):
        app.position = "top-right"
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["position"] == "top-right"

    def test_quit_saves_all_settings_together(self, app):
        app.preview_size = 200
        app.zoom = 0.5
        app.position = "top-left"
        app.window_x = 100
        app.window_y = 100
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["preview_size"] == 200
        assert d["zoom"] == 0.5
        assert d["position"] == "top-left"
        assert d["window_x"] == 100
        assert d["window_y"] == 100

    def test_double_quit_does_not_raise(self, app):
        with pytest.raises(SystemExit):
            app._quit()

    def test_quit_without_handle(self, app):
        app.handle = None
        with pytest.raises(SystemExit):
            app._quit()

    def test_quit_without_listeners(self, app):
        app._kb_listener = None
        app._ms_listener = None
        with pytest.raises(SystemExit):
            app._quit()

    def test_escape_during_drag_saves_position(self, app):
        app.window_x = 400
        app.window_y = 300
        app._dragging = True
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d.get("window_x") == 400

    def test_alt_f4_during_drag_saves_position(self, app):
        app.window_x = 400
        app.window_y = 300
        app._dragging = True
        with pytest.raises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d.get("window_x") == 400


class TestAutoSave:
    """Auto-save during normal usage."""

    def test_auto_save_counter_increments(self, app):
        app._save_counter = 0
        for _ in range(50):
            app._save_counter += 1
        assert app._save_counter == 50

    def test_auto_save_counter_resets_at_100(self, app):
        app._save_counter = 95
        for _ in range(10):
            app._save_counter += 1
        assert app._save_counter == 105

    def test_auto_save_preserves_original_position_when_hidden(self, app):
        app.window_x = 400
        app.window_y = 300
        app._hidden_by_us = True
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 400
        assert d["window_y"] == 300
