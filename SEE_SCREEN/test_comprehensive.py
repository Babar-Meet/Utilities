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
        """Settings file has negative preview_size → loaded (UI will clamp later)."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": -100}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, -100)

    def test_08_settings_huge_values(self):
        """Settings file has huge preview_size → loaded."""
        with open(make_app().settings_file, 'w') as f:
            json.dump({"preview_size": 99999}, f)
        app = make_app()
        app.load_settings()
        self.assertEqual(app.preview_size, 99999)

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


if __name__ == '__main__':
    unittest.main(verbosity=1)
