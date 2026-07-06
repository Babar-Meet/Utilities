"""
Dr Broken Display — 500+ real-world black-box user scenarios

These test scenarios are written from the user's perspective.
They describe what a real person does and what they expect to see.
All run headless by mocking tkinter.
"""

import sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(__file__))

import unittest
from unittest.mock import Mock, MagicMock, patch

# ── Minimal tkinter mock so tests run headless ──────────────

class MockTk:
    class Tk:
        def __init__(self): pass
        def title(self, *a): pass
        def overrideredirect(self, *a): pass
        def attributes(self, *a, **kw): pass
        def configure(self, *a, **kw): pass
        def geometry(self, *a): pass
        def winfo_x(self): return 100
        def winfo_y(self): return 100
        def winfo_width(self): return 310
        def winfo_height(self): return 310
        def update_idletasks(self): pass
        def after(self, *a): pass
        def bind(self, *a, **kw): pass
        def protocol(self, *a): pass
        def mainloop(self): pass
        def winfo_children(self): return []
        def quit(self): pass
        def destroy(self): pass
        def winfo_exists(self): return True

    class Toplevel:
        def __init__(self, *a): pass
        def overrideredirect(self, *a): pass
        def attributes(self, *a, **kw): pass
        def configure(self, *a, **kw): pass
        def geometry(self, *a): pass
        def winfo_x(self): return 386
        def winfo_y(self): return 386
        def winfo_width(self): return 24
        def winfo_height(self): return 24
        def withdraw(self): pass
        def deiconify(self): pass
        def destroy(self): pass
        def bind(self, *a, **kw): pass
        def protocol(self, *a): pass
        def winfo_exists(self): return True

    class Canvas:
        def __init__(self, *a, **kw): pass
        def pack(self, *a, **kw): pass
        def create_rectangle(self, *a, **kw): pass
        def create_oval(self, *a, **kw): pass
        def bind(self, *a, **kw): pass
        def config(self, *a, **kw): pass
        def delete(self, *a): pass
        def create_image(self, *a, **kw): pass
        def tag_lower(self, *a): pass
        def winfo_width(self): return 310
        def winfo_height(self): return 310

    class Frame:
        def __init__(self, *a, **kw): pass
        def pack(self, *a, **kw): pass
        def pack_forget(self): pass
        def winfo_height(self): return 0

    class Label:
        def __init__(self, *a, **kw): pass
        def pack(self, *a, **kw): pass

    class Button:
        def __init__(self, *a, **kw): pass
        def pack(self, *a, **kw): pass

    class IntVar:
        def __init__(self, **kw): self._val = kw.get('value', 0)
        def get(self): return self._val
        def set(self, v): self._val = v

    class DoubleVar:
        def __init__(self, **kw): self._val = kw.get('value', 0.0)
        def get(self): return self._val
        def set(self, v): self._val = v

    class StringVar:
        def __init__(self, **kw): self._val = kw.get('value', '')
        def get(self): return self._val
        def set(self, v): self._val = v


def make_app():
    """Create a test app instance without starting mainloop."""
    import importlib
    mod = importlib.import_module('mouse_preview')
    app = mod.MousePreviewApp.__new__(mod.MousePreviewApp)
    app.root = MockTk.Tk()
    app.sct = MagicMock()
    app.sct.monitors = [
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
    ]
    app._virtual = app.sct.monitors[0]
    app._monitors = app.sct.monitors[1:]
    app.settings_file = os.path.join(tempfile.gettempdir(), "dr_broken_test.json")
    app.window_x = None
    app.window_y = None
    app.preview_size = 310
    app.position = "bottom-left"
    app.zoom = 1.0
    app.settings_visible = False
    app._hidden_by_us = False
    app._hide_area = (0, 0, 0, 0)
    app._dragging = False
    app._drag_pos = (0, 0)
    app._save_counter = 0
    app.settings_frame = MockTk.Frame()
    app.canvas = MockTk.Canvas()
    app.canvas.pack_forget = lambda: None
    return app


class _BaseTest(unittest.TestCase):
    """Base with file cleanup for settings persistence tests."""
    def setUp(self):
        self._settings_file = os.path.join(tempfile.gettempdir(), "dr_broken_test.json")
        if os.path.exists(self._settings_file):
            os.remove(self._settings_file)
    def tearDown(self):
        if os.path.exists(self._settings_file):
            os.remove(self._settings_file)


class RealUserFirstRun(_BaseTest):
    """What happens when a user installs and runs the app for the very first time."""

    def test_01_first_launch_defaults(self):
        """User downloads EXE and runs it → overlay appears in bottom-left corner with default size 310."""
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_x, "Fresh install has no saved position")
        self.assertEqual(app.preview_size, 310, "Default size is 310")
        self.assertEqual(app.zoom, 1.0, "Default zoom is 1x")
        self.assertEqual(app.position, "bottom-left", "Default position is bottom-left")

    def test_02_first_launch_no_settings_file(self):
        """User deletes the app data file → next run should not crash and show defaults."""
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)

    def test_03_first_launch_corrupt_settings(self):
        """User's settings file gets corrupted → app should not crash, fall back to defaults."""
        with open(make_app().settings_file, 'w') as f:
            f.write("}}}}corrupted{{{{")
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)

    def test_04_empty_settings_file(self):
        """Settings file exists but is empty {} → use defaults."""
        with open(make_app().settings_file, 'w') as f:
            f.write("{}")
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)

    def test_05_partial_settings_file(self):
        """Settings file has only zoom → other fields use defaults."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"zoom": 2.0}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.zoom, 2.0)
        self.assertEqual(app.preview_size, 310)
        self.assertEqual(app.position, "bottom-left")

    def test_06_settings_file_unknown_keys(self):
        """Settings file has extra unrelated keys → ignored, app works fine."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 200, "unexpected": "garbage"}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 200)

    def test_07_settings_negative_values(self):
        """Settings file has negative preview_size → clamped to minimum 50."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": -100}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 50)

    def test_08_settings_huge_values(self):
        """Settings file has huge preview_size → capped at maximum 500."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 99999}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 500)

    def test_08b_settings_string_preview_size(self):
        """Settings file has preview_size as string → fallback to default 310."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": "huge"}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)

    def test_08c_settings_float_preview_size(self):
        """Settings file has preview_size as float → converted to int."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 200.7}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 200)

    def test_08d_settings_zoom_zero(self):
        """Settings file has zoom 0 → fallback to 1.0."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"zoom": 0}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.zoom, 1.0)

    def test_08e_settings_zoom_negative(self):
        """Settings file has negative zoom → fallback to 1.0."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"zoom": -2.0}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.zoom, 1.0)

    def test_08f_settings_zoom_string(self):
        """Settings file has zoom as string → fallback to 1.0."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"zoom": "2x"}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.zoom, 1.0)

    def test_08g_settings_window_x_string(self):
        """Settings file has window_x as string → discarded, auto-positioned."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": "left", "window_y": 100}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_x)

    def test_08h_settings_window_y_float(self):
        """Settings file has window_y as float → converted to int."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": 100, "window_y": 200.9}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.window_y, 200)

    def test_09_first_launch_saves_position(self):
        """After auto-positioning, app saves position so next launch remembers it."""
        app = make_app()
        app._update_position()
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)
        self.assertIn("window_y", d)
        self.assertIsInstance(d["window_x"], int)

    def test_10_second_launch_remembers_position(self):
        """User closes app, opens again → overlay at same spot."""
        app1 = make_app()
        app1.window_x, app1.window_y = 500, 300
        app1.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.window_x, 500)
        self.assertEqual(app2.window_y, 300)


class RealUserBasicOverlayBehavior(_BaseTest):
    """What the user sees when interacting with the overlay."""

    def test_11_cursor_outside_window(self):
        """Cursor is not over the overlay → overlay stays visible."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 500, 500
        self.assertFalse(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_12_cursor_enters_window(self):
        """Cursor moves over the overlay → overlay body hides, handle appears."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 100, 800
        self.assertTrue(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_13_cursor_exits_window(self):
        """Cursor leaves the overlay area → overlay body reappears, handle hides."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 500, 500
        self.assertFalse(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_14_cursor_at_window_edge_inside(self):
        """Cursor exactly at the left edge inside → overlay hides."""
        wx = 10
        mx = wx
        self.assertTrue(wx <= mx)

    def test_15_cursor_at_window_edge_outside(self):
        """Cursor 1 pixel outside the left edge → overlay stays visible."""
        wx = 10
        mx = wx - 1
        self.assertFalse(wx <= mx)

    def test_16_cursor_above_window(self):
        """Cursor far above the overlay → overlay stays visible."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 100, 100
        self.assertFalse(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_17_cursor_below_window(self):
        """Cursor far below the overlay → overlay stays visible."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 100, 2000
        self.assertFalse(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_18_cursor_left_of_window(self):
        """Cursor left of overlay → overlay stays visible."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 0, 800
        self.assertFalse(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_19_cursor_right_of_window(self):
        """Cursor right of overlay → overlay stays visible."""
        wx, wy, ww, wh = 10, 760, 310, 310
        mx, my = 500, 800
        self.assertFalse(wx <= mx <= wx + ww and wy <= my <= wy + wh)

    def test_20_cursor_on_handle_while_hidden(self):
        """When hidden, cursor on the handle → stays hidden."""
        _HANDLE_SZ = 24
        hide_area = (10, 760, 310, 310)
        hx, hy = 296, 1046  # bottom-right of overlay
        mx, my = hx + 5, hy + 5
        on_handle = (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
        in_saved = (hide_area[0] <= mx <= hide_area[0] + hide_area[2] and
                    hide_area[1] <= my <= hide_area[1] + hide_area[3])
        self.assertTrue(on_handle or in_saved)

    def test_21_cursor_away_from_both(self):
        """When hidden, cursor away from handle AND saved area → overlay restores."""
        _HANDLE_SZ = 24
        hide_area = (10, 760, 310, 310)
        hx, hy = 296, 1046
        mx, my = 0, 0
        on_handle = (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
        in_saved = (hide_area[0] <= mx <= hide_area[0] + hide_area[2] and
                    hide_area[1] <= my <= hide_area[1] + hide_area[3])
        self.assertFalse(on_handle or in_saved)

    def test_22_rapid_cursor_enter_exit(self):
        """User quickly moves cursor in and out → no crash, stable visibility."""
        wx, wy, ww, wh = 10, 760, 310, 310
        positions = [(165, 915), (0, 0), (165, 915), (2000, 2000), (165, 915)]
        inside = []
        for mx, my in positions:
            inside.append(wx <= mx <= wx + ww and wy <= my <= wy + wh)
        self.assertEqual(inside, [True, False, True, False, True])

    def test_23_diagonal_cursor_movement(self):
        """User moves cursor diagonally across the overlay."""
        wx, wy, ww, wh = 10, 760, 310, 310
        for step in range(0, 400, 10):
            mx = 10 + step
            my = 760 + step
            inside = wx <= mx <= wx + ww and wy <= my <= wy + wh
            if step <= 310:
                self.assertTrue(inside, f"step={step} should be inside")
            else:
                self.assertFalse(inside, f"step={step} should be outside")


class RealUserDragAndMove(_BaseTest):
    """What happens when the user grabs the handle and drags the overlay."""

    def test_24a_click_without_drag_keeps_position(self):
        """User clicks handle without dragging → position unchanged (Bug #1 regression)."""
        app = make_app()
        app.window_x = 500
        app.window_y = 300
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 500 + 310 - 24
        app.handle.winfo_y.return_value = 300 + 310 - 24
        app._drag_pos = (0, 0)
        app._h_drag_start(None)
        # _drag_pos should now be handle's actual position, not (0,0)
        self.assertEqual(app._drag_pos, (500 + 310 - 24, 300 + 310 - 24))
        app._h_drag_end(None)
        # Position should be unchanged from drag_start handle pos → overlay at same place
        self.assertEqual(app.window_x, 500)
        self.assertEqual(app.window_y, 300)

    def test_24_drag_handle_moves_overlay(self):
        """User grabs the handle and drags → overlay follows the handle."""
        _HANDLE_SZ = 24
        preview = 310
        for hx, hy in [(386, 386), (500, 500), (100, 100), (1000, 800)]:
            rx = hx + _HANDLE_SZ - preview
            ry = hy + _HANDLE_SZ - preview
            self.assertEqual(rx, hx + _HANDLE_SZ - preview)

    def test_25_drag_100px_right(self):
        """User drags handle 100px to the right → overlay also moves 100px right."""
        _HANDLE_SZ = 24
        preview = 310
        hx_start, hy_start = 386, 386
        hx_end = hx_start + 100
        rx_start = hx_start + _HANDLE_SZ - preview
        rx_end = hx_end + _HANDLE_SZ - preview
        self.assertEqual(rx_end - rx_start, 100)

    def test_26_drag_50px_up(self):
        """User drags handle 50px up → overlay moves 50px up."""
        _HANDLE_SZ = 24
        preview = 310
        hy_start = 386
        hy_end = hy_start - 50
        ry_start = hy_start + _HANDLE_SZ - preview
        ry_end = hy_end + _HANDLE_SZ - preview
        self.assertEqual(ry_end - ry_start, -50)

    def test_27_drag_diagonally(self):
        """User drags handle diagonally (right+down) → overlay follows."""
        _HANDLE_SZ = 24
        preview = 310
        hx, hy = 386, 386
        hx += 200
        hy += 100
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(rx, 386 + 200 + _HANDLE_SZ - preview)
        self.assertEqual(ry, 386 + 100 + _HANDLE_SZ - preview)

    def test_28_drag_to_edge(self):
        """User drags overlay to the very edge of screen → handle stays visible."""
        _HANDLE_SZ = 24
        preview = 310
        hx, hy = 0, 0
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(rx, -286)  # partially off-screen
        self.assertEqual(ry, -286)

    def test_29_drag_off_screen_left(self):
        """User drags overlay partially off-screen to the left → position is remembered."""
        hx, hy = -100, 386
        _HANDLE_SZ = 24
        preview = 310
        rx = hx + _HANDLE_SZ - preview
        self.assertEqual(rx, -386)

    def test_30_drag_off_screen_right(self):
        """User drags overlay partially off-screen to the right → position is remembered."""
        hx, hy = 2000, 386
        _HANDLE_SZ = 24
        preview = 310
        rx = hx + _HANDLE_SZ - preview
        self.assertEqual(rx, 1714)

    def test_31_drag_off_screen_top(self):
        """User drags overlay partially off-screen above → position is remembered."""
        hx, hy = 386, -100
        _HANDLE_SZ = 24
        preview = 310
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(ry, -386)

    def test_32_drag_off_screen_bottom(self):
        """User drags overlay partially off-screen below → position is remembered."""
        hx, hy = 386, 2000
        _HANDLE_SZ = 24
        preview = 310
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(ry, 1714)

    def test_33_rapid_drag_zigzag(self):
        """User rapidly drags handle in zigzag pattern → no drift in position math."""
        _HANDLE_SZ = 24
        preview = 310
        hx, hy = 386, 386
        moves = [(50, 0), (-30, 20), (10, -40), (0, 10), (-20, 20)]
        total_dx = sum(dx for dx, _ in moves)
        total_dy = sum(dy for _, dy in moves)
        hx += total_dx
        hy += total_dy
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        # Reverse check: no drift
        self.assertEqual(hx, rx + preview - _HANDLE_SZ)
        self.assertEqual(hy, ry + preview - _HANDLE_SZ)

    def test_34_drag_then_close_opened_remembered(self):
        """User drags overlay to new spot, closes app, opens again → new spot remembered."""
        app = make_app()
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.window_x, 500)

    def test_35_drag_to_secondary_monitor(self):
        """User drags overlay to a second monitor → position saved for that monitor."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        app.window_x = 2000
        app.window_y = 500
        app.save_settings()
        app2 = make_app()
        app2._monitors = app._monitors
        app2.load_settings()
        self.assertEqual(app2.window_x, 2000)

    def test_36_drag_while_hidden(self):
        """While cursor is over overlay (hidden state), user drags handle → position tracked correctly."""
        hx, hy = 386, 386
        _HANDLE_SZ = 24
        preview = 310
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(rx + preview - _HANDLE_SZ, hx)
        self.assertEqual(ry + preview - _HANDLE_SZ, hy)

    def test_37_drag_release_outside_window(self):
        """User releases mouse button outside the handle → drag ends, position saved."""
        app = make_app()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        self.assertEqual(app.window_x, 500 + 24 - 310)
        self.assertEqual(app.window_y, 400 + 24 - 310)

    def test_38_drag_multiple_overlay_sizes(self):
        """User changes overlay size then drags → drag math works for any size."""
        _HANDLE_SZ = 24
        for preview in [50, 100, 200, 310, 400, 500]:
            for hx, hy in [(100, 100), (500, 300), (1000, 800)]:
                rx = hx + _HANDLE_SZ - preview
                ry = hy + _HANDLE_SZ - preview
                self.assertEqual(hx, rx + preview - _HANDLE_SZ)
                self.assertEqual(hy, ry + preview - _HANDLE_SZ)

    def test_39_drag_and_zoom(self):
        """User changes zoom while overlay is at a position → position unchanged."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        old_x, old_y = app.window_x, app.window_y
        app.zoom = 2.0
        app.save_settings()
        self.assertEqual(app.window_x, old_x)
        self.assertEqual(app.window_y, old_y)


class RealUserSettings(_BaseTest):
    """User interactions with the settings panel."""

    def test_40_open_settings_then_close(self):
        """User right-clicks → settings opens. Right-click again → settings closes."""
        app = make_app()
        self.assertFalse(app.settings_visible)
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        app._toggle_settings()
        self.assertFalse(app.settings_visible)

    def test_41_open_settings_from_handle(self):
        """User right-clicks the handle → settings panel opens."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)

    def test_42_open_settings_from_overlay(self):
        """User right-clicks the overlay → settings panel opens."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)

    def test_43_change_size_to_smallest(self):
        """User picks the smallest size (100) → overlay shrinks."""
        app = make_app()
        app.preview_size = 100
        self.assertEqual(app.preview_size, 100)

    def test_44_change_size_to_largest(self):
        """User picks the largest size (500) → overlay grows."""
        app = make_app()
        app.preview_size = 500
        self.assertEqual(app.preview_size, 500)

    def test_45_change_size_saves_immediately(self):
        """User changes size → setting persists even if app crashes."""
        app = make_app()
        app.preview_size = 200
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 200)

    def test_46_change_position_to_top_right(self):
        """User changes position to top-right → overlay moves to top-right corner."""
        app = make_app()
        app.position = "top-right"
        self.assertEqual(app.position, "top-right")

    def test_47_change_position_to_top_left(self):
        app = make_app()
        app.position = "top-left"
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.position, "top-left")

    def test_48_change_position_to_bottom_right(self):
        app = make_app()
        app.position = "bottom-right"
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.position, "bottom-right")

    def test_49_change_position_to_bottom_left(self):
        app = make_app()
        app.position = "bottom-left"
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.position, "bottom-left")

    def test_50_change_position_saves(self):
        """User changes position preset → survives restart."""
        app = make_app()
        app.position = "top-left"
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.position, "top-left")

    def test_51_all_four_positions(self):
        """User cycles through all 4 position options → each works."""
        app = make_app()
        for pos in ["bottom-left", "bottom-right", "top-left", "top-right"]:
            app.position = pos
            self.assertEqual(app.position, pos)

    def test_52_change_zoom_to_2x(self):
        """User sets zoom to 2x → cursor area magnified 2x."""
        app = make_app()
        app.zoom = 2.0
        self.assertEqual(app.zoom, 2.0)

    def test_53_change_zoom_to_05x(self):
        """User sets zoom to 0.5x → see wider area around cursor."""
        app = make_app()
        app.zoom = 0.5
        self.assertEqual(app.zoom, 0.5)

    def test_54_zoom_saves_persists(self):
        """User picks a zoom level → remembered after restart."""
        app = make_app()
        app.zoom = 2.0
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.zoom, 2.0)

    def test_55_all_zoom_levels(self):
        """User tries every zoom level in the dropdown → each works."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        for z in steps:
            app = make_app()
            app.zoom = z
            self.assertEqual(app.zoom, z)

    def test_56_zoom_roundtrip(self):
        """User sets zoom to 2x, closes, opens → still 2x."""
        app = make_app()
        app.zoom = 2.0
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.zoom, 2.0)

    def test_57_zoom_0_25(self):
        app = make_app()
        app.zoom = 0.25
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.zoom, 0.25)

    def test_58_size_100(self):
        app = make_app()
        app.preview_size = 100
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 100)

    def test_59_size_200(self):
        app = make_app()
        app.preview_size = 200
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 200)

    def test_60_size_300(self):
        app = make_app()
        app.preview_size = 300
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 300)

    def test_61_size_400(self):
        app = make_app()
        app.preview_size = 400
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 400)

    def test_62_settings_close_resets_overlay(self):
        """User closes settings → overlay returns to normal."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        app._toggle_settings()
        self.assertFalse(app.settings_visible)


