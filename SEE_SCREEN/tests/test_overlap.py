"""
Comprehensive overlap detection tests.
"""

import pytest


class TestBasicOverlap:
    """Basic overlap scenarios with a single 1080p monitor."""

    def test_fully_inside(self, app):
        assert app._overlaps_any_monitor(100, 100, 310, 310)

    def test_at_origin(self, app):
        assert app._overlaps_any_monitor(0, 0, 310, 310)

    def test_at_bottom_right(self, app):
        assert app._overlaps_any_monitor(1610, 770, 310, 310)

    def test_small_window(self, app):
        assert app._overlaps_any_monitor(500, 300, 100, 100)

    def test_at_default_position(self, app):
        assert app._overlaps_any_monitor(10, 760, 310, 310)

    def test_at_top_right(self, app):
        assert app._overlaps_any_monitor(1600, 10, 310, 310)

    def test_entirely_off_left(self, app):
        assert not app._overlaps_any_monitor(-311, 100, 310, 310)

    def test_entirely_off_top(self, app):
        assert not app._overlaps_any_monitor(100, -311, 310, 310)

    def test_touch_left_edge(self, app):
        assert app._overlaps_any_monitor(-309, 100, 310, 310)

    def test_touch_top_edge(self, app):
        assert app._overlaps_any_monitor(100, -309, 310, 310)

    def test_off_screen_far_away(self, app):
        assert not app._overlaps_any_monitor(99999, 99999, 310, 310)

    def test_hidden_32767(self, app):
        assert not app._overlaps_any_monitor(32767, 32767, 310, 310)

    def test_extreme_positive(self, app):
        assert not app._overlaps_any_monitor(50000, 50000, 310, 310)

    def test_extreme_negative(self, app):
        assert not app._overlaps_any_monitor(-50000, 50000, 310, 310)

    def test_1px_touch_right(self, app):
        assert app._overlaps_any_monitor(1920, 0, 310, 310)

    def test_1px_touch_bottom(self, app):
        assert app._overlaps_any_monitor(0, 1080, 310, 310)

    def test_single_pixel_at_edge(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        assert app._overlaps_any_monitor(1919, 0, 1, 1)
        assert app._overlaps_any_monitor(0, 1079, 1, 1)
        assert app._overlaps_any_monitor(1920, 0, 1, 1)
        assert app._overlaps_any_monitor(0, 1080, 1, 1)


class TestOverlapWith1366x768:
    """Overlap on a smaller 1366x768 monitor (typical laptop)."""

    def test_inside(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        assert app._overlaps_any_monitor(100, 100, 310, 310)

    def test_outside_right(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        assert not app._overlaps_any_monitor(1400, 100, 310, 310)

    def test_touch_right_edge(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        assert app._overlaps_any_monitor(1366, 100, 310, 310)

    def test_touch_left_edge(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        assert app._overlaps_any_monitor(-309, 100, 310, 310)


class TestOverlapWithUltrawide:
    """Overlap on an ultrawide 3440x1440 monitor."""

    def test_inside(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 3440, "height": 1440}]
        assert app._overlaps_any_monitor(3000, 1000, 310, 310)

    def test_far_right(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 3440, "height": 1440}]
        assert not app._overlaps_any_monitor(4000, 1000, 310, 310)

    def test_touch_right_edge(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 3440, "height": 1440}]
        assert app._overlaps_any_monitor(3440, 1000, 310, 310)


class TestOverlapWith4K:
    """Overlap on a 4K 3840x2160 monitor."""

    def test_inside(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 3840, "height": 2160}]
        assert app._overlaps_any_monitor(3500, 1800, 310, 310)

    def test_outside_right(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 3840, "height": 2160}]
        assert not app._overlaps_any_monitor(4000, 1800, 310, 310)


class TestOverlapWithPortrait:
    """Overlap on a portrait 1080x1920 monitor."""

    def test_inside(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1080, "height": 1920}]
        assert app._overlaps_any_monitor(100, 1800, 100, 100)

    def test_outside_right(self, app):
        app._monitors = [{"left": 0, "top": 0, "width": 1080, "height": 1920}]
        assert not app._overlaps_any_monitor(1100, 100, 310, 310)


