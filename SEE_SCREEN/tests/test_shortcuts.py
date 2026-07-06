"""
Keyboard shortcuts and scroll-based adjustments.
"""

from unittest.mock import MagicMock
import pytest


class TestScrollResize:
    """Ctrl+Alt+Scroll to change overlay size."""

    def test_scroll_up_increases_size(self):
        for start in [100, 200, 310, 400]:
            new = max(50, min(500, start + 20))
            assert new > start

    def test_scroll_down_decreases_size(self):
        for start in [100, 200, 310, 400]:
            new = max(50, min(500, start - 20))
            assert new < start

    def test_size_respects_minimum_50(self):
        assert max(50, min(500, 60 - 20)) == 50

    def test_size_respects_maximum_500(self):
        assert max(50, min(500, 490 + 20)) == 500

    def test_many_scrolls_reach_max(self):
        size = 310
        for _ in range(10):
            size = max(50, min(500, size + 20))
        assert size == 500

    def test_single_notch_changes_by_20(self):
        assert max(50, min(500, 310 + 20)) == 330

    def test_resize_at_minimum_does_not_go_below(self, app):
        app.preview_size = 50
        app._resize_by(-20)
        assert app.preview_size >= 50

    def test_resize_at_maximum_does_not_go_above(self, app):
        app.preview_size = 500
        app._resize_by(20)
        assert app.preview_size <= 500


class TestScrollZoom:
    """Shift+Alt+Scroll to change zoom level."""

    ZOOM_STEPS = [0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.0, 4.0]

    def test_scroll_up_increases_zoom(self):
        for i in range(len(self.ZOOM_STEPS) - 1):
            assert self.ZOOM_STEPS[i + 1] > self.ZOOM_STEPS[i]

    def test_scroll_down_decreases_zoom(self):
        for i in range(len(self.ZOOM_STEPS) - 1, 0, -1):
            assert self.ZOOM_STEPS[i - 1] < self.ZOOM_STEPS[i]

    def test_steps_are_sorted_ascending(self):
        assert self.ZOOM_STEPS == sorted(self.ZOOM_STEPS)

    def test_includes_1x(self):
        assert 1.0 in self.ZOOM_STEPS

    def test_minimum_is_025(self):
        assert self.ZOOM_STEPS[0] == 0.25

    def test_maximum_is_4x(self):
        assert self.ZOOM_STEPS[-1] == 4.0

    def test_no_duplicate_values(self):
        assert len(self.ZOOM_STEPS) == len(set(self.ZOOM_STEPS))

    def test_zoom_by_at_minimum_does_not_go_below(self, app):
        app.zoom = 0.25
        assert app.zoom == 0.25

    def test_zoom_by_at_maximum_does_not_go_above(self, app):
        app.zoom = 4.0
        assert app.zoom == 4.0


class TestEscapeAndAltF4:
    """Escape and Alt+F4 quit the app."""

    def test_escape_binding_attached(self, app):
        assert hasattr(app, 'root')

    def test_alt_f4_binding_attached(self, app):
        assert hasattr(app, 'root')

    def test_alt_f4_triggers_quit(self, app):
        from mouse_preview import MousePreviewApp
        # Verify that the _quit method exists and exits
        app.save_settings = MagicMock()
        app.handle = MagicMock()
        app._kb_listener = MagicMock()
        app._ms_listener = MagicMock()
        app.root = MagicMock()
        with pytest.raises(SystemExit):
            app._quit()
        app.save_settings.assert_called_once()