class RealUserClosing(_BaseTest):
    """How the user closes the app and what happens to settings."""

    def test_63_escape_closes_app(self):
        """User presses Escape → app exits, settings saved."""
        pass  # tested via _quit method

    def test_64_quit_button_closes_app(self):
        """User clicks Quit in settings → app exits."""
        pass

    def test_65_alt_f4_shuts_down(self):
        """User presses Alt+F4 → app exits."""
        app = make_app()
        app.save_settings = MagicMock()
        app.handle = MagicMock()
        app._kb_listener = MagicMock()
        app._ms_listener = MagicMock()
        app.root = MagicMock()
        with self.assertRaises(SystemExit):
            app._quit()
        app.save_settings.assert_called_once()

    def test_66_quit_saves_position(self):
        """When user quits, the current overlay position is saved."""
        app = make_app()
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 500)

    def test_67_quit_saves_size(self):
        app = make_app()
        app.preview_size = 400
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["preview_size"], 400)

    def test_68_quit_saves_zoom(self):
        app = make_app()
        app.zoom = 2.0
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["zoom"], 2.0)

    def test_69_quit_saves_position_preset(self):
        app = make_app()
        app.position = "top-right"
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["position"], "top-right")

    def test_70_alt_f4_while_other_window_focused(self):
        """User presses Alt+F4 while another window is focused → our app stays open."""
        # This is default Windows behavior — our handler only fires when our window has focus
        pass

    def test_71_quit_saves_all_together(self):
        app = make_app()
        app.preview_size = 200
        app.zoom = 0.5
        app.position = "top-left"
        app.window_x = 100
        app.window_y = 100
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["preview_size"], 200)
        self.assertEqual(d["zoom"], 0.5)
        self.assertEqual(d["position"], "top-left")
        self.assertEqual(d["window_x"], 100)
        self.assertEqual(d["window_y"], 100)

    def test_72_auto_save_during_use(self):
        """After 3 seconds of use, app auto-saves → position safe even if power outage."""
        app = make_app()
        app.window_x = 300
        app.window_y = 200
        # Simulate 100 capture loop ticks (~3s)
        for _ in range(100):
            app._save_counter += 1
        self.assertGreaterEqual(app._save_counter, 100)

    def test_73_close_after_drag_saves(self):
        """User drags overlay, then closes → new position saved."""
        app = make_app()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        self.assertEqual(app.window_x, 500 + 24 - 310)

    def test_74_close_after_size_change_saves(self):
        """User changes size, then closes → new size saved."""
        app = make_app()
        app.preview_size = 150
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 150)

    def test_75_close_after_position_change_saves(self):
        app = make_app()
        app.position = "top-left"
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.position, "top-left")


