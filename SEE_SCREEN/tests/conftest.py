"""
Shared test fixtures, mocks, and utilities for Dr Broken Display tests.

Usage::

    def test_something(app, settings_file):
        assert app.preview_size == 310
        app.window_x = 100
        app.save_settings()
        assert os.path.exists(settings_file)
"""

import sys
import os
import json
import tempfile
from unittest.mock import MagicMock, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest


# ── Mock tkinter classes ──────────────────────────────────

class _MockTk:
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


@pytest.fixture(scope="function")
def mock_tk():
    """
    Monkey-patches tkinter with headless mocks so tests can run
    without a display server.
    """
    import mouse_preview as mp
    original_tk = mp.tk
    mp.tk = _MockTk
    yield mp.tk
    mp.tk = original_tk


def _make_raw_app():
    """
    Create a bare MousePreviewApp instance without running __init__.
    Caller must set up all required attributes.
    """
    import mouse_preview as mp
    app = mp.MousePreviewApp.__new__(mp.MousePreviewApp)
    app.root = _MockTk.Tk()
    app.sct = MagicMock()
    app.sct.monitors = [
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
    ]
    app._virtual = app.sct.monitors[0]
    app._monitors = app.sct.monitors[1:]
    return app


@pytest.fixture(scope="function")
def settings_file():
    """
    Provides a temporary JSON file path for settings persistence tests.
    Cleans up after the test.
    """
    path = os.path.join(tempfile.gettempdir(), "dr_broken_test_settings.json")
    if os.path.exists(path):
        os.remove(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture(scope="function")
def app(mock_tk, settings_file):
    """
    Fully-initialized test app with mocks, ready for testing.
    Starts with default settings; does NOT call mainloop.
    """
    app = _make_raw_app()
    app.settings_file = settings_file
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
    app.settings_frame = _MockTk.Frame()
    app.canvas = _MockTk.Canvas()
    app.canvas.pack_forget = lambda: None
    app.size_var = _MockTk.IntVar(value=app.preview_size)
    app.pos_var = _MockTk.StringVar(value=app.position)
    app.zoom_var = _MockTk.DoubleVar(value=app.zoom)
    return app


def make_app():
    """
    Quick helper for unittest-style tests that don't use pytest fixtures.
    Creates a bare app with default state.
    """
    import mouse_preview as mp
    app = mp.MousePreviewApp.__new__(mp.MousePreviewApp)
    app.root = _MockTk.Tk()
    app.sct = MagicMock()
    app.sct.monitors = [
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
    ]
    app._virtual = app.sct.monitors[0]
    app._monitors = app.sct.monitors[1:]
    app.settings_file = os.path.join(tempfile.gettempdir(), "dr_broken_test_instance.json")
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
    app.settings_frame = _MockTk.Frame()
    app.canvas = _MockTk.Canvas()
    app.canvas.pack_forget = lambda: None
    app.size_var = _MockTk.IntVar(value=app.preview_size)
    app.pos_var = _MockTk.StringVar(value=app.position)
    app.zoom_var = _MockTk.DoubleVar(value=app.zoom)
    return app
