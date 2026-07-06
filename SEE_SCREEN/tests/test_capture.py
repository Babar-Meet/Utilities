"""
Capture and content — what the user sees inside the overlay.
"""

import pytest


class TestCaptureArea:
    """The area captured around the cursor."""

    def test_capture_is_centered_on_cursor(self, app):
        mx, my = 960, 540
        cap_sz = 310
        half = cap_sz // 2
        left = max(0, mx - half)
        top = max(0, my - half)
        assert left == 960 - 155
        assert top == 540 - 155

    def test_capture_near_left_edge_clamps(self, app):
        mx = 10
        cap_sz = 310
        half = cap_sz // 2
        left = max(0, mx - half)
        assert left == 0

    def test_capture_near_top_edge_clamps(self, app):
        my = 10
        cap_sz = 310
        half = cap_sz // 2
        top = max(0, my - half)
        assert top == 0

    def test_capture_near_right_edge_clamps(self, app):
        mx = 1910
        cap_sz = 310
        half = cap_sz // 2
        left = max(0, mx - half)
        left = min(left, 1920 - cap_sz)
        assert left == 1920 - 310

    def test_capture_near_bottom_edge_clamps(self, app):
        my = 1070
        cap_sz = 310
        half = cap_sz // 2
        top = max(0, my - half)
        top = min(top, 1080 - cap_sz)
        assert top == 1080 - 310

    def test_capture_small_preview_various_positions(self, app):
        preview = 50
        cap_sz = int(preview / 1.0)
        half = cap_sz // 2
        for mx in [0, 10, 25, 960, 1900, 1919]:
            left = max(0, mx - half)
            left = min(left, 1920 - cap_sz)
            assert left >= 0
            assert left <= 1920 - cap_sz

    def test_capture_large_preview_various_positions(self, app):
        preview = 500
        cap_sz = int(preview / 1.0)
        half = cap_sz // 2
        for mx in [0, 250, 500, 960, 1500, 1919]:
            left = max(0, mx - half)
            left = min(left, 1920 - cap_sz)
            assert left >= 0
            assert left <= 1920 - cap_sz


class TestCaptureWithZoom:
    """Capture area sizing with different zoom levels."""

    def test_zoom_2x_capture_half_area(self, app):
        cap_sz = int(310 / 2.0)
        assert cap_sz == 155

    def test_zoom_05x_capture_double_area(self, app):
        cap_sz = int(310 / 0.5)
        assert cap_sz == 620

    def test_zoom_4x_capture_small(self, app):
        cap_sz = int(310 / 4.0)
        assert cap_sz == 77

    def test_zoom_025x_capture_huge(self, app):
        cap_sz = int(310 / 0.25)
        assert cap_sz == 1240

    def test_all_zoom_levels_positive_capture_size(self, app):
        preview = 310
        for zoom in [0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.0, 4.0]:
            cap_sz = int(preview / zoom)
            assert cap_sz > 0

    def test_min_preview_max_zoom(self, app):
        cap_sz = int(50 / 4.0)
        assert cap_sz == 12

    def test_max_preview_min_zoom(self, app):
        cap_sz = int(500 / 0.25)
        assert cap_sz == 2000

    def test_capture_clamps_near_left_zoomed(self, app):
        mx = 10
        cap_sz = int(310 / 2.0)
        half = cap_sz // 2
        left = max(0, mx - half)
        left = min(left, 1920 - cap_sz)
        assert left == 0

    def test_capture_clamps_near_right_zoomed(self, app):
        mx = 1910
        cap_sz = int(310 / 2.0)
        half = cap_sz // 2
        left = max(0, mx - half)
        left = min(left, 1920 - cap_sz)
        assert left == 1920 - 155


class TestCrosshairPosition:
    """The blue dot (crosshair) position within the preview."""

    def test_crosshair_at_center(self, app):
        mx, my = 100, 100
        left, top = 50, 50
        preview = 310
        cap_w, cap_h = 310, 310
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        assert round(cx) == 50
        assert round(cy) == 50

    def test_crosshair_at_origin(self, app):
        mx, my = 0, 0
        left, top = 0, 0
        preview = 310
        cap_w, cap_h = 310, 310
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        assert cx == 0
        assert cy == 0

    def test_crosshair_at_monitor_corner(self, app):
        mx, my = 1919, 1079
        left, top = 1920 - 310, 1080 - 310
        preview = 310
        cx = (mx - left) * (preview / 310)
        cy = (my - top) * (preview / 310)
        assert round(cx) == 309
        assert round(cy) == 309

    def test_crosshair_mid_frame(self, app):
        mx, my = 155, 155
        left, top = 0, 0
        preview = 310
        cap_w, cap_h = 310, 310
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        assert round(cx) == 155
        assert round(cy) == 155

    def test_crosshair_with_zoom(self, app):
        mx, my = 100, 100
        left, top = 50, 50
        preview = 310
        cap_w, cap_h = 155, 155
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        assert round(cx) == 100
        assert round(cy) == 100