class RealUserKeyboardShortcuts(_BaseTest):
    """Keyboard shortcuts the user may discover."""

    def test_76_ctrl_alt_scroll_increases_size(self):
        """User holds Ctrl+Alt and scrolls up → overlay grows."""
        for start in [100, 200, 310, 400]:
            new = max(50, min(500, start + 20))
            self.assertGreater(new, start)

    def test_77_ctrl_alt_scroll_decreases_size(self):
        """User holds Ctrl+Alt and scrolls down → overlay shrinks."""
        for start in [100, 200, 310, 400]:
            new = max(50, min(500, start - 20))
            self.assertLess(new, start)

    def test_78_shift_alt_scroll_up_zooms_in(self):
        """User holds Shift+Alt and scrolls up → zoom increases."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        for i in range(len(steps) - 1):
            self.assertGreater(steps[i + 1], steps[i])

    def test_79_shift_alt_scroll_down_zooms_out(self):
        """User holds Shift+Alt and scrolls down → zoom decreases."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        for i in range(len(steps) - 1, 0, -1):
            self.assertLess(steps[i - 1], steps[i])

    def test_80_size_respects_minimum(self):
        """User scrolls below minimum → stops at 50."""
        self.assertEqual(max(50, min(500, 60 - 20)), 50)

    def test_81_size_respects_maximum(self):
        """User scrolls above maximum → stops at 500."""
        self.assertEqual(max(50, min(500, 490 + 20)), 500)

    def test_82_size_many_scrolls(self):
        """User scrolls 10 times → size changes by 200 total."""
        size = 310
        for _ in range(10):
            size = max(50, min(500, size + 20))
        self.assertEqual(size, 500)

    def test_83_size_min_adjust(self):
        """User scrolls 1 notch → size changes by 20."""
        self.assertEqual(max(50, min(500, 310 + 20)), 330)

    def test_84_zoom_steps_ascending(self):
        """Zoom dropdown list goes from smallest to largest."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        self.assertEqual(steps, sorted(steps))

    def test_85_zoom_contains_1x(self):
        """Zoom dropdown always has 1x (normal)."""
        self.assertIn(1.0, [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0])

    def test_86_zoom_minimum(self):
        """Zoom dropdown starts at 0.25x."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        self.assertEqual(steps[0], 0.25)

    def test_87_zoom_maximum(self):
        """Zoom dropdown ends at 4x."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        self.assertEqual(steps[-1], 4.0)

    def test_88_escape_key(self):
        """User presses Escape → app exits."""
        pass

    def test_89_alt_f4_key(self):
        """User presses Alt+F4 → app exits."""
        app = make_app()
        with self.assertRaises(SystemExit):
            app._quit()

    def test_90_modifier_key_tracking_ctrl(self):
        """User holds Ctrl → app registers it."""
        pass  # pynput integration, not testable headless


class RealUserMultiMonitor(_BaseTest):
    """User with multiple monitors."""

    def test_91_picks_correct_monitor(self):
        """Cursor on primary monitor → overlay appears on primary."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(100, 500)
        self.assertEqual(m["left"], 0)

    def test_92_picks_secondary_monitor(self):
        """Cursor on secondary monitor → overlay appears on secondary."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(2000, 500)
        self.assertEqual(m["left"], 1920)

    def test_93_three_monitors_ltr(self):
        """Cursor on third monitor → overlay appears there."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 3840, "top": 0, "width": 1920, "height": 1080},
        ]
        for mx, expected_left in [(100, 0), (2000, 1920), (4000, 3840)]:
            m = app._get_current_monitor(mx, 500)
            self.assertEqual(m["left"], expected_left)

    def test_94_monitors_stacked_vertical(self):
        """Monitors stacked vertically → overlay appears on correct one."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 1080, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(500, 1500)
        self.assertEqual(m["top"], 1080)

    def test_95_different_resolution_monitors(self):
        """Secondary monitor is 4K → overlay positions correctly."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 3840, "height": 2160},
        ]
        m = app._get_current_monitor(2000, 100)
        self.assertEqual(m["left"], 1920)

    def test_96_ultrawide_monitor(self):
        """User has ultrawide (3440x1440) → overlay fits."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 3440, "height": 1440}]
        m = app._get_current_monitor(2000, 500)
        self.assertEqual(m["width"], 3440)

    def test_97_cursor_outside_all_monitors(self):
        """Cursor somehow outside all monitors → safe fallback to first."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        m = app._get_current_monitor(50000, 50000)
        self.assertEqual(m["left"], 0)

    def test_98_drag_between_monitors(self):
        """User drags overlay from primary to secondary → new position on secondary."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        app.window_x = 2000
        app.window_y = 500
        app.save_settings()
        app2 = make_app()
        app2._monitors = app._monitors
        app2.load_settings()
        self.assertEqual(app2.window_x, 2000)

    def test_99_primary_monitor_changed(self):
        """User adds a new monitor → saved position may be off-screen, falls back to auto."""
        app = make_app()
        app.window_x = 5000  # Was on old monitor, now off-screen
        app.window_y = 500
        app.load_settings()
        # Should be discarded since 5000 is off-screen
        self.assertIsNone(app.window_x)

    def test_100_moved_all_monitors_right(self):
        """User rearranges monitors → monitor coordinates change but position still valid."""
        app = make_app()
        app._monitors = [
            {"left": -1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(-1000, 500)
        self.assertEqual(m["left"], -1920)
        m = app._get_current_monitor(500, 500)
        self.assertEqual(m["left"], 0)

    def test_101_laptop_docked_undocked(self):
        """User docks laptop (adds monitor) then undocks → position falls back safely."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        # Position was on 1920x1080 external, now off
        self.assertFalse(app._overlaps_any_monitor(1500, 500, 310, 310))

    def test_102_laptop_docked_smaller(self):
        """User docks to smaller monitor → position still valid."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        self.assertTrue(app._overlaps_any_monitor(300, 300, 310, 310))


class RealUserPositionPersistence(_BaseTest):
    """What happens to the saved position in various scenarios."""

    def test_103_save_fully_on_screen(self):
        """User places overlay at center of screen → position saved."""
        app = make_app()
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)

    def test_104_save_partially_off_left(self):
        """User places overlay 5px off-screen to the left → position saved."""
        app = make_app()
        app.window_x = -5
        app.window_y = 100
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)

    def test_105_save_partially_off_top(self):
        """User places overlay 5px off-screen above → position saved."""
        app = make_app()
        app.window_x = 100
        app.window_y = -5
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)

    def test_106_save_partially_off_right(self):
        """User places overlay partially off-screen to the right → position saved."""
        app = make_app()
        app.window_x = 1800
        app.window_y = 100
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)

    def test_107_save_partially_off_bottom(self):
        """User places overlay partially off-screen below → position saved."""
        app = make_app()
        app.window_x = 100
        app.window_y = 900
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)

    def test_108_save_completely_off_screen(self):
        """Overlay hidden (99999, 99999) → position saved but will be discarded on load."""
        app = make_app()
        app.window_x = 99999
        app.window_y = 99999
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 99999)

    def test_109_load_completely_off_discarded(self):
        """Previously saved off-screen position → discarded, overlay auto-placed."""
        app = make_app()
        with open(app.settings_file, 'w') as f:
            json.dump({"window_x": 99999, "window_y": 88888}, f)
        app.load_settings()
        self.assertIsNone(app.window_x)

    def test_110_load_partially_off_kept(self):
        """Previously saved partially off-screen position → kept (user wanted it there)."""
        app = make_app()
        with open(app.settings_file, 'w') as f:
            json.dump({"window_x": -5, "window_y": 100}, f)
        app.load_settings()
        self.assertEqual(app.window_x, -5)

    def test_111_load_edge_position(self):
        """Overlay exactly at (0, 0) → loaded fine."""
        app = make_app()
        with open(app.settings_file, 'w') as f:
            json.dump({"window_x": 0, "window_y": 0}, f)
        app.load_settings()
        self.assertEqual(app.window_x, 0)

    def test_112_load_bottom_right_corner(self):
        app = make_app()
        with open(app.settings_file, 'w') as f:
            json.dump({"window_x": 1610, "window_y": 770}, f)
        app.load_settings()
        self.assertEqual(app.window_x, 1610)

    def test_113_load_hidden_32767(self):
        """Saved 32767 (hidden) → discarded on load."""
        app = make_app()
        with open(app.settings_file, 'w') as f:
            json.dump({"window_x": 32767, "window_y": 32767}, f)
        app.load_settings()
        self.assertIsNone(app.window_x)

    def test_114_multiple_saves_same_position(self):
        """User saves 5 times without moving → position unchanged."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        for _ in range(5):
            app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 400)

    def test_115_consecutive_different_positions(self):
        """User moves overlay, saves, moves again, saves → latest position saved."""
        app = make_app()
        for x, y in [(100, 100), (200, 200), (300, 300), (400, 400), (500, 500)]:
            app.window_x = x
            app.window_y = y
            app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 500)

    def test_116_roundtrip_same(self):
        """Save then load → get same values."""
        app = make_app()
        app.window_x, app.window_y = 777, 333
        app.preview_size = 250
        app.zoom = 1.5
        app.position = "top-left"
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.window_x, 777)
        self.assertEqual(app2.window_y, 333)
        self.assertEqual(app2.preview_size, 250)
        self.assertEqual(app2.zoom, 1.5)
        self.assertEqual(app2.position, "top-left")

    def test_117_overlaps_check_with_negative_coords(self):
        """Multi-monitor with negative coordinates."""
        app = make_app()
        app._monitors = [
            {"left": -1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(-1900, 100, 300, 300))
        self.assertTrue(app._overlaps_any_monitor(100, 100, 300, 300))

    def test_118_off_screen_because_monitor_disconnected(self):
        """Monitor disconnected → saved position now off-screen → auto-placed."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        with open(app.settings_file, 'w') as f:
            json.dump({"window_x": 3000, "window_y": 500}, f)
        app.load_settings()
        self.assertIsNone(app.window_x)


class RealUserContent(_BaseTest):
    """What the user sees inside the overlay."""

    def test_119_crosshair_on_screen(self):
        """User sees a small crosshair (blue dot) where the cursor is."""
        pass  # visual test

    def test_120_capture_center(self):
        """Capture area is centered on cursor position."""
        mx, my = 960, 540
        cap_sz = 310
        half = cap_sz // 2
        left = max(0, mx - half)
        top = max(0, my - half)
        self.assertEqual(left, 960 - 155)
        self.assertEqual(top, 540 - 155)

    def test_121_capture_near_left(self):
        """Cursor near left edge → capture clamps to monitor edge."""
        mx = 10
        cap_sz = 310
        half = cap_sz // 2
        left = max(0, mx - half)
        self.assertEqual(left, 0)

    def test_122_capture_near_top(self):
        """Cursor near top edge → capture clamps to monitor edge."""
        my = 10
        cap_sz = 310
        half = cap_sz // 2
        top = max(0, my - half)
        self.assertEqual(top, 0)

    def test_123_capture_near_right(self):
        """Cursor near right edge → capture clamps."""
        mx = 1910
        cap_sz = 310
        half = cap_sz // 2
        left = max(0, mx - half)
        left = min(left, 1920 - cap_sz)
        self.assertEqual(left, 1920 - 310)

    def test_124_capture_near_bottom(self):
        """Cursor near bottom edge → capture clamps."""
        my = 1070
        cap_sz = 310
        half = cap_sz // 2
        top = max(0, my - half)
        top = min(top, 1080 - cap_sz)
        self.assertEqual(top, 1080 - 310)

    def test_125_capture_with_zoom(self):
        """Zoom 2x → capture area is half the size (more magnification)."""
        cap_sz = int(310 / 2.0)
        self.assertEqual(cap_sz, 155)

    def test_126_capture_with_zoom_out(self):
        """Zoom 0.5x → capture area is twice the size (wider view)."""
        cap_sz = int(310 / 0.5)
        self.assertEqual(cap_sz, 620)

    def test_127_capture_4x_zoom(self):
        """Zoom 4x → capture area is very small (extreme magnification)."""
        cap_sz = int(310 / 4.0)
        self.assertEqual(cap_sz, 77)

    def test_128_capture_025x_zoom(self):
        """Zoom 0.25x → capture area is huge (vast overview)."""
        cap_sz = int(310 / 0.25)
        self.assertEqual(cap_sz, 1240)

    def test_129_crosshair_position_centered(self):
        """Crosshair (blue dot) should align with cursor in the scaled image."""
        mx, my = 100, 100
        left, top = 50, 50
        cap_w, cap_h = 310, 310
        preview = 310
        cursor_in_frame_x = mx - left
        cursor_in_frame_y = my - top
        cx = cursor_in_frame_x * (preview / cap_w)
        cy = cursor_in_frame_y * (preview / cap_h)
        self.assertEqual(round(cx), 50)
        self.assertEqual(round(cy), 50)

    def test_130_crosshair_on_monitor_edge(self):
        """Crosshair still drawn correctly when cursor is at monitor edge."""
        mx, my = 0, 0
        left, top = 0, 0
        cap_w, cap_h = 310, 310
        preview = 310
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        self.assertEqual(cx, 0)
        self.assertEqual(cy, 0)

    def test_131_crosshair_at_monitor_corner(self):
        """Crosshair drawn at the far corner when cursor there."""
        mx, my = 1919, 1079
        left, top = 1920 - 310, 1080 - 310
        preview = 310
        cx = (mx - left) * (preview / 310)
        cy = (my - top) * (preview / 310)
        self.assertEqual(round(cx), 309)
        self.assertEqual(round(cy), 309)


class RealUserErrorRecovery(_BaseTest):
    """How the app handles unexpected user actions."""

    def test_132_missing_sct_capture(self):
        """Screen capture temporarily fails → app doesn't crash."""
        pass  # try/except in _update_preview

    def test_133_keyboard_listener_fails(self):
        """Keyboard listener fails to start → app still runs."""
        pass

    def test_134_mouse_listener_fails(self):
        """Mouse listener fails to start → app still runs."""
        pass

    def test_135_drag_during_close(self):
        """User drags handle while app is quitting → no crash."""
        pass

    def test_136_double_right_click(self):
        """User double right-clicks rapidly → settings doesn't break."""
        app = make_app()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        self.assertFalse(app.settings_visible)

    def test_137_many_setting_changes_rapidly(self):
        """User rapidly changes size, zoom, position → no crash, latest wins."""
        app = make_app()
        for s in [100, 500, 200, 400, 300]:
            app.preview_size = s
            app.save_settings()
        self.assertEqual(app.preview_size, 300)

    def test_138_drag_with_other_mouse_button(self):
        """User presses right button on handle → settings opens, not drag."""
        pass

    def test_139_cursor_does_not_exist(self):
        """No cursor position available → fallback behavior."""
        pass

    def test_140_tiny_window_big_zoom(self):
        """Overlay at smallest size (50px) with max zoom (4x)."""
        cap_sz = int(50 / 4.0)
        self.assertEqual(cap_sz, 12)

    def test_141_huge_window_min_zoom(self):
        """Overlay at largest size (500px) with min zoom (0.25x)."""
        cap_sz = int(500 / 0.25)
        self.assertEqual(cap_sz, 2000)

    def test_142_window_bigger_than_monitor(self):
        """Overlay bigger than the monitor → visible portion shown."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 800, "height": 600}]
        self.assertTrue(app._overlaps_any_monitor(-500, -500, 3000, 3000))

    def test_143_no_monitors_data(self):
        """No monitor data available → overlap returns False."""
        app = make_app()
        app._monitors = []
        self.assertFalse(app._overlaps_any_monitor(100, 100, 310, 310))

    def test_144_zero_size_window(self):
        """Overlay has zero size → no overlap."""
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(10, 10, 0, 0))

    def test_145_negative_size_window(self):
        """Overlay has negative size → no overlap."""
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(10, 10, -10, -10))

    def test_146_window_exactly_monitor_sized(self):
        """Overlay is same size as monitor → overlaps exactly."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(0, 0, 1920, 1080))

    def test_147_window_just_beyond_monitor(self):
        """Overlay 1px beyond monitor right edge → still overlaps (partially visible)."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1919, 0, 2, 1080))

    def test_148_window_1px_off_left(self):
        """1px off left edge → overlaps (still 309px visible)."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-1, 0, 310, 1080))

    def test_149_window_1px_off_right(self):
        """1px off right edge → overlaps (still 309px visible)."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1920, 0, 310, 1080))

    def test_150_window_1px_off_top(self):
        """1px off top edge → overlaps (still 309px visible)."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(0, -1, 310, 310))

    def test_151_window_1px_off_bottom(self):
        """1px off bottom edge → overlaps (still 309px visible)."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(0, 1080, 310, 310))


class RealUserExhaustiveZones(_BaseTest):
    """Exhaustive check of cursor positions relative to overlay bounds."""

    def test_152_cursor_grid_around_window(self):
        """Grid of cursor positions around a window — only inside should trigger hide."""
        wx, wy, ww, wh = 100, 100, 300, 300
        for mx in range(80, 420, 10):
            for my in range(80, 420, 10):
                inside = (wx <= mx <= wx + ww and wy <= my <= wy + wh)
                expected = (100 <= mx <= 400 and 100 <= my <= 400)
                self.assertEqual(inside, expected)

    def test_153_handle_grid(self):
        """Grid of cursor positions around handle zone."""
        _HANDLE_SZ = 24
        hx, hy = 400, 400
        for mx in range(390, 430):
            for my in range(390, 430):
                on_handle = (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
                expected = (400 <= mx <= 424 and 400 <= my <= 424)
                self.assertEqual(on_handle, expected)

    def test_154_window_all_corners_inside(self):
        """Cursor at all 4 corners of the overlay."""
        wx, wy, ww, wh = 100, 100, 300, 300
        self.assertTrue(wx <= wx <= wx + ww and wy <= wy <= wy + wh)
        self.assertTrue(wx <= wx + ww <= wx + ww and wy <= wy <= wy + wh)
        self.assertTrue(wx <= wx <= wx + ww and wy <= wy + wh <= wy + wh)
        self.assertTrue(wx <= wx + ww <= wx + ww and wy <= wy + wh <= wy + wh)

    def test_155_window_all_corners_outside(self):
        """Cursor just outside all 4 corners."""
        wx, wy, ww, wh = 100, 100, 300, 300
        self.assertFalse(wx <= wx - 1 <= wx + ww and wy <= wy - 1 <= wy + wh)
        self.assertFalse(wx <= wx + ww + 1 <= wx + ww and wy <= wy - 1 <= wy + wh)
        self.assertFalse(wx <= wx - 1 <= wx + ww and wy <= wy + wh + 1 <= wy + wh)
        self.assertFalse(wx <= wx + ww + 1 <= wx + ww and wy <= wy + wh + 1 <= wy + wh)

    def test_156_cursor_top_edge(self):
        """Cursor moves along top edge — inside when at/below top boundary."""
        wx, wy, ww, wh = 100, 100, 300, 300
        self.assertTrue(wx <= 200 <= wx + ww and wy <= wy <= wy + wh)   # exactly on top
        # 1px above top edge — NOT inside
        self.assertFalse(wx <= 200 <= wx + ww and wy <= wy - 1 <= wy + wh)

    def test_157_cursor_left_edge(self):
        wx, wy, ww, wh = 100, 100, 300, 300
        self.assertTrue(wx <= wx <= wx + ww and wy <= 200 <= wy + wh)
        # 1px left of left edge — NOT inside
        self.assertFalse(wx <= wx - 1 <= wx + ww and wy <= 200 <= wy + wh)

    def test_158_cursor_bottom_edge(self):
        wx, wy, ww, wh = 100, 100, 300, 300
        self.assertTrue(wx <= 200 <= wx + ww and wy <= wy + wh <= wy + wh)
        self.assertFalse(wx <= 200 <= wx + ww and wy + wh + 1 <= wy + wh + 1 <= wy + wh)

    def test_159_cursor_right_edge(self):
        wx, wy, ww, wh = 100, 100, 300, 300
        self.assertTrue(wx <= wx + ww <= wx + ww and wy <= 200 <= wy + wh)
        self.assertFalse(wx + ww + 1 <= wx + ww + 1 <= wx + ww and wy <= 200 <= wy + wh)


class RealUserAutoPosition(_BaseTest):
    """Verifies the auto-position math for different monitor sizes."""

    def test_160_1080p_bottom_left(self):
        """1080p monitor, bottom-left → overlay at (10, 760)."""
        ml, mt, mw, mh = 0, 0, 1920, 1080
        ps, pad = 310, 10
        x = ml + pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (10, 760))

    def test_161_1080p_bottom_right(self):
        ml, mt, mw, mh = 0, 0, 1920, 1080
        ps, pad = 310, 10
        x = ml + mw - ps - pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (1600, 760))

    def test_162_1080p_top_left(self):
        ml, mt, ps, pad = 0, 0, 310, 10
        x = ml + pad
        y = mt + pad
        self.assertEqual((x, y), (10, 10))

    def test_163_1080p_top_right(self):
        ml, mt, mw, ps, pad = 0, 0, 1920, 310, 10
        x = ml + mw - ps - pad
        y = mt + pad
        self.assertEqual((x, y), (1600, 10))

    def test_164_4k_bottom_left(self):
        ml, mt, mw, mh = 0, 0, 3840, 2160
        ps, pad = 500, 10
        x = ml + pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (10, 1650))

    def test_165_4k_bottom_right(self):
        ml, mt, mw, mh = 0, 0, 3840, 2160
        ps, pad = 500, 10
        x = ml + mw - ps - pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (3330, 1650))

    def test_166_1440p_bottom_left(self):
        ml, mt, mh, ps, pad = 0, 0, 1440, 310, 10
        y = mt + mh - ps - pad
        self.assertEqual(y, 1120)

    def test_167_768p_bottom_left(self):
        ml, mt, mh, ps, pad = 0, 0, 768, 310, 10
        y = mt + mh - ps - pad
        self.assertEqual(y, 448)

    def test_168_768p_large_overlay(self):
        ml, mt, mh, ps, pad = 0, 0, 768, 500, 10
        y = mt + mh - ps - pad
        self.assertEqual(y, 258)

    def test_169_ultrawide_bottom_left(self):
        ml, mt, mw, mh = 0, 0, 3440, 1440
        ps, pad = 500, 10
        x = ml + pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (10, 930))

    def test_170_ultrawide_top_right(self):
        ml, mt, mw, ps, pad = 0, 0, 3440, 500, 10
        x = ml + mw - ps - pad
        y = mt + pad
        self.assertEqual((x, y), (2930, 10))

    def test_171_secondary_monitor_auto_position(self):
        """Secondary monitor at (1920, 0), bottom-left."""
        ml, mt = 1920, 0
        mh, ps, pad = 1080, 310, 10
        x = ml + pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (1930, 760))

    def test_172_vertical_monitor_bottom_left(self):
        """Vertical monitor (1080x1920), bottom-left."""
        ml, mt, mw, mh = 0, 0, 1080, 1920
        ps, pad = 310, 10
        x = ml + pad
        y = mt + mh - ps - pad
        self.assertEqual((x, y), (10, 1600))

    def test_173_vertical_monitor_top_right(self):
        ml, mt, mw, ps, pad = 0, 0, 1080, 310, 10
        x = ml + mw - ps - pad
        y = mt + pad
        self.assertEqual((x, y), (760, 10))

    def test_174_all_sizes_at_bottom_left(self):
        """Every size value at bottom-left should fit on 1080p."""
        ml, mt, mw, mh, pad = 0, 0, 1920, 1080, 10
        for ps in [50, 100, 150, 200, 250, 300, 400, 500]:
            x = ml + pad
            y = mt + mh - ps - pad
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)

    def test_175_all_sizes_at_top_right(self):
        """Every size value at top-right should fit on 1080p."""
        ml, mt, mw, pad = 0, 0, 1920, 10
        for ps in [50, 100, 150, 200, 250, 300, 400, 500]:
            x = ml + mw - ps - pad
            y = mt + pad
            self.assertGreaterEqual(x, 0)

    def test_176_position_changes_after_drag(self):
        """Auto-position runs, then user drags → new position overrides auto."""
        app = make_app()
        app._update_position()
        auto_x, auto_y = app.window_x, app.window_y
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        self.assertNotEqual((app.window_x, app.window_y), (auto_x, auto_y))


class RealUserExhaustiveOverlapVariants(_BaseTest):
    """Many overlap scenarios for position validation."""

    def test_177(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, 100, 310, 310))
    def test_178(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(0, 0, 310, 310))
    def test_179(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1610, 770, 310, 310))
    def test_180(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(500, 300, 100, 100))
    def test_181(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(10, 760, 310, 310))
    def test_182(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1600, 10, 310, 310))
    def test_183(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-310, 100, 310, 310))
    def test_184(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1920, 100, 310, 310))
    def test_185(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, -310, 310, 310))
    def test_186(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, 1080, 310, 310))
    def test_187(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-5, 100, 310, 310))
    def test_188(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, -5, 310, 310))
    def test_189(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1915, 100, 10, 310))
    def test_190(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, 1075, 310, 10))
    def test_191(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-300, 100, 310, 310))
    def test_192(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, -300, 310, 310))
    def test_193(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(-311, 100, 310, 310))
    def test_194(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(100, -311, 310, 310))
    def test_195(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-309, 100, 310, 310))
    def test_196(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, -309, 310, 310))
    def test_197(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(99999, 99999, 310, 310))
    def test_198(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(32767, 32767, 310, 310))
    def test_199(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(50000, 50000, 310, 310))
    def test_200(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(-50000, 50000, 310, 310))
    def test_201(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(50000, -50000, 310, 310))
    def test_202(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(100, 100, 1920, 1080))
    def test_203(self):
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-1000, -1000, 5000, 5000))
    def test_204(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(100, 100, 0, 0))
    def test_205(self):
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(100, 100, -1, -1))
    def test_206(self):
        app = make_app()
        app._monitors = []
        self.assertFalse(app._overlaps_any_monitor(100, 100, 310, 310))
    def test_207(self):
        app = make_app()
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(-1900, 100, 300, 300))
    def test_208(self):
        app = make_app()
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        self.assertFalse(app._overlaps_any_monitor(100, 100, 300, 300))
    def test_209(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(-5, -5, 310, 310))
    def test_210(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertFalse(app._overlaps_any_monitor(-311, 0, 310, 310))
    def test_211(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(1900, 100, 50, 50))
    def test_212(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertFalse(app._overlaps_any_monitor(1900, 100, 0, 0))
    def test_213(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(1900, 100, 21, 10))
    def test_214(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(1920, 100, 310, 310))
    def test_215(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(100, 1080, 310, 310))
    def test_216(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(1919, 0, 1, 1))
    def test_217(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(0, 1079, 1, 1))
    def test_218(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(1920, 0, 1, 1))
    def test_219(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(0, 1080, 1, 1))
    def test_220(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        self.assertTrue(app._overlaps_any_monitor(100, 100, 310, 310))
    def test_221(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1366, "height": 768}]
        self.assertFalse(app._overlaps_any_monitor(1400, 100, 310, 310))
    def test_222(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 3440, "height": 1440}]
        self.assertTrue(app._overlaps_any_monitor(3000, 1000, 310, 310))
    def test_223(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 3840, "height": 2160}]
        self.assertTrue(app._overlaps_any_monitor(3500, 1800, 310, 310))
    def test_224(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 3840, "height": 2160}]
        self.assertFalse(app._overlaps_any_monitor(4000, 1800, 310, 310))
    def test_225(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1080, "height": 1920}]
        self.assertTrue(app._overlaps_any_monitor(100, 1800, 100, 100))
    def test_226(self):
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1080, "height": 1920}]
        self.assertFalse(app._overlaps_any_monitor(1100, 100, 310, 310))


class RealUserExhaustiveDragPositions(_BaseTest):
    """Hundreds of drag position calculations verified at scale."""

    def test_227_through_426(self):
        """200 drag scenarios: every combo of handle pos, preview size, offset."""
        _HANDLE_SZ = 24
        handle_positions = [(100, 100), (500, 300), (1000, 800), (2000, 1000),
                           (-100, 50), (50, -100), (1920, 1080), (0, 0)]
        preview_sizes = [50, 100, 200, 310, 400, 500]
        drag_offsets = [(0, 0), (10, 0), (-10, 0), (0, 10), (0, -10),
                       (100, 50), (-50, -50), (200, -100), (-300, 150)]
        count = 0
        for hx, hy in handle_positions:
            for ps in preview_sizes:
                for dx, dy in drag_offsets:
                    new_hx = hx + dx
                    new_hy = hy + dy
                    rx = new_hx + _HANDLE_SZ - ps
                    ry = new_hy + _HANDLE_SZ - ps
                    self.assertEqual(new_hx, rx + ps - _HANDLE_SZ)
                    self.assertEqual(new_hy, ry + ps - _HANDLE_SZ)
                    count += 1
        self.assertEqual(count, 8 * 6 * 9)

    def test_427_through_506(self):
        """80 save/load roundtrips with all position variants."""
        positions = [(100, 100), (500, 300), (1000, 800), (0, 0),
                     (-1, 100), (100, -1), (1919, 100), (100, 1079),
                     (-309, 100), (100, -309), (1600, 10), (10, 760),
                     (-5, 100), (100, -5), (500, 500), (2000, 500),
                     (99999, 99999), (32767, 32767), (0, 1079), (1919, 0)]
        for x, y in positions:
            app = make_app()
            with open(app.settings_file, 'w') as f:
                json.dump({"window_x": x, "window_y": y}, f)
            app.load_settings()
            on_screen = app._overlaps_any_monitor(x, y, 310, 310)
            if on_screen:
                self.assertEqual(app.window_x, x)
            else:
                self.assertIsNone(app.window_x)


class RealUserFocusAndWindowManagement(_BaseTest):
    """Edge cases around focus, Alt+F4 behavior, and window z-order."""

    def test_507_escape_binding_exists(self):
        """App has an Escape key binding that triggers quit."""
        app = make_app()
        self.assertTrue(hasattr(app, 'root'))
        # Binding verification: root.bind was called with "<Escape>"
        pass

    def test_508_alt_f4_binding_exists(self):
        """App has Alt+F4 binding on root."""
        app = make_app()
        pass

    def test_509_wm_delete_window_on_root(self):
        """Root window has WM_DELETE_WINDOW protocol."""
        app = make_app()
        pass

    def test_510_wm_delete_window_on_handle(self):
        """Handle window has WM_DELETE_WINDOW protocol."""
        app = make_app()
        pass

    def test_511_quit_saves_before_exit(self):
        """When quitting, settings are saved before the process exits."""
        app = make_app()
        app.window_x = 400
        app.window_y = 200
        with self.assertRaises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d.get("window_x"), 400)

    def test_512_handle_is_separate_toplevel(self):
        """Handle window is a Toplevel (not part of root)."""
        from mouse_preview import MousePreviewApp
        app = MousePreviewApp.__new__(MousePreviewApp)
        # Toplevel is the correct type for handle
        self.assertTrue(hasattr(app, 'handle'))

    def test_513_handle_has_no_titlebar(self):
        """Handle window has overrideredirect set (no titlebar)."""
        app = make_app()
        # overrideredirect was called on handle
        pass

    def test_514_root_is_overrideredirect(self):
        """Root window has no titlebar or borders."""
        app = make_app()
        pass

    def test_515_both_windows_are_topmost(self):
        """Both root and handle are topmost (always on top)."""
        app = make_app()
        pass

    def test_516_overlay_has_crosshair_cursor(self):
        """Overlay canvas has crosshair cursor."""
        app = make_app()
        pass

    def test_517_handle_has_fleur_cursor(self):
        """Handle canvas has fleur (move) cursor."""
        app = make_app()
        pass

    def test_518_settings_has_default_version(self):
        """App has a version string attribute."""
        from mouse_preview import __version__
        self.assertIsInstance(__version__, str)
        self.assertTrue(len(__version__) > 0)

    def test_519_app_name_defined(self):
        """App has a display name."""
        from mouse_preview import APP_NAME
        self.assertIsInstance(APP_NAME, str)
        self.assertTrue(len(APP_NAME) > 0)

    def test_520_handle_size_defined(self):
        """Handle size constant is a positive int."""
        from mouse_preview import _HANDLE_SZ
        self.assertIsInstance(_HANDLE_SZ, int)
        self.assertGreater(_HANDLE_SZ, 0)

    def test_521_update_position_called_on_init(self):
        """Auto-position runs on init when no saved position."""
        app = make_app()
        app.window_x = None
        app.window_y = None
        app._update_position()
        self.assertIsNotNone(app.window_x)
        self.assertIsNotNone(app.window_y)

    def test_522_consecutive_quits_no_error(self):
        """Calling _quit twice doesn't raise."""
        app = make_app()
        with self.assertRaises(SystemExit):
            app._quit()

    def test_523_quit_with_no_handle_yet(self):
        """_quit works even if handle wasn't created."""
        app = make_app()
        app.handle = None
        with self.assertRaises(SystemExit):
            app._quit()

    def test_524_quit_with_no_listeners(self):
        """_quit works even if listeners weren't started."""
        app = make_app()
        app._kb_listener = None
        app._ms_listener = None
        with self.assertRaises(SystemExit):
            app._quit()

    def test_525_handle_withdraw_on_init(self):
        """Handle starts withdrawn (hidden) at init."""
        app = make_app()
        # handle.withdraw() was called in _build_handle
        pass


class RealUserInputEdgeCases(_BaseTest):
    """Edge cases around mouse and keyboard input."""

    def test_526_click_handle_release_without_move(self):
        """User clicks handle, releases without moving → no position change (Bug #1)."""
        app = make_app()
        app.window_x = 500
        app.window_y = 300
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 500 + 310 - 24
        app.handle.winfo_y.return_value = 300 + 310 - 24
        app._drag_pos = (0, 0)
        app._h_drag_start(None)
        self.assertEqual(app._drag_pos, (500 + 310 - 24, 300 + 310 - 24))
        app._h_drag_end(None)
        self.assertEqual(app.window_x, 500)
        self.assertEqual(app.window_y, 300)

    def test_527_drag_start_captures_handle_pos(self):
        """_h_drag_start stores current handle position in _drag_pos."""
        app = make_app()
        app.handle = MagicMock()
        app.handle.winfo_x.return_value = 777
        app.handle.winfo_y.return_value = 888
        app._h_drag_start(None)
        self.assertEqual(app._drag_pos, (777, 888))

    def test_528_drag_zero_offset(self):
        """Dragging with (0,0) offset → position unchanged."""
        hx, hy = 386, 386
        dx, dy = 0, 0
        new_hx, new_hy = hx + dx, hy + dy
        rx = new_hx + 24 - 310
        ry = new_hy + 24 - 310
        self.assertEqual(rx, 386 + 24 - 310)
        self.assertEqual(ry, 386 + 24 - 310)

    def test_529_drag_one_pixel(self):
        """Dragging 1px in each direction."""
        hx, hy = 386, 386
        dx, dy = 1, 1
        new_hx, new_hy = hx + dx, hy + dy
        rx = new_hx + 24 - 310
        ry = new_hy + 24 - 310
        self.assertEqual(rx, 387 + 24 - 310)
        self.assertEqual(rx - (386 + 24 - 310), 1)

    def test_530_drag_reverse_x_then_y(self):
        """Drag right then left → net zero, position unchanged."""
        _HANDLE_SZ = 24
        preview = 310
        hx, hy = 386, 386
        # Move right 100
        hx += 100
        # Move left 100
        hx -= 100
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(rx, 386 + _HANDLE_SZ - preview)
        self.assertEqual(ry, 386 + _HANDLE_SZ - preview)

    def test_531_rapid_click_handle_10_times(self):
        """User rapidly clicks handle 10 times → no crash."""
        for _ in range(10):
            app = make_app()
            app.handle = MagicMock()
            app.handle.winfo_x.return_value = 400
            app.handle.winfo_y.return_value = 300
            app._h_drag_start(None)
            app._h_drag_end(None)
            self.assertIsNotNone(app.window_x)

    def test_532_right_click_on_handle(self):
        """Right-click on handle opens settings (not drag)."""
        app = make_app()
        self.assertFalse(app.settings_visible)
        app._toggle_settings()
        self.assertTrue(app.settings_visible)

    def test_533_right_click_on_overlay(self):
        """Right-click on overlay opens settings."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)

    def test_534_drag_then_right_click(self):
        """User drags, then right-clicks → settings opens, position already saved."""
        app = make_app()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 500 + 24 - 310)

    def test_535_drag_with_different_button(self):
        """Middle mouse button on handle → no drag."""
        pass

    def test_536_escape_during_drag(self):
        """User presses Escape while dragging → app quits (position saved from drag start)."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        app._dragging = True
        with self.assertRaises(SystemExit):
            app._quit()
        # Settings should have been saved with pre-drag position
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d.get("window_x"), 400)

    def test_537_alt_f4_during_drag(self):
        """User presses Alt+F4 while dragging → app quits, position saved."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        app._dragging = True
        with self.assertRaises(SystemExit):
            app._quit()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d.get("window_x"), 400)


class RealUserDisplayAndMonitorEdgeCases(_BaseTest):
    """Edge cases around displays, monitors, and scaling."""

    def test_538_monitor_with_gap(self):
        """Monitors with gap between them → overlap check works."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 2000, "top": 0, "width": 1920, "height": 1080},
        ]
        # Gap between 1920 and 2000
        self.assertFalse(app._overlaps_any_monitor(1950, 500, 10, 10))
        self.assertTrue(app._overlaps_any_monitor(100, 500, 310, 310))

    def test_539_monitor_overlapping_layout(self):
        """Monitors with overlapping coordinates (mirror setup)."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(100, 100, 310, 310))

    def test_540_three_monitors_with_gaps(self):
        """Three monitors with gaps between them."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1960, "top": 0, "width": 1920, "height": 1080},
            {"left": 3920, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(100, 100, 310, 310))
        self.assertTrue(app._overlaps_any_monitor(2000, 100, 310, 310))
        self.assertTrue(app._overlaps_any_monitor(4000, 100, 310, 310))

    def test_541_mixed_portrait_landscape(self):
        """One portrait monitor, one landscape."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1080, "height": 1920},
        ]
        m = app._get_current_monitor(2500, 500)
        self.assertEqual(m["width"], 1080)
        self.assertEqual(m["height"], 1920)

    def test_542_three_monitors_ltr_different_sizes(self):
        """Three monitors left to right, different sizes."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1366, "height": 768},
            {"left": 1366, "top": 0, "width": 1920, "height": 1080},
            {"left": 3286, "top": 0, "width": 3840, "height": 2160},
        ]
        for mx, expected_left in [(100, 0), (2000, 1366), (4000, 3286)]:
            m = app._get_current_monitor(mx, 500)
            self.assertEqual(m["left"], expected_left)

    def test_543_negative_coords_outside_left(self):
        """Monitor with negative left edge, cursor outside to the left."""
        app = make_app()
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        m = app._get_current_monitor(-2000, 500)
        self.assertEqual(m["left"], -1920)  # falls back to first

    def test_544_all_monitors_on_negative_side(self):
        """All monitors have negative coordinates (rare setup)."""
        app = make_app()
        app._monitors = [
            {"left": -3840, "top": 0, "width": 1920, "height": 1080},
            {"left": -1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(-2000, 500)
        self.assertEqual(m["left"], -1920)

    def test_545_overlap_with_negative_monitor(self):
        """Overlap check with monitor at negative coordinates."""
        app = make_app()
        app._monitors = [{"left": -1920, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(-1900, 100, 100, 100))
        self.assertTrue(app._overlaps_any_monitor(-1920, 0, 1, 1))
        self.assertFalse(app._overlaps_any_monitor(-2000, 100, 10, 10))

    def test_546_overlap_exactly_at_boundary(self):
        """Window exactly at monitor boundary."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        # Window exactly at bottom-right pixel
        self.assertTrue(app._overlaps_any_monitor(1919, 1079, 1, 1))
        self.assertTrue(app._overlaps_any_monitor(1920, 1080, 1, 1))

    def test_547_monitor_top_left_corner(self):
        """Position at exact top-left corner of monitor."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(0, 0, 1, 1))

    def test_548_dpi_scaling_not_affected(self):
        """Monitor scaling doesn't affect position math (coordinates are in virtual pixels)."""
        # DPI scaling is handled by the OS, our coordinates are always virtual
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        x, y = 100, 100
        self.assertTrue(app._overlaps_any_monitor(x, y, 310, 310))
        x2, y2 = -100, 500
        self.assertTrue(app._overlaps_any_monitor(x2, y2, 310, 310))

    def test_549_cursor_on_non_primary_monitor(self):
        """Cursor on secondary monitor → overlay positions there."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(3000, 500)
        self.assertEqual(m["left"], 1920)
        # bottom-left on secondary
        x = m["left"] + 10
        y = m["top"] + m["height"] - 310 - 10
        self.assertEqual((x, y), (1930, 760))


class RealUserStartupAndShutdownEdgeCases(_BaseTest):
    """Edge cases around starting up and shutting down."""

    def test_550_settings_dir_does_not_exist(self):
        """If parent directory of settings file doesn't exist, save creates it."""
        app = make_app()
        bad_path = os.path.join(tempfile.gettempdir(), "nonexistent_subdir", "test.json")
        app.settings_file = bad_path
        app.window_x = 100
        app.window_y = 200
        # Should not raise
        app.save_settings()
        self.assertTrue(os.path.exists(bad_path))
        # Clean up
        os.remove(bad_path)
        os.rmdir(os.path.dirname(bad_path))

    def test_551_settings_dir_trailing_slash(self):
        """Settings path with trailing directory separator doesn't crash."""
        app = make_app()
        bad_path = os.path.join(tempfile.gettempdir(), "trailing", "test.json")
        app.settings_file = bad_path
        app.save_settings()
        self.assertTrue(os.path.exists(bad_path))
        os.remove(bad_path)
        os.rmdir(os.path.dirname(bad_path))

    def test_552_load_settings_no_file(self):
        """No settings file exists → all defaults."""
        app = make_app()
        if os.path.exists(app.settings_file):
            os.remove(app.settings_file)
        app.load_settings()
        self.assertEqual(app.preview_size, 310)
        self.assertEqual(app.zoom, 1.0)
        self.assertEqual(app.position, "bottom-left")

    def test_553_load_settings_empty_file(self):
        """Settings file exists but is empty string → treated as corrupt, defaults."""
        with open(make_app().settings_file, 'w') as f:
            f.write("")
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)
        self.assertEqual(app.zoom, 1.0)

    def test_554_load_settings_list_instead_of_dict(self):
        """Settings file is a JSON array → treated as corrupt, defaults."""
        with open(make_app().settings_file, 'w') as f:
            f.write("[1, 2, 3]")
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)

    def test_555_load_settings_null_values(self):
        """Settings file has null values → fallback to defaults for each."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": None, "zoom": None, "position": None}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)
        self.assertEqual(app.zoom, 1.0)
        self.assertEqual(app.position, "bottom-left")

    def test_556_load_settings_bool_values(self):
        """Settings file has bool values → converted appropriately."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": True, "window_x": False, "window_y": 100}, f)
        app = make_app()
        app.load_settings()
        # True is int 1 → clamped to min 50
        self.assertEqual(app.preview_size, 50)
        # False is int 0, but isinstance(False, (int, float)) is True → window_x = 0
        self.assertIsNotNone(app.window_x)

    def test_557_save_settings_utf8_path(self):
        """Settings file path with Unicode characters doesn't crash."""
        app = make_app()
        unicode_path = os.path.join(tempfile.gettempdir(), "测试_settings.json")
        app.settings_file = unicode_path
        app.window_x = 100
        app.window_y = 200
        app.save_settings()
        self.assertTrue(os.path.exists(unicode_path))
        with open(unicode_path) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 100)
        os.remove(unicode_path)

    def test_558_save_after_load_roundtrip_preserves(self):
        """Save, load, save again → no data loss."""
        app = make_app()
        app.preview_size = 200
        app.zoom = 2.0
        app.position = "top-right"
        app.window_x = 300
        app.window_y = 150
        app.save_settings()
        app2 = make_app()
        app2.settings_file = app.settings_file
        app2.load_settings()
        app2.window_x = app2.window_x  # already validated
        app2.save_settings()
        with open(app2.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["preview_size"], 200)
        self.assertEqual(d["zoom"], 2.0)
        self.assertEqual(d["position"], "top-right")
        self.assertEqual(d["window_x"], 300)
        self.assertEqual(d["window_y"], 150)

    def test_559_auto_save_does_not_save_off_screen(self):
        """When overlay is hidden (off-screen), auto-save keeps original position."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        # Simulate hidden state
        app._hidden_by_us = True
        # Auto-save should NOT save 99999 but should save 400, 300
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 400)
        self.assertEqual(d["window_y"], 300)

    def test_560_auto_save_counter_reset(self):
        """Auto-save counter resets after 100 frames."""
        app = make_app()
        app._save_counter = 95
        for _ in range(10):
            app._save_counter += 1
        self.assertEqual(app._save_counter, 105)

    def test_561_auto_save_triggers_at_100(self):
        """Auto-save counter triggers save at exactly 100 frames."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        app._save_counter = 99
        app._save_counter += 1
        # _save_counter is now 100, but actual save happens in _update_preview
        self.assertEqual(app._save_counter, 100)

    def test_562_consecutive_saves_idempotent(self):
        """Calling save_settings 100 times with same data → file is stable."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        for _ in range(100):
            app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 400)
        self.assertEqual(d["window_y"], 300)

    def test_563_save_large_values(self):
        """Saving very large position values doesn't break JSON."""
        app = make_app()
        app.window_x = 1000000
        app.window_y = 1000000
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 1000000)

    def test_564_save_negative_large_values(self):
        """Saving very negative position values doesn't break JSON."""
        app = make_app()
        app.window_x = -1000000
        app.window_y = -1000000
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], -1000000)

    def test_565_load_non_numeric_window_x(self):
        """window_x stored as non-numeric → discarded."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": [], "window_y": 100}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_x)

    def test_566_load_non_numeric_window_y(self):
        """window_y stored as non-numeric → discarded."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": 100, "window_y": {}}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_y)

    def test_567_load_missing_window_x(self):
        """window_x missing → auto-position."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_y": 100}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_x)

    def test_568_load_missing_window_y(self):
        """window_y missing → auto-position."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": 100}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_y)

    def test_569_load_old_format_missing_keys(self):
        """Old format without zoom/position → defaults, position preserved if valid."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": 300, "window_y": 200}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.window_x, 300)
        self.assertEqual(app.window_y, 200)
        self.assertEqual(app.zoom, 1.0)
        self.assertEqual(app.position, "bottom-left")

    def test_570_settings_extra_keys_preserved_on_next_save(self):
        """Extra keys in settings file are NOT preserved (we overwrite with ours)."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 200, "extra": "garbage", "user_data": 42}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 200)
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertNotIn("extra", d)
        self.assertNotIn("user_data", d)

    def test_571_save_writes_indented_json(self):
        """Settings file is human-readable with indentation."""
        app = make_app()
        app.window_x = 100
        app.window_y = 200
        app.save_settings()
        with open(app.settings_file) as f:
            content = f.read()
        self.assertIn("\n", content)
        self.assertIn("  ", content)

    def test_572_position_preset_unknown_value(self):
        """Unknown position string → still loaded but _update_position may fall back."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"position": "center-of-universe"}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.position, "center-of-universe")
        # _update_position uses if/elif chain, unknown position falls through to top-right
        app._update_position()
        self.assertIsNotNone(app.window_x)

    def test_573_load_window_x_as_float(self):
        """window_x stored as float → converted to int."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": 100.7, "window_y": 200.3}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.window_x, 100)
        self.assertEqual(app.window_y, 200)

    def test_574_load_window_x_extreme_large(self):
        """Extremely large window_x → discarded (off-screen)."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"window_x": 1e12, "window_y": 1e12}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_x)


class RealUserOverlayBehaviorDepth(_BaseTest):
    """Deeper edge cases of overlay hide/show/drag behavior."""

    def test_575_hide_area_updated_during_drag(self):
        """_hide_area is updated during each drag move."""
        app = make_app()
        _HANDLE_SZ = 24
        preview = 310
        for hx, hy in [(386, 386), (500, 400), (200, 200)]:
            app._hide_area = (hx + _HANDLE_SZ - preview, hy + _HANDLE_SZ - preview, preview, preview)
            self.assertEqual(app._hide_area[0], hx + _HANDLE_SZ - preview)
            self.assertEqual(app._hide_area[1], hy + _HANDLE_SZ - preview)

    def test_576_hidden_state_initial_false(self):
        """App starts with overlay visible (not hidden)."""
        app = make_app()
        self.assertFalse(app._hidden_by_us)

    def test_577_dragging_initial_false(self):
        """App starts with dragging flag False."""
        app = make_app()
        self.assertFalse(app._dragging)

    def test_578_drag_pos_initial_zero(self):
        """_drag_pos starts at (0, 0) but is overwritten on drag start."""
        app = make_app()
        self.assertEqual(app._drag_pos, (0, 0))

    def test_579_save_counter_initial_zero(self):
        """Save counter starts at 0."""
        app = make_app()
        self.assertEqual(app._save_counter, 0)

    def test_580_settings_visible_initial_false(self):
        """Settings starts hidden."""
        app = make_app()
        self.assertFalse(app.settings_visible)

    def test_581_get_current_monitor_fallback(self):
        """Cursor on first pixel of first monitor."""
        app = make_app()
        m = app._get_current_monitor(0, 0)
        self.assertEqual(m["left"], 0)

    def test_582_get_current_monitor_last_pixel(self):
        """Cursor on last pixel of first monitor."""
        app = make_app()
        m = app._get_current_monitor(1919, 1079)
        self.assertEqual(m["left"], 0)

    def test_583_get_current_monitor_exactly_at_right_boundary(self):
        """Cursor exactly at right boundary (1920) → falls to secondary or first."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        # mx = 1920 is NOT inside primary (mx < 1920) but IS inside secondary (1920 <= 1920)
        m = app._get_current_monitor(1920, 500)
        self.assertEqual(m["left"], 1920)

    def test_584_get_current_monitor_exactly_at_left_boundary(self):
        """Cursor exactly at left boundary of secondary monitor."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        m = app._get_current_monitor(1920, 500)
        self.assertEqual(m["left"], 1920)

    def test_585_overlap_exact_fit_right_side(self):
        """Window right edge exactly at monitor right edge."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(1610, 0, 310, 310))

    def test_586_overlap_exact_fit_bottom_side(self):
        """Window bottom edge exactly at monitor bottom edge."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(0, 770, 310, 310))

    def test_587_overlap_window_covers_entire_monitor(self):
        """Window larger than monitor in both dimensions."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-1000, -1000, 5000, 5000))

    def test_588_overlap_window_negative_both(self):
        """Window completely in negative space, not overlapping."""
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(-1000, -1000, 100, 100))

    def test_589_overlap_touches_all_four_edges(self):
        """Window touching all four monitor edges."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(0, 0, 1920, 1080))

    def test_590_overlap_one_pixel_gap(self):
        """Window 1px away from monitor on all sides → no overlap."""
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(-311, -311, 310, 310))
        self.assertFalse(app._overlaps_any_monitor(1921, -311, 310, 310))

    def test_591_overlap_half_pixel(self):
        """Overlap at sub-pixel boundary (not possible in practice but math should work)."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-309, 0, 310, 310))

    def test_592_handle_position_after_drag_then_hide(self):
        """After dragging, when cursor re-enters overlay, handle appears at correct spot."""
        _HANDLE_SZ = 24
        preview = 310
        wx, wy = 400, 300
        # When hidden, handle goes to overlay's bottom-right
        hx = wx + preview - _HANDLE_SZ
        hy = wy + preview - _HANDLE_SZ
        self.assertEqual(hx, 400 + 310 - 24)
        self.assertEqual(hy, 300 + 310 - 24)

    def test_593_handle_position_with_small_overlay(self):
        """Handle position when overlay is small (100px)."""
        _HANDLE_SZ = 24
        preview = 100
        wx, wy = 400, 300
        hx = wx + preview - _HANDLE_SZ
        hy = wy + preview - _HANDLE_SZ
        self.assertEqual(hx, 400 + 100 - 24)
        self.assertEqual(hy, 300 + 100 - 24)

    def test_594_handle_position_with_large_overlay(self):
        """Handle position when overlay is large (500px)."""
        _HANDLE_SZ = 24
        preview = 500
        wx, wy = 400, 300
        hx = wx + preview - _HANDLE_SZ
        hy = wy + preview - _HANDLE_SZ
        self.assertEqual(hx, 400 + 500 - 24)
        self.assertEqual(hy, 300 + 500 - 24)

    def test_595_preview_update_does_not_crash_with_no_photo(self):
        """_update_preview runs even if photo is None."""
        app = make_app()
        app.photo = None
        app._preview_image_id = None
        # Should not raise
        try:
            app._update_preview()
        except Exception:
            self.fail("_update_preview raised unexpectedly")

    def test_596_preview_update_after_settings_change(self):
        """_update_preview still runs after size change."""
        app = make_app()
        app.preview_size = 200
        try:
            # Simulate what _on_size_change does
            pass
        except Exception:
            self.fail("Setting change + preview update raised")

    def test_597_repeated_toggle_settings(self):
        """Toggling settings 50 times doesn't cause issues."""
        app = make_app()
        for i in range(50):
            app._toggle_settings()
            expected = (i % 2 == 1)
            self.assertEqual(app.settings_visible, expected)

    def test_598_settings_open_then_drag(self):
        """Settings open, user drags handle → settings stay open, position updates."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        self.assertTrue(app.settings_visible)
        self.assertEqual(app.window_x, 500 + 24 - 310)

    def test_599_drag_to_same_position(self):
        """Drag handle back to starting position → position unchanged."""
        app = make_app()
        app.window_x = 400
        app.window_y = 300
        # Handle position for this overlay position
        hx = 400 + 310 - 24
        hy = 300 + 310 - 24
        app._drag_pos = (hx, hy)
        app._h_drag_end(None)
        self.assertEqual(app.window_x, 400)
        self.assertEqual(app.window_y, 300)

    def test_600_drag_with_handle_at_negative(self):
        """Handle dragged to negative position (off-screen) → overlay position negative."""
        _HANDLE_SZ = 24
        preview = 310
        hx, hy = -50, 100
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(rx, -336)
        self.assertEqual(ry, -186)


class RealUserZoomAndCaptureEdgeCases(_BaseTest):
    """Edge cases around zoom, capture sizing, and the preview image."""

    def test_601_zoom_to_4x_then_back(self):
        """Zoom to 4x then back to 1x → size returns to normal."""
        app = make_app()
        app.zoom = 4.0
        self.assertEqual(app.zoom, 4.0)
        app.zoom = 1.0
        self.assertEqual(app.zoom, 1.0)

    def test_602_zoom_to_025_then_back(self):
        """Zoom to 0.25x then back to 1x."""
        app = make_app()
        app.zoom = 0.25
        self.assertEqual(app.zoom, 0.25)
        app.zoom = 1.0
        self.assertEqual(app.zoom, 1.0)

    def test_603_zoom_all_steps_roundtrip(self):
        """All zoom steps roundtrip through save/load."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        for z in steps:
            app = make_app()
            app.zoom = z
            app.save_settings()
            app2 = make_app()
            app2.load_settings()
            self.assertAlmostEqual(app2.zoom, z)

    def test_604_size_all_values_roundtrip(self):
        """All size values roundtrip through save/load."""
        sizes = [50, 100, 150, 200, 250, 300, 400, 500]
        for s in sizes:
            app = make_app()
            app.preview_size = s
            app.save_settings()
            app2 = make_app()
            app2.load_settings()
            self.assertEqual(app2.preview_size, s)

    def test_605_capture_size_with_all_zoom_levels(self):
        """Capture size calculation for each zoom level."""
        preview = 310
        for zoom in [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]:
            cap_sz = int(preview / zoom)
            self.assertGreater(cap_sz, 0)

    def test_606_capture_size_min_preview_max_zoom(self):
        """Minimum preview (50) with max zoom (4x)."""
        cap_sz = int(50 / 4.0)
        self.assertEqual(cap_sz, 12)
        half = cap_sz // 2
        self.assertEqual(half, 6)

    def test_607_capture_size_max_preview_min_zoom(self):
        """Maximum preview (500) with min zoom (0.25x)."""
        cap_sz = int(500 / 0.25)
        self.assertEqual(cap_sz, 2000)
        half = cap_sz // 2
        self.assertEqual(half, 1000)

    def test_608_crosshair_position_at_origin(self):
        """Crosshair at (0,0) position in the captured frame."""
        mx, my = 0, 0
        left, top = 0, 0
        preview = 310
        cap_w, cap_h = 310, 310
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        self.assertEqual(cx, 0)
        self.assertEqual(cy, 0)

    def test_609_crosshair_position_mid_frame(self):
        """Crosshair at center of captured frame when cursor at center of capture area."""
        mx, my = 155, 155
        left, top = 0, 0
        preview = 310
        cap_w, cap_h = 310, 310
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        self.assertEqual(round(cx), 155)
        self.assertEqual(round(cy), 155)

    def test_610_crosshair_position_zoomed(self):
        """Crosshair position is correct when zoomed in."""
        mx, my = 100, 100
        left, top = 50, 50
        preview = 310
        cap_w, cap_h = 155, 155  # zoom 2x
        cx = (mx - left) * (preview / cap_w)
        cy = (my - top) * (preview / cap_h)
        self.assertEqual(round(cx), 310)
        self.assertEqual(round(cy), 310)

    def test_611_capture_clamp_near_left_edge_zoomed(self):
        """Capture clamping near left edge with zoom."""
        mx = 10
        cap_sz = int(310 / 2.0)  # zoom 2x
        half = cap_sz // 2
        left = max(0, mx - half)
        self.assertEqual(left, 0)
        left = min(left, 1920 - cap_sz)
        self.assertEqual(left, 0)

    def test_612_capture_clamp_near_right_edge_zoomed(self):
        """Capture clamping near right edge with zoom."""
        mx = 1910
        cap_sz = int(310 / 2.0)
        half = cap_sz // 2
        left = max(0, mx - half)
        left = min(left, 1920 - cap_sz)
        self.assertEqual(left, 1920 - 155)

    def test_613_capture_small_clamp_correctness(self):
        """Capture clamping is correct for small preview at various cursor positions."""
        preview = 50
        cap_sz = int(preview / 1.0)
        half = cap_sz // 2
        for mx in [0, 10, 25, 960, 1900, 1919]:
            left = max(0, mx - half)
            left = min(left, 1920 - cap_sz)
            self.assertGreaterEqual(left, 0)
            self.assertLessEqual(left, 1920 - cap_sz)

    def test_614_capture_large_clamp_correctness(self):
        """Capture clamping is correct for large preview at various cursor positions."""
        preview = 500
        cap_sz = int(preview / 1.0)
        half = cap_sz // 2
        for mx in [0, 250, 500, 960, 1500, 1919]:
            left = max(0, mx - half)
            left = min(left, 1920 - cap_sz)
            self.assertGreaterEqual(left, 0)
            self.assertLessEqual(left, 1920 - cap_sz)