class TestOverlapWithNegativeCoords:
    """Overlap with monitors at negative coordinates."""

    def test_negative_left_monitor(self, app):
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        assert app._overlaps_any_monitor(-1900, 100, 300, 300)

    def test_outside_negative_monitor_left(self, app):
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        assert not app._overlaps_any_monitor(-2000, 100, 10, 10)

    def test_two_monitors_negative_and_positive(self, app):
        app._monitors = [
            {"left": -1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        assert app._overlaps_any_monitor(-1900, 100, 300, 300)
        assert app._overlaps_any_monitor(100, 100, 300, 300)


class TestExhaustiveOverlapGrid:
    """Exhaustive grid of cursor positions around a window boundary."""

    def test_grid_around_window(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        for mx in range(80, 420, 10):
            for my in range(80, 420, 10):
                inside = (wx <= mx <= wx + ww and wy <= my <= wy + wh)
                expected = (100 <= mx <= 400 and 100 <= my <= 400)
                assert inside == expected, f"Failed at mx={mx}, my={my}"

    def test_handle_grid(self, app):
        _HANDLE_SZ = 24
        hx, hy = 400, 400
        for mx in range(390, 430):
            for my in range(390, 430):
                on_handle = (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
                expected = (400 <= mx <= 424 and 400 <= my <= 424)
                assert on_handle == expected, f"Failed at mx={mx}, my={my}"

    def test_window_corners_inside(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        assert wx <= wx <= wx + ww and wy <= wy <= wy + wh
        assert wx <= wx + ww <= wx + ww and wy <= wy <= wy + wh
        assert wx <= wx <= wx + ww and wy <= wy + wh <= wy + wh
        assert wx <= wx + ww <= wx + ww and wy <= wy + wh <= wy + wh

    def test_window_corners_outside(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        assert not (wx <= wx - 1 <= wx + ww and wy <= wy - 1 <= wy + wh)
        assert not (wx <= wx + ww + 1 <= wx + ww and wy <= wy - 1 <= wy + wh)
        assert not (wx <= wx - 1 <= wx + ww and wy <= wy + wh + 1 <= wy + wh)
        assert not (wx <= wx + ww + 1 <= wx + ww and wy <= wy + wh + 1 <= wy + wh)

    def test_cursor_top_edge_boundary(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        assert wx <= 200 <= wx + ww and wy <= wy <= wy + wh
        assert not (wx <= 200 <= wx + ww and wy <= wy - 1 <= wy + wh)

    def test_cursor_left_edge_boundary(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        assert wx <= wx <= wx + ww and wy <= 200 <= wy + wh
        assert not (wx <= wx - 1 <= wx + ww and wy <= 200 <= wy + wh)

    def test_cursor_bottom_edge_boundary(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        assert wx <= 200 <= wx + ww and wy <= wy + wh <= wy + wh
        assert not (wx <= 200 <= wx + ww and wy + wh + 1 <= wy + wh + 1 <= wy + wh)

    def test_cursor_right_edge_boundary(self, app):
        wx, wy, ww, wh = 100, 100, 300, 300
        assert wx <= wx + ww <= wx + ww and wy <= 200 <= wy + wh
        assert not (wx + ww + 1 <= wx + ww + 1 <= wx + ww and wy <= 200 <= wy + wh)


class TestOverlapMultiMonitor:
    """Overlap across multiple monitors."""

    def test_window_spans_two_monitors(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        assert app._overlaps_any_monitor(1900, 500, 100, 100)

    def test_window_between_monitors_gap(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1940, "top": 0, "width": 1920, "height": 1080},
        ]
        assert not app._overlaps_any_monitor(1921, 500, 18, 100)

    def test_window_bridges_gap(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        assert app._overlaps_any_monitor(1919, 500, 2, 2)

    def test_exactly_touches_two(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        assert app._overlaps_any_monitor(1920, 500, 1, 1)
        assert app._overlaps_any_monitor(1919, 500, 2, 2)

    def test_window_in_gap_not_touching(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 100, "height": 100},
            {"left": 200, "top": 0, "width": 100, "height": 100},
        ]
        assert not app._overlaps_any_monitor(150, 0, 10, 10)

    def test_touches_only_first_monitor(self, app):
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        assert app._overlaps_any_monitor(100, 100, 310, 310)
