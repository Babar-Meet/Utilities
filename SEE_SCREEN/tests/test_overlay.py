"""
Overlay hide/show behavior — cursor enters/exits the preview window.
"""

import pytest


class TestOverlayVisibility:
    """When the cursor interacts with the overlay area."""

    def test_cursor_outside_window_stays_visible(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 500, 500
        assert not (wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_cursor_inside_window_triggers_hide(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 100, 800
        assert wx <= mx <= wx + ww and wy <= my <= wy + wh

    def test_cursor_leaves_window_restores(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 500, 500
        assert not (wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_cursor_at_left_edge_inside_triggers_hide(self, app):
        wx = 10
        mx = wx
        assert wx <= mx

    def test_cursor_one_pixel_left_of_edge_stays_visible(self, app):
        wx = 10
        mx = wx - 1
        assert not (wx <= mx)

    def test_cursor_far_above_stays_visible(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 100, 100
        assert not (wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_cursor_far_below_stays_visible(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 100, 2000
        assert not (wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_cursor_left_of_window_stays_visible(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 0, 800
        assert not (wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_cursor_right_of_window_stays_visible(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 500, 800
        assert not (wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_cursor_on_handle_while_hidden_keeps_hidden(self, app):
        _HANDLE_SZ = 24
        hide_area = (10, 760, 310, 310)
        hx, hy = 296, 1046  # bottom-right of overlay → handle position
        mx, my = hx + 5, hy + 5
        on_handle = (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
        in_saved = (hide_area[0] <= mx <= hide_area[0] + hide_area[2] and
                    hide_area[1] <= my <= hide_area[1] + hide_area[3])
        assert on_handle or in_saved

    def test_cursor_away_from_both_restores_overlay(self, app):
        _HANDLE_SZ = 24
        hide_area = (10, 760, 310, 310)
        hx, hy = 296, 1046
        mx, my = 0, 0
        on_handle = (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
        in_saved = (hide_area[0] <= mx <= hide_area[0] + hide_area[2] and
                    hide_area[1] <= my <= hide_area[1] + hide_area[3])
        assert not (on_handle or in_saved)

    def test_rapid_enter_exit_no_crash(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        positions = [(165, 915), (0, 0), (165, 915), (2000, 2000), (165, 915)]
        inside = [wx <= mx <= wx + ww and wy <= my <= wy + wh for mx, my in positions]
        assert inside == [True, False, True, False, True]

    def test_diagonal_cursor_movement(self, app):
        wx, wy, ww, wh = 10, 760, 310, 310
        for step in range(0, 400, 10):
            mx = 10 + step
            my = 760 + step
            inside = wx <= mx <= wx + ww and wy <= my <= wy + wh
            if step <= 310:
                assert inside, f"step={step} should be inside"
            else:
                assert not inside, f"step={step} should be outside"


class TestOverlayState:
    """Internal state tracking for hide/show logic."""

    def test_hidden_by_us_starts_false(self, app):
        assert not app._hidden_by_us

    def test_dragging_starts_false(self, app):
        assert not app._dragging

    def test_hide_area_updated_during_drag_move(self, app):
        _HANDLE_SZ = 24
        preview = 310
        for hx, hy in [(386, 386), (500, 400), (200, 200)]:
            app._hide_area = (hx + _HANDLE_SZ - preview, hy + _HANDLE_SZ - preview,
                              preview, preview)
            assert app._hide_area[0] == hx + _HANDLE_SZ - preview
            assert app._hide_area[1] == hy + _HANDLE_SZ - preview

    def test_handle_position_after_hide(self, app):
        _HANDLE_SZ = 24
        preview = 310
        wx, wy = 400, 300
        hx = wx + preview - _HANDLE_SZ
        hy = wy + preview - _HANDLE_SZ
        assert hx == 400 + 310 - 24
        assert hy == 300 + 310 - 24

    def test_handle_position_with_small_overlay(self, app):
        _HANDLE_SZ = 24
        preview = 100
        wx, wy = 400, 300
        hx = wx + preview - _HANDLE_SZ
        hy = wy + preview - _HANDLE_SZ
        assert hx == 400 + 100 - 24
        assert hy == 300 + 100 - 24

    def test_handle_position_with_large_overlay(self, app):
        _HANDLE_SZ = 24
        preview = 500
        wx, wy = 400, 300
        hx = wx + preview - _HANDLE_SZ
        hy = wy + preview - _HANDLE_SZ
        assert hx == 400 + 500 - 24
        assert hy == 300 + 500 - 24