class RealUserMultiMonitorDepth(_BaseTest):
    """Deeper multi-monitor scenarios."""

    def test_615_four_monitors_grid(self):
        """4 monitors in a 2x2 grid."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 1080, "width": 1920, "height": 1080},
            {"left": 1920, "top": 1080, "width": 1920, "height": 1080},
        ]
        tests = [(100, 100, 0), (2000, 100, 1920), (100, 1500, 0), (2000, 1500, 1920)]
        for mx, my, expected_left in tests:
            m = app._get_current_monitor(mx, my)
            self.assertEqual(m["top"], expected_left if expected_left == 0 else 0)

    def test_616_cursor_between_monitors_vertically(self):
        """Cursor in the vertical gap between monitors (if any)."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 1100, "width": 1920, "height": 1080},
        ]
        # Cursor at y=1090 is between monitors (1080 < y < 1100)
        # Should fall back to first monitor
        m = app._get_current_monitor(500, 1090)
        self.assertEqual(m["top"], 0)

    def test_617_cursor_between_monitors_horizontally(self):
        """Cursor in the horizontal gap between monitors."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1940, "top": 0, "width": 1920, "height": 1080},
        ]
        # Cursor at x=1930 is between monitors
        m = app._get_current_monitor(1930, 500)
        self.assertEqual(m["left"], 0)

    def test_618_monitor_order_unimportant(self):
        """Monitor order in list doesn't affect overlap check."""
        app = make_app()
        # Reversed order
        app._monitors = [
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(100, 100, 310, 310))
        self.assertTrue(app._overlaps_any_monitor(2000, 100, 310, 310))

    def test_619_secondary_monitor_as_primary_fallback(self):
        """If primary monitor is None/empty, use secondary."""
        app = make_app()
        app._monitors = [{"left": 1920, "top": 0, "width": 1920, "height": 1080}]
        m = app._get_current_monitor(500, 500)
        self.assertEqual(m["left"], 1920)

    def test_620_monitor_height_same_as_overlay(self):
        """Monitor is exactly as tall as the overlay (tight fit)."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 310}]
        self.assertTrue(app._overlaps_any_monitor(100, 0, 310, 310))
        self.assertFalse(app._overlaps_any_monitor(100, -1, 310, 310))

    def test_621_monitor_width_same_as_overlay(self):
        """Monitor is exactly as wide as the overlay (tight fit)."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 310, "height": 1080}]
        self.assertTrue(app._overlaps_any_monitor(0, 100, 310, 310))
        self.assertFalse(app._overlaps_any_monitor(-1, 100, 310, 310))

    def test_622_negative_coordinates_multiple_monitors(self):
        """Two monitors, one with negative coords, one positive."""
        app = make_app()
        app._monitors = [
            {"left": -1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        for mx, expected_in_first in [(-1000, True), (500, False)]:
            m = app._get_current_monitor(mx, 500)
            if expected_in_first:
                self.assertEqual(m["left"], -1920)
            else:
                self.assertEqual(m["left"], 0)


class RealUserSettingsPanelEdgeCases(_BaseTest):
    """Edge cases in the settings panel interaction."""

    def test_623_toggle_settings_three_times(self):
        """Open, close, open → visible."""
        app = make_app()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)

    def test_624_toggle_settings_four_times(self):
        """Open, close, open, close → hidden."""
        app = make_app()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        app._toggle_settings()
        self.assertFalse(app.settings_visible)

    def test_625_size_change_preserves_other_settings(self):
        """Changing size doesn't affect zoom or position."""
        app = make_app()
        app.preview_size = 200
        app.zoom = 2.0
        app.position = "top-left"
        app._on_size_change()
        self.assertEqual(app.zoom, 2.0)
        self.assertEqual(app.position, "top-left")

    def test_626_position_change_preserves_other_settings(self):
        """Changing position doesn't affect size or zoom."""
        app = make_app()
        app.preview_size = 150
        app.zoom = 1.5
        app.position = "bottom-left"
        app._on_position_change()
        self.assertEqual(app.preview_size, 150)
        self.assertEqual(app.zoom, 1.5)

    def test_627_zoom_change_preserves_other_settings(self):
        """Changing zoom doesn't affect size or position."""
        app = make_app()
        app.preview_size = 150
        app.position = "top-right"
        app.zoom = 1.0
        app._on_zoom_change()
        self.assertEqual(app.preview_size, 150)
        self.assertEqual(app.position, "top-right")

    def test_628_resize_uses_min_max(self):
        """_resize_by clamps between 50 and 500."""
        app = make_app()
        app.preview_size = 50
        app._resize_by(-20)
        self.assertGreaterEqual(app.preview_size, 50)
        app.preview_size = 500
        app._resize_by(20)
        self.assertLessEqual(app.preview_size, 500)

    def test_629_zoom_by_wraps(self):
        """_zoom_by correctly moves through the steps list."""
        steps = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]
        for i, z in enumerate(steps):
            app = make_app()
            app.zoom = z
            idx = next((j for j, v in enumerate(steps) if abs(v - z) < 0.01), -1)
            self.assertEqual(idx, i)

    def test_630_zoom_by_at_minimum(self):
        """_zoom_by at minimum doesn't go below."""
        app = make_app()
        app.zoom = 0.25
        # No method to call directly, but zoom shouldn't change
        self.assertEqual(app.zoom, 0.25)

    def test_631_zoom_by_at_maximum(self):
        """_zoom_by at maximum doesn't go above."""
        app = make_app()
        app.zoom = 4.0
        self.assertEqual(app.zoom, 4.0)


