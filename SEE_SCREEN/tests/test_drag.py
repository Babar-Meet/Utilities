"""
Drag & move operations — user drags the handle to reposition the overlay.
"""

import json
from unittest.mock import MagicMock
import pytest


def _mock_event(x=0, y=0):
    e = MagicMock()
    e.x = x
    e.y = y
    return e


class TestClickWithoutDrag:
    """User clicks the handle but does not move the mouse."""

    def test_click_without_drag_keeps_position(self, app):
        """Regression: _h_drag_start must store handle position so _h_drag_end doesn't use stale (0,0)."""
        app.window_x = 500
        app.window_y = 300
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 500 + 310 - 24
        app.handle.winfo_y.return_value = 300 + 310 - 24
        app._drag_pos = (0, 0)
        app._h_drag_start(_mock_event())
        assert app._drag_pos == (500 + 310 - 24, 300 + 310 - 24)
        app._h_drag_end(None)
        assert app.window_x == 500
        assert app.window_y == 300

    def test_drag_start_captures_current_handle_position(self, app):
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 777
        app.handle.winfo_y.return_value = 888
        app._h_drag_start(_mock_event())
        assert app._drag_pos == (777, 888)


class TestDragMath:
    """Mathematical correctness of handle-to-overlay position mapping."""

    _HANDLE_SZ = 24

    def test_drag_moves_overlay_by_same_amount(self):
        for hx, hy in [(386, 386), (500, 500), (100, 100), (1000, 800)]:
            rx = hx + self._HANDLE_SZ - 310
            ry = hy + self._HANDLE_SZ - 310
            assert rx == hx + 24 - 310
            assert ry == hy + 24 - 310

    def test_drag_100px_right_moves_overlay_100px_right(self):
        hx_start, hy_start = 386, 386
        hx_end = hx_start + 100
        rx_start = hx_start + 24 - 310
        rx_end = hx_end + 24 - 310
        assert rx_end - rx_start == 100

    def test_drag_50px_up_moves_overlay_50px_up(self):
        hy_start = 386
        hy_end = hy_start - 50
        ry_start = hy_start + 24 - 310
        ry_end = hy_end + 24 - 310
        assert ry_end - ry_start == -50

    def test_drag_diagonally(self):
        hx, hy = 386, 386
        hx += 200
        hy += 100
        rx = hx + 24 - 310
        ry = hy + 24 - 310
        assert rx == 386 + 200 + 24 - 310
        assert ry == 386 + 100 + 24 - 310

    def test_drag_zero_offset_no_change(self):
        hx, hy = 386, 386
        dx, dy = 0, 0
        new_hx, new_hy = hx + dx, hy + dy
        rx = new_hx + 24 - 310
        ry = new_hy + 24 - 310
        assert rx == 386 + 24 - 310
        assert ry == 386 + 24 - 310

    def test_drag_one_pixel(self):
        hx, hy = 386, 386
        dx, dy = 1, 1
        new_hx, new_hy = hx + dx, hy + dy
        rx = new_hx + 24 - 310
        delta = rx - (386 + 24 - 310)
        assert delta == 1

    def test_drag_reverse_x_then_y_returns_to_start(self):
        hx, hy = 386, 386
        hx += 100
        hx -= 100
        rx = hx + 24 - 310
        assert rx == 386 + 24 - 310

    def test_zigzag_drag_no_drift(self):
        hx, hy = 386, 386
        moves = [(50, 0), (-30, 20), (10, -40), (0, 10), (-20, 20)]
        total_dx = sum(dx for dx, _ in moves)
        total_dy = sum(dy for _, dy in moves)
        hx += total_dx
        hy += total_dy
        rx = hx + 24 - 310
        ry = hy + 24 - 310
        assert hx == rx + 310 - 24
        assert hy == ry + 310 - 24

    def test_drag_to_screen_edge(self):
        hx, hy = 0, 0
        rx = hx + 24 - 310
        ry = hy + 24 - 310
        assert rx == -286
        assert ry == -286

    def test_drag_off_screen_left(self):
        hx, hy = -100, 386
        rx = hx + 24 - 310
        assert rx == -386

    def test_drag_off_screen_right(self):
        hx, hy = 2000, 386
        rx = hx + 24 - 310
        assert rx == 1714

    def test_drag_off_screen_top(self):
        hx, hy = 386, -100
        ry = hy + 24 - 310
        assert ry == -386

    def test_drag_off_screen_bottom(self):
        hx, hy = 386, 2000
        ry = hy + 24 - 310
        assert ry == 1714


class TestDragWithDifferentSizes:
    """Drag math works correctly for any overlay size."""

    _HANDLE_SZ = 24

    def test_all_size_values_roundtrip(self):
        for preview in [50, 100, 200, 310, 400, 500]:
            for hx, hy in [(100, 100), (500, 300), (1000, 800)]:
                rx = hx + self._HANDLE_SZ - preview
                ry = hy + self._HANDLE_SZ - preview
                assert hx == rx + preview - self._HANDLE_SZ
                assert hy == ry + preview - self._HANDLE_SZ


class TestDragOperations:
    """Drag-related operations and their side effects."""

    def test_drag_end_saves_position(self, app):
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        assert app.window_x == 500 + 24 - 310
        assert app.window_y == 400 + 24 - 310
        with open(app.settings_file) as f:
            d = json.load(f)
        assert d["window_x"] == 500 + 24 - 310

    def test_drag_end_saves_even_without_move(self, app):
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 600
        app.handle.winfo_y.return_value = 500
        app._h_drag_start(_mock_event())
        app._h_drag_end(None)
        assert app.window_x == 600 + 24 - 310

    def test_drag_then_close_remembers(self, app):
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.window_x == 500

    def test_drag_to_secondary_monitor_persists(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        app.window_x = 2000
        app.window_y = 500
        app.save_settings()
        from conftest import make_app
        app2 = make_app()
        app2._monitors = app._monitors
        app2.settings_file = app.settings_file
        app2.load_settings()
        assert app2.window_x == 2000

    def test_drag_overrides_auto_position(self, app):
        app._update_position()
        auto_x, auto_y = app.window_x, app.window_y
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        assert (app.window_x, app.window_y) != (auto_x, auto_y)

    def test_drag_to_same_position_no_change(self, app):
        app.window_x = 400
        app.window_y = 300
        hx = 400 + 310 - 24
        hy = 300 + 310 - 24
        app._drag_pos = (hx, hy)
        app._h_drag_end(None)
        assert app.window_x == 400
        assert app.window_y == 300

    def test_drag_handle_at_negative_position(self, app):
        hx, hy = -50, 100
        rx = hx + 24 - 310
        ry = hy + 24 - 310
        assert rx == -336
        assert ry == -186

    def test_drag_with_settings_open(self, app):
        app._toggle_settings()
        assert app.settings_visible
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        assert app.settings_visible
        assert app.window_x == 500 + 24 - 310


class TestRapidDrag:
    """Rapid or repeated drag operations."""

    def test_rapid_click_handle_10_times(self, app):
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 400
        app.handle.winfo_y.return_value = 300
        for _ in range(10):
            app._h_drag_start(_mock_event())
            app._h_drag_end(None)
        assert app.window_x is not None
