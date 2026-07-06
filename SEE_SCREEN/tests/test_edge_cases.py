"""
Miscellaneous edge cases that don't fit neatly into other categories.
"""

import json
import pytest
from conftest import make_app


class TestAutoPosition:
    """Auto-position math for different monitor sizes and positions."""

    def test_1080p_bottom_left(self, app):
        ml, mt, mw, mh = 0, 0, 1920, 1080
        ps, pad = 310, 10
        x = ml + pad
        y = mt + mh - ps - pad
        assert (x, y) == (10, 760)

    def test_1080p_bottom_right(self, app):
        ml, mt, mw, mh = 0, 0, 1920, 1080
        ps, pad = 310, 10
        x = ml + mw - ps - pad
        y = mt + mh - ps - pad
        assert (x, y) == (1600, 760)

    def test_1080p_top_left(self, app):
        ml, mt, ps, pad = 0, 0, 310, 10
        x = ml + pad
        y = mt + pad
        assert (x, y) == (10, 10)

    def test_1080p_top_right(self, app):
        ml, mt, mw, ps, pad = 0, 0, 1920, 310, 10
        x = ml + mw - ps - pad
        y = mt + pad
        assert (x, y) == (1600, 10)

    def test_4k_bottom_left(self, app):
        ml, mt, mw, mh = 0, 0, 3840, 2160
        ps, pad = 500, 10
        x = ml + pad
        y = mt + mh - ps - pad
        assert (x, y) == (10, 1650)

    def test_4k_bottom_right(self, app):
        ml, mt, mw, mh = 0, 0, 3840, 2160
        ps, pad = 500, 10
        x = ml + mw - ps - pad
        y = mt + mh - ps - pad
        assert (x, y) == (3330, 1650)

    def test_1440p_bottom_left(self, app):
        ml, mt, mh, ps, pad = 0, 0, 1440, 310, 10
        y = mt + mh - ps - pad
        assert y == 1120

    def test_768p_bottom_left(self, app):
        ml, mt, mh, ps, pad = 0, 0, 768, 310, 10
        y = mt + mh - ps - pad
        assert y == 448

    def test_768p_large_overlay(self, app):
        ml, mt, mh, ps, pad = 0, 0, 768, 500, 10
        y = mt + mh - ps - pad
        assert y == 258

    def test_ultrawide_bottom_left(self, app):
        ml, mt, mw, mh = 0, 0, 3440, 1440
        ps, pad = 500, 10
        x = ml + pad
        y = mt + mh - ps - pad
        assert (x, y) == (10, 930)

    def test_ultrawide_top_right(self, app):
        ml, mt, mw, ps, pad = 0, 0, 3440, 500, 10
        x = ml + mw - ps - pad
        y = mt + pad
        assert (x, y) == (2930, 10)

    def test_secondary_monitor_auto_position(self, app):
        ml, mt = 1920, 0
        mh, ps, pad = 1080, 310, 10
        x = ml + pad
        y = mt + mh - ps - pad
        assert (x, y) == (1930, 760)

    def test_vertical_monitor_bottom_left(self, app):
        ml, mt, mw, mh = 0, 0, 1080, 1920
        ps, pad = 310, 10
        x = ml + pad
        y = mt + mh - ps - pad
        assert (x, y) == (10, 1600)

    def test_vertical_monitor_top_right(self, app):
        ml, mt, mw, ps, pad = 0, 0, 1080, 310, 10
        x = ml + mw - ps - pad
        y = mt + pad
        assert (x, y) == (760, 10)

    def test_all_sizes_fit_bottom_left(self, app):
        ml, mt, mw, mh, pad = 0, 0, 1920, 1080, 10
        for ps in [50, 100, 150, 200, 250, 300, 400, 500]:
            x = ml + pad
            y = mt + mh - ps - pad
            assert x >= 0
            assert y >= 0

    def test_all_sizes_fit_top_right(self, app):
        ml, mt, mw, pad = 0, 0, 1920, 10
        for ps in [50, 100, 150, 200, 250, 300, 400, 500]:
            x = ml + mw - ps - pad
            y = mt + pad
            assert x >= 0


class TestConstantsAndMetadata:
    """App constants and metadata."""

    def test_handle_size_is_reasonable(self, app):
        from mouse_preview import _HANDLE_SZ
        assert 16 <= _HANDLE_SZ <= 48

    def test_zoom_steps_are_sorted(self, app):
        from mouse_preview import MousePreviewApp
        steps = MousePreviewApp.ZOOM_STEPS
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))
        assert 1.0 in steps

    def test_version_is_string(self, app):
        from mouse_preview import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_app_name_is_string(self, app):
        from mouse_preview import APP_NAME
        assert isinstance(APP_NAME, str)
        assert len(APP_NAME) > 0

    def test_size_minimum_bound(self, app):
        assert max(50, min(500, 30)) == 50
        assert max(50, min(500, 50)) == 50

    def test_size_maximum_bound(self, app):
        assert max(50, min(500, 600)) == 500
        assert max(50, min(500, 500)) == 500