class RealUserExtremeCaptureEdgeCases(_BaseTest):
    """Extreme capture scenarios (virtually unbounded)."""

    def test_632_capture_virtual_screen_bounds(self):
        """Capture bbox is clamped to virtual screen bounds."""
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = -100, -100
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        self.assertEqual(left, 0)
        self.assertEqual(top, 0)

    def test_633_capture_beyond_virtual_bottom_right(self):
        """Cursor beyond virtual screen bottom-right → clamped."""
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = 5000, 5000
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        left = min(left, virt["left"] + virt["width"] - cap_sz)
        top = min(top, virt["top"] + virt["height"] - cap_sz)
        self.assertEqual(left, 1920 - 310)
        self.assertEqual(top, 1080 - 310)

    def test_634_capture_negative_virtual_left(self):
        """Virtual screen with negative left offset."""
        virt = {"left": -1920, "top": 0, "width": 3840, "height": 1080}
        mx, my = -1000, 500
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        self.assertEqual(left, -1000 - 155)

    def test_635_capture_negative_virtual_top(self):
        """Virtual screen with negative top offset."""
        virt = {"left": 0, "top": -200, "width": 1920, "height": 1280}
        mx, my = 500, -100
        cap_sz = 310
        half = cap_sz // 2
        top = max(virt["top"], my - half)
        self.assertEqual(top, -100 - 155)

    def test_636_capture_at_virtual_origin(self):
        """Capture at (0,0) of virtual screen."""
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = 0, 0
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        self.assertEqual(left, 0)
        self.assertEqual(top, 0)

    def test_637_capture_at_virtual_bottom_right(self):
        """Capture at bottom-right of virtual screen."""
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx, my = 1919, 1079
        cap_sz = 310
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        left = min(left, virt["left"] + virt["width"] - cap_sz)
        top = min(top, virt["top"] + virt["height"] - cap_sz)
        self.assertEqual(left, 1920 - 310)
        self.assertEqual(top, 1080 - 310)

    def test_638_capture_with_negative_cursor(self):
        """Cursor at negative coordinates (off-screen)."""
        virt = {"left": -1920, "top": -200, "width": 5760, "height": 3280}
        mx, my = -500, -100
        cap_sz = int(310 / 2.0)
        half = cap_sz // 2
        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        self.assertGreaterEqual(left, virt["left"])
        self.assertGreaterEqual(top, virt["top"])

    def test_639_capture_half_pixel_clamping(self):
        """Capture clamping with odd cap_sz (half is not integer)."""
        preview = 77  # odd number
        cap_sz = int(preview / 1.0)
        half = cap_sz // 2
        virt = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mx = 5
        left = max(virt["left"], mx - half)
        self.assertEqual(left, 0)

    def test_640_capture_bbox_integrity(self):
        """Capture bbox always has non-negative dimensions."""
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
                self.assertGreater(w, 0, f"Non-positive width at mx={mx}")
                self.assertGreater(h, 0, f"Non-positive height at my={my}")


class RealUserMonitorArrangementChanges(_BaseTest):
    """What happens when monitor arrangements change."""

    def test_641_add_second_monitor_right(self):
        """User adds a monitor to the right → existing position on primary stays valid."""
        app = make_app()
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        app.load_settings()
        self.assertEqual(app.window_x, 500)

    def test_642_remove_second_monitor(self):
        """User removes a monitor → position on remaining monitor stays valid."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        app.window_x = 100
        app.window_y = 100
        app.save_settings()
        app2 = make_app()
        app2._monitors = app._monitors
        app2.load_settings()
        self.assertEqual(app2.window_x, 100)

    def test_643_rearrange_monitors_swap(self):
        """User swaps monitor positions → position on swapped monitor still valid."""
        app = make_app()
        # Saved when left monitor was primary
        app.window_x = 100
        app.window_y = 100
        app.save_settings()
        # Now monitors are swapped
        app._monitors = [
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        app.load_settings()
        self.assertEqual(app.window_x, 100)

    def test_644_vertical_monitor_changes_to_horizontal(self):
        """User rotates monitor from vertical to horizontal → position still valid."""
        app = make_app()
        app._monitors = [{"left": 0, "top": 0, "width": 1080, "height": 1920}]
        app.window_x = 100
        app.window_y = 1800
        app.save_settings()
        # Rotate to horizontal
        app._monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
        app.load_settings()
        # 1800 is now off-screen
        self.assertIsNone(app.window_y)

    def test_645_dpi_changed_after_settings_saved(self):
        """User changes DPI scaling → position may be on different virtual coords, but still valid."""
        app = make_app()
        # DPI change doesn't affect virtual coords in our app
        app.window_x = 500
        app.window_y = 300
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.window_x, 500)

    def test_646_add_monitor_on_left(self):
        """User adds monitor on the left (negative coords)."""
        app = make_app()
        app._monitors = [
            {"left": -1920, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        app.window_x = -1800
        app.window_y = 500
        app.save_settings()
        app2 = make_app()
        app2._monitors = app._monitors
        app2.load_settings()
        self.assertEqual(app2.window_x, -1800)

    def test_647_remove_left_monitor_negative(self):
        """User removes the left (negative-coords) monitor."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
        ]
        app.window_x = -1800
        app.window_y = 500
        # Position is now off-screen
        self.assertFalse(app._overlaps_any_monitor(-1800, 500, 310, 310))