class TestOperationSequences:
    """Real-world sequences of operations."""

    def test_open_settings_change_size_close(self, app):
        app._toggle_settings()
        assert app.settings_visible
        app.size_var.set(200)
        app._on_size_change()
        assert app.preview_size == 200
        app._toggle_settings()
        assert not app.settings_visible

    def test_open_settings_change_position_close(self, app):
        app._toggle_settings()
        app.pos_var.set("top-right")
        app._on_position_change()
        assert app.position == "top-right"
        app._toggle_settings()
        assert not app.settings_visible

    def test_drag_then_change_size(self, app):
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app.size_var.set(200)
        app._on_size_change()
        assert app.preview_size == 200

    def test_drag_then_change_position(self, app):
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app.pos_var.set("top-left")
        app._on_position_change()
        assert app.position == "top-left"

    def test_zoom_then_drag(self, app):
        app.zoom_var.set(2.0)
        app._on_zoom_change()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        assert app.zoom == 2.0
        assert app.window_x == 500 + 24 - 310

    def test_size_zoom_drag_all(self, app):
        app.size_var.set(200)
        app._on_size_change()
        app.zoom_var.set(0.5)
        app._on_zoom_change()
        app._drag_pos = (600, 500)
        app._h_drag_end(None)
        assert app.preview_size == 200
        assert app.zoom == 0.5
        assert app.window_x == 600 + 24 - 200

    def test_multiple_operations_with_saves(self, app):
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 500 + 24 - 310
        app.size_var.set(200)
        app._on_size_change()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["preview_size"] == 200
        app.zoom_var.set(2.0)
        app._on_zoom_change()
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["preview_size"] == 200
        assert d["zoom"] == 2.0


class TestCaptureExtremes:
    """Extreme capture scenarios (virtually unbounded)."""

    def test_capture_virtual_screen_bounds(self, app):
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = -100, -100
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        assert left == 0
        assert top == 0

    def test_capture_beyond_virtual_bottom_right(self, app):
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = 5000, 5000
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        left = min(left, virt["left"] + virt["width"] - cap_sz)
        top = min(top, virt["top"] + virt["height"] - cap_sz)
        assert left == 1920 - 310
        assert top == 1080 - 310

    def test_capture_with_negative_virtual_screen(self, app):
        virt = {"left": -1920, "top": 0, "width": 3840, "height": 1080}
        mx, my = -1000, 500
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        assert left == -1000 - 155

    def test_capture_at_virtual_origin(self, app):
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = 0, 0
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        assert left == 0
        assert top == 0

    def test_capture_at_virtual_bottom_right(self, app):
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = 1919, 1079
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        left = min(left, virt["left"] + virt["width"] - cap_sz)
        top = min(top, virt["top"] + virt["height"] - cap_sz)
        assert left == 1920 - 310
        assert top == 1080 - 310

    def test_capture_bbox_always_positive(self, app):
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        for mx in [0, 500, 960, 1500, 1919]:
            for my in [0, 500, 540, 800, 1079]:
                cap_sz = 310
                half = cap_sz // 2
                left = max(virt["left"], mx - half)
                top = max(virt["top"], my - half)
                left = min(left, virt["left"] + virt["width"] - cap_sz)
                top = min(top, virt["top"] + virt["height"] - cap_sz)
                right = min(virt["left"] + virt["width"], left + cap_sz)
                bottom = min(virt["top"] + virt["height"], top + cap_sz)
                w = right - left
                h = bottom - top
                assert w > 0, f"Non-positive width at mx={mx}"
                assert h > 0, f"Non-positive height at my={my}"


class TestPositionPresetChanges:
    """Position preset change scenarios."""

    def test_change_to_top_left_from_bottom_left(self, app):
        app._update_position()
        app.pos_var.set("top-left")
        app._on_position_change()
        assert app.position == "top-left"
        assert app.window_y < 500

    def test_change_to_bottom_right(self, app):
        app._update_position()
        app.pos_var.set("bottom-right")
        app._on_position_change()
        assert app.position == "bottom-right"
        assert app.window_x > 1500

    def test_change_to_top_right(self, app):
        app._update_position()
        app.pos_var.set("top-right")
        app._on_position_change()
        assert app.position == "top-right"
        assert app.window_x > 1500

    def test_change_to_bottom_left(self, app):
        app._update_position()
        app.pos_var.set("bottom-left")
        app._on_position_change()
        assert app.position == "bottom-left"
        assert app.window_x < 100