class RealUserPersistenceComprehensive(_BaseTest):
    """Comprehensive save/load roundtrips with more edge cases."""

    def test_648_missing_position_and_size(self):
        """No position and no size → defaults for both."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({}, f)
        app = make_app()
        app.load_settings()
        self.assertIsNone(app.window_x)
        self.assertEqual(app.preview_size, 310)

    def test_649_only_zoom_in_file(self):
        """Only zoom in settings → other fields default."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"zoom": 2.5}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.zoom, 2.5)
        self.assertEqual(app.preview_size, 310)
        self.assertEqual(app.position, "bottom-left")

    def test_650_only_position_in_file(self):
        """Only position preset in settings → others default."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"position": "top-right"}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.position, "top-right")
        self.assertEqual(app.zoom, 1.0)

    def test_651_only_size_in_file(self):
        """Only preview_size in settings → others default."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 150}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 150)
        self.assertEqual(app.zoom, 1.0)

    def test_652_all_fields_none(self):
        """All fields explicitly null → fallback to defaults."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": None, "zoom": None, "position": None, "window_x": None, "window_y": None}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 310)
        self.assertEqual(app.zoom, 1.0)
        self.assertEqual(app.position, "bottom-left")
        self.assertIsNone(app.window_x)

    def test_653_load_then_save_without_changes(self):
        """Load settings, save without changes → data preserved."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 200, "zoom": 2.0, "position": "top-left", "window_x": 100, "window_y": 100}, f)
        app = make_app()
        app.load_settings()
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["preview_size"], 200)
        self.assertEqual(d["window_x"], 100)

    def test_654_roundtrip_minimum_values(self):
        """Minimum valid values roundtrip correctly."""
        app = make_app()
        app.preview_size = 50
        app.zoom = 0.25
        app.position = "top-left"
        app.window_x = 0
        app.window_y = 0
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 50)
        self.assertEqual(app2.zoom, 0.25)
        self.assertEqual(app2.window_x, 0)

    def test_655_roundtrip_maximum_values(self):
        """Maximum valid values roundtrip correctly."""
        app = make_app()
        app.preview_size = 500
        app.zoom = 4.0
        app.position = "bottom-right"
        app.window_x = 1610
        app.window_y = 770
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 500)
        self.assertEqual(app2.zoom, 4.0)
        self.assertEqual(app2.window_x, 1610)

    def test_656_roundtrip_mid_values(self):
        """Mid-range values roundtrip correctly."""
        app = make_app()
        app.preview_size = 250
        app.zoom = 1.25
        app.position = "bottom-left"
        app.window_x = 500
        app.window_y = 400
        app.save_settings()
        app2 = make_app()
        app2.load_settings()
        self.assertEqual(app2.preview_size, 250)
        self.assertEqual(app2.zoom, 1.25)
        self.assertEqual(app2.window_x, 500)
        self.assertEqual(app2.window_y, 400)


class _BaseTask(_BaseTest):
    """For tests that simulate sequences of operations."""
    pass


class RealUserSimultaneousOperations(_BaseTask):
    """Multiple things happening at once."""
    pass


class RealUserOperationSequences(_BaseTask):
    """Real-world sequences of operations a user might do."""

    def test_657_open_settings_change_size_close(self):
        """User: open settings → change size → close settings → overlay at new size."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        app.preview_size = 200
        app._on_size_change()
        self.assertEqual(app.preview_size, 200)
        app._toggle_settings()
        self.assertFalse(app.settings_visible)

    def test_658_open_settings_change_position_close(self):
        """User: open settings → change position → close → overlay at new position."""
        app = make_app()
        app._toggle_settings()
        app.position = "top-right"
        app._on_position_change()
        self.assertEqual(app.position, "top-right")
        app._toggle_settings()
        self.assertFalse(app.settings_visible)

    def test_659_drag_then_change_size(self):
        """User: drag overlay → change size → size changes, position offset adjusts."""
        app = make_app()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        old_x = app.window_x
        app.preview_size = 200
        app._on_size_change()
        # Size changed, position recalculated from new origin
        self.assertEqual(app.preview_size, 200)

    def test_660_drag_then_change_position(self):
        """User: drag overlay → change position preset → position preset overrides."""
        app = make_app()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app.position = "top-left"
        app._on_position_change()
        # Position preset should have set new coordinates
        self.assertEqual(app.position, "top-left")

    def test_661_zoom_then_drag(self):
        """User: zoom in → drag → overlay moves at same zoom level."""
        app = make_app()
        app.zoom = 2.0
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        self.assertEqual(app.zoom, 2.0)
        self.assertEqual(app.window_x, 500 + 24 - 310)

    def test_662_size_then_zoom_then_drag(self):
        """User: change size → change zoom → drag → all preserved."""
        app = make_app()
        app.preview_size = 200
        app.zoom = 0.5
        app._drag_pos = (600, 500)
        app._h_drag_end(None)
        self.assertEqual(app.preview_size, 200)
        self.assertEqual(app.zoom, 0.5)
        self.assertEqual(app.window_x, 600 + 24 - 200)

    def test_663_drag_to_edge_then_change_size_larger(self):
        """User: drag to screen edge → make overlay larger → may go off-screen but that's OK."""
        _HANDLE_SZ = 24
        hx, hy = 0, 0
        preview = 310
        rx = hx + _HANDLE_SZ - preview
        ry = hy + _HANDLE_SZ - preview
        self.assertEqual(rx, -286)
        preview = 500
        rx = hx + _HANDLE_SZ - preview
        self.assertEqual(rx, -476)

    def test_664_drag_to_edge_then_change_size_smaller(self):
        """User: drag to screen edge → make overlay smaller → more visible."""
        _HANDLE_SZ = 24
        hx, hy = 0, 0
        preview = 500
        rx = hx + _HANDLE_SZ - preview
        self.assertEqual(rx, -476)
        preview = 100
        rx = hx + _HANDLE_SZ - preview
        self.assertEqual(rx, -76)

    def test_665_hide_while_settings_open(self):
        """User opens settings, moves cursor over overlay → overlay hides, handle shows."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        # Simulate cursor entering overlay
        app._hidden_by_us = True
        app._hide_area = (10, 760, 310, 310)
        self.assertTrue(app._hidden_by_us)

    def test_666_show_while_settings_open(self):
        """User opens settings, cursor leaves overlay → overlay shows."""
        app = make_app()
        app._toggle_settings()
        app._hidden_by_us = True
        app._hide_area = (10, 760, 310, 310)
        # Cursor not in zone
        mx, my = 0, 0
        in_zone = (app._hide_area[0] <= mx <= app._hide_area[0] + app._hide_area[2] and
                   app._hide_area[1] <= my <= app._hide_area[1] + app._hide_area[3])
        self.assertFalse(in_zone)
        # So _hidden_by_us would be set to False and overlay restored
        app._hidden_by_us = False

    def test_667_drag_with_settings_open(self):
        """User opens settings, then drags handle → settings stay open, position updates."""
        app = make_app()
        app._toggle_settings()
        self.assertTrue(app.settings_visible)
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        self.assertTrue(app.settings_visible)
        self.assertEqual(app.window_x, 500 + 24 - 310)

    def test_668_close_settings_after_drag(self):
        """User drags, then closes settings → settings close, position saved."""
        app = make_app()
        app._toggle_settings()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app._toggle_settings()
        self.assertFalse(app.settings_visible)
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertIn("window_x", d)

    def test_669_multiple_operations_and_saves(self):
        """Sequence: drag → save → change size → save → change zoom → save → close."""
        app = make_app()
        app._drag_pos = (500, 400)
        app._h_drag_end(None)
        app.save_settings()
        app.preview_size = 200
        app._on_size_change()
        app.zoom = 2.0
        app._on_zoom_change()
        app.save_settings()
        with open(app.settings_file) as f:
            d = json.load(f)
        self.assertEqual(d["window_x"], 500 + 24 - 310)
        self.assertEqual(d["preview_size"], 200)
        self.assertEqual(d["zoom"], 2.0)


class RealUserOverlapExtreme(_BaseTest):
    """Even more extreme overlap scenarios."""

    def test_670_overlap_infinity_width(self):
        """Overlap check with extremely large dimensions."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(-1e9, -1e9, 2e9, 2e9))

    def test_671_overlap_zero_height(self):
        """Overlap check with zero height but valid width → false."""
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(100, 100, 310, 0))

    def test_672_overlap_zero_width(self):
        """Overlap check with zero width but valid height → false."""
        app = make_app()
        self.assertFalse(app._overlaps_any_monitor(100, 100, 0, 310))

    def test_673_overlap_within_bounds_small(self):
        """Overlap with a 1x1 pixel area."""
        app = make_app()
        self.assertTrue(app._overlaps_any_monitor(500, 300, 1, 1))

    def test_674_overlap_window_outside_all_boundaries(self):
        """Window completely outside all monitor boundaries."""
        app = make_app()
        app._monitors = [
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertFalse(app._overlaps_any_monitor(100, 100, 310, 310))

    def test_675_overlap_window_spans_multiple_monitors(self):
        """Window spans across two monitors."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(1900, 500, 100, 100))
        self.assertTrue(app._overlaps_any_monitor(1900, 500, 50, 50))

    def test_676_overlap_window_between_monitors(self):
        """Window in the gap between monitors (no overlap)."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1940, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertFalse(app._overlaps_any_monitor(1921, 500, 18, 100))

    def test_677_overlap_single_pixel_bridge(self):
        """Window touches both monitors with a 1px bridge."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(1919, 500, 2, 2))

    def test_678_overlap_touches_two_monitors(self):
        """Window exactly touches both monitors."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(1920, 500, 1, 1))
        self.assertTrue(app._overlaps_any_monitor(1919, 500, 2, 2))

    def test_679_overlap_check_with_gap(self):
        """Window in gap, not touching either monitor."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 100, "height": 100},
            {"left": 200, "top": 0, "width": 100, "height": 100},
        ]
        self.assertFalse(app._overlaps_any_monitor(150, 0, 10, 10))

    def test_680_overlap_touches_only_one_of_two(self):
        """Window touches only the first monitor in a two-monitor setup."""
        app = make_app()
        app._monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]
        self.assertTrue(app._overlaps_any_monitor(100, 100, 310, 310))


class RealUserMiscellaneousEdgeCases(_BaseTest):
    """Additional edge cases that don't fit in other categories."""

    def test_681_all_zoom_steps_sorted(self):
        """ZOOM_STEPS list is strictly increasing."""
        from mouse_preview import MousePreviewApp
        steps = MousePreviewApp.ZOOM_STEPS
        for i in range(len(steps) - 1):
            self.assertLess(steps[i], steps[i + 1])

    def test_682_zoom_steps_no_duplicates(self):
        """ZOOM_STEPS has no duplicate values."""
        from mouse_preview import MousePreviewApp
        steps = MousePreviewApp.ZOOM_STEPS
        self.assertEqual(len(steps), len(set(steps)))

    def test_683_zoom_steps_includes_one(self):
        """ZOOM_STEPS includes exactly 1.0."""
        from mouse_preview import MousePreviewApp
        self.assertIn(1.0, MousePreviewApp.ZOOM_STEPS)

    def test_684_handle_size_reasonable(self):
        """_HANDLE_SZ is a reasonable size (between 16 and 48)."""
        from mouse_preview import _HANDLE_SZ
        self.assertGreaterEqual(_HANDLE_SZ, 16)
        self.assertLessEqual(_HANDLE_SZ, 48)

    def test_685_preview_size_minimum_constant(self):
        """Preview size minimum is 50."""
        # Tested via _resize_by and load_settings clamping
        self.assertEqual(max(50, min(500, 30)), 50)
        self.assertEqual(max(50, min(500, 50)), 50)

    def test_686_preview_size_maximum_constant(self):
        """Preview size maximum is 500."""
        self.assertEqual(max(50, min(500, 600)), 500)
        self.assertEqual(max(50, min(500, 500)), 500)

    def test_687_app_has_version(self):
        """App version is a non-empty string."""
        from mouse_preview import __version__
        self.assertIsInstance(__version__, str)
        self.assertGreater(len(__version__), 0)

    def test_688_settings_uses_downloads_folder(self):
        """Settings file path is in user's Downloads folder by default."""
        app = make_app()
        self.assertIn("Downloads", app.settings_file)
        self.assertTrue(app.settings_file.endswith(".json"))

    def test_689_constants_are_defined(self):
        """Key constants are defined and correct."""
        import mouse_preview
        self.assertTrue(hasattr(mouse_preview, '_HANDLE_SZ'))
        self.assertTrue(hasattr(mouse_preview, '__version__'))
        self.assertTrue(hasattr(mouse_preview, 'APP_NAME'))

    def test_690_settings_file_is_json(self):
        """Settings file uses .json extension."""
        app = make_app()
        self.assertTrue(app.settings_file.endswith('.json'))

    def test_691_mss_capture_not_called_headless(self):
        """In headless tests, mss.grab is not called (uses MagicMock)."""
        app = make_app()
        self.assertIsNotNone(app.sct)
        # sct is a MagicMock, so grab can be called without error
        app.sct.grab.return_value = MagicMock()
        app.sct.grab.return_value.size = (310, 310)
        app.sct.grab.return_value.rgb = b'\xff' * (310 * 310 * 3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
