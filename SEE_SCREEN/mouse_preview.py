"""
Dr Broken Display — see what's under your cursor in a corner preview window.

Usage:
    python mouse_preview.py

Right-click the preview  →  open settings (size, position, zoom)
Drag the blue handle     →  reposition window (when overlay is hidden)
Ctrl+Alt+Scroll         →  resize window
Shift+Alt+Scroll        →  change zoom
Press Escape            →  quit
"""

import tkinter as tk
from tkinter import ttk
import mss
from PIL import Image, ImageTk, ImageDraw
import pyautogui
import json
import os
import sys
import threading
from pynput import keyboard, mouse

__version__ = "1.1.0"
APP_NAME = "Dr Broken Display"
_HANDLE_SZ = 24


class MousePreviewApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{__version__}")

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1a1a1a")

        self.sct = mss.mss()
        monitors = self.sct.monitors
        self._virtual = monitors[0]
        self._monitors = monitors[1:]

        self.settings_file = os.path.join(
            os.path.expanduser("~/Downloads"),
            "dr_broken_display_settings.json",
        )
        self.load_settings()

        self.settings_visible = False
        self.photo = None
        self.drag_off_x = 0
        self.drag_off_y = 0
        self._preview_image_id = None
        self._hidden_by_us = False
        self._hide_area = (0, 0, 0, 0)
        self._dragging = False

        self._build_handle()
        self._build_preview()
        if self.window_x is not None and self.window_y is not None:
            self.root.geometry(f"+{self.window_x}+{self.window_y}")
        else:
            self._update_position()

        self._start_global_listeners()

        self.root.after(33, self._update_preview)

        self.root.bind("<Escape>", lambda e: self._quit())
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.mainloop()

    # ── settings persistence ──────────────────────────────

    def load_settings(self):
        d = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file) as f:
                    d = json.load(f)
            except Exception:
                pass
        self.preview_size = d.get("preview_size", 310)
        self.position = d.get("position", "bottom-left")
        self.zoom = d.get("zoom", 1.0)
        self.window_x = d.get("window_x")
        self.window_y = d.get("window_y")

    def save_settings(self):
        data = {
            "preview_size": self.preview_size,
            "position": self.position,
            "zoom": self.zoom,
        }
        if self.window_x is not None and self.window_y is not None:
            data["window_x"] = self.window_x
            data["window_y"] = self.window_y
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=2)

    # ── handle (always-visible drag square) ────────────────

    def _build_handle(self):
        self.handle = tk.Toplevel(self.root)
        self.handle.overrideredirect(True)
        self.handle.attributes("-topmost", True)
        self.handle.configure(bg="#3377ee")
        self.handle.geometry(f"{_HANDLE_SZ}x{_HANDLE_SZ}")
        self.handle.withdraw()

        self.handle.bind("<Button-1>", self._h_drag_start)
        self.handle.bind("<B1-Motion>", self._h_drag_move)
        self.handle.bind("<ButtonRelease-1>", self._h_drag_end)
        self.handle.bind("<Button-3>", lambda e: self._toggle_settings())

    def _h_drag_start(self, e):
        self._dragging = True
        self.drag_off_x = e.x
        self.drag_off_y = e.y

    def _h_drag_move(self, e):
        dx = e.x - self.drag_off_x
        dy = e.y - self.drag_off_y
        hx = self.handle.winfo_x() + dx
        hy = self.handle.winfo_y() + dy
        self.handle.geometry(f"+{hx}+{hy}")
        self.root.geometry(f"+{hx + _HANDLE_SZ - self.preview_size}+{hy + _HANDLE_SZ - self.preview_size}")
        self._hide_area = (hx + _HANDLE_SZ - self.preview_size, hy + _HANDLE_SZ - self.preview_size,
                           self.preview_size, self.preview_size)

    def _h_drag_end(self, e):
        self._dragging = False
        self.window_x = self.root.winfo_x()
        self.window_y = self.root.winfo_y()
        self.save_settings()

    # ── UI construction ───────────────────────────────────

    def _build_preview(self):
        self.canvas = tk.Canvas(
            self.root,
            width=self.preview_size,
            height=self.preview_size,
            highlightthickness=0,
            bg="#1a1a1a",
            bd=0,
            cursor="crosshair",
        )
        self.canvas.pack()

        self.canvas.bind("<Button-3>", lambda e: self._toggle_settings())

        self._build_settings_panel()

    def _build_settings_panel(self):
        bg = "#2b2b2b"
        fg = "#ccc"
        self.settings_frame = tk.Frame(
            self.root, bg=bg, highlightbackground="#555", highlightthickness=1
        )

        frame_opt = {"bg": bg}
        label_opt = {"bg": bg, "fg": fg, "font": ("Segoe UI", 9), "width": 8, "anchor": "w"}

        tk.Label(
            self.settings_frame,
            text=APP_NAME,
            bg=bg,
            fg="#e0e0e0",
            font=("Segoe UI", 10, "bold"),
        ).pack(fill="x", padx=10, pady=(8, 0))

        tk.Frame(self.settings_frame, height=1, bg="#444").pack(
            fill="x", padx=8, pady=4
        )

        sf = tk.Frame(self.settings_frame, **frame_opt)
        sf.pack(fill="x", padx=10, pady=2)
        tk.Label(sf, **label_opt, text="Size:").pack(side="left")
        self.size_var = tk.IntVar(value=self.preview_size)
        c = ttk.Combobox(
            sf,
            textvariable=self.size_var,
            values=[100, 150, 200, 250, 300, 400, 500],
            width=7,
            state="readonly",
        )
        c.pack(side="right")
        c.bind("<<ComboboxSelected>>", self._on_size_change)

        pf = tk.Frame(self.settings_frame, **frame_opt)
        pf.pack(fill="x", padx=10, pady=2)
        tk.Label(pf, **label_opt, text="Position:").pack(side="left")
        self.pos_var = tk.StringVar(value=self.position)
        c = ttk.Combobox(
            pf,
            textvariable=self.pos_var,
            values=["bottom-left", "bottom-right", "top-left", "top-right"],
            width=13,
            state="readonly",
        )
        c.pack(side="right")
        c.bind("<<ComboboxSelected>>", self._on_position_change)

        zf = tk.Frame(self.settings_frame, **frame_opt)
        zf.pack(fill="x", padx=10, pady=2)
        tk.Label(zf, **label_opt, text="Zoom:").pack(side="left")
        self.zoom_var = tk.DoubleVar(value=self.zoom)
        c = ttk.Combobox(
            zf,
            textvariable=self.zoom_var,
            values=[0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0],
            width=7,
            state="readonly",
        )
        c.pack(side="right")
        c.bind("<<ComboboxSelected>>", self._on_zoom_change)

        btn_row = tk.Frame(self.settings_frame, bg=bg)
        btn_row.pack(fill="x", padx=10, pady=(4, 10))
        tk.Button(
            btn_row,
            text="Close",
            command=self._hide_settings,
            bg="#3a3a3a",
            fg=fg,
            relief="flat",
            font=("Segoe UI", 9),
            padx=10,
            activebackground="#555",
            activeforeground="#fff",
            cursor="hand2",
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            btn_row,
            text="Quit",
            command=self._quit,
            bg="#4a2a2a",
            fg="#e88",
            relief="flat",
            font=("Segoe UI", 9),
            padx=10,
            activebackground="#5a3a3a",
            activeforeground="#faa",
            cursor="hand2",
        ).pack(side="left")

    # ── window geometry ───────────────────────────────────

    def _rebuild_layout(self):
        for w in self.root.winfo_children():
            w.pack_forget()

        if self.position in ("bottom-left", "bottom-right"):
            if self.settings_visible:
                self.settings_frame.pack(fill="x")
            self.canvas.pack()
        else:
            self.canvas.pack()
            if self.settings_visible:
                self.settings_frame.pack(fill="x")

        self._update_position()

    def _get_current_monitor(self, mx, my):
        for m in self._monitors:
            if m["left"] <= mx < m["left"] + m["width"] and m["top"] <= my < m["top"] + m["height"]:
                return m
        return self._monitors[0]

    def _update_position(self):
        mx, my = pyautogui.position()
        mon = self._get_current_monitor(mx, my)
        mw, mh = mon["width"], mon["height"]
        ml, mt = mon["left"], mon["top"]

        self.root.update_idletasks()
        pad = 10
        settings_h = (
            self.settings_frame.winfo_height() if self.settings_visible else 0
        )
        total_h = self.preview_size + settings_h

        if self.position == "bottom-left":
            x = ml + pad
            y = mt + mh - total_h - pad
        elif self.position == "bottom-right":
            x = ml + mw - self.preview_size - pad
            y = mt + mh - total_h - pad
        elif self.position == "top-left":
            x = ml + pad
            y = mt + pad
        else:
            x = ml + mw - self.preview_size - pad
            y = mt + pad

        self.root.geometry(f"+{x}+{y}")
        self.window_x = x
        self.window_y = y

    # ── settings toggles ──────────────────────────────────

    def _toggle_settings(self):
        if self.settings_visible:
            self._hide_settings()
        else:
            self._show_settings()

    def _show_settings(self):
        self.settings_visible = True
        self._rebuild_layout()

    def _hide_settings(self):
        self.settings_visible = False
        self._rebuild_layout()

    # ── setting change handlers ───────────────────────────

    def _on_size_change(self, _=None):
        self.preview_size = self.size_var.get()
        self.canvas.config(width=self.preview_size, height=self.preview_size)
        self.save_settings()
        self._rebuild_layout()

    def _on_position_change(self, _=None):
        self.position = self.pos_var.get()
        self.save_settings()
        self._rebuild_layout()

    def _on_zoom_change(self, _=None):
        self.zoom = self.zoom_var.get()
        self.save_settings()

    # ── global hotkeys: Ctrl+Alt+Scroll (size), Shift+Alt+Scroll (zoom) ─

    ZOOM_STEPS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]

    def _start_global_listeners(self):
        self._ctrl_held = False
        self._alt_held = False
        self._shift_held = False

        def on_press(key):
            try:
                if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    self._ctrl_held = True
                elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    self._alt_held = True
                elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    self._shift_held = True
            except Exception:
                pass

        def on_release(key):
            try:
                if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    self._ctrl_held = False
                elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    self._alt_held = False
                elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    self._shift_held = False
            except Exception:
                pass

        def on_scroll(x, y, dx, dy):
            if self._ctrl_held and self._alt_held:
                step = 20
                if dy > 0:
                    self.root.after(0, lambda: self._resize_by(step))
                elif dy < 0:
                    self.root.after(0, lambda: self._resize_by(-step))
            elif self._shift_held and self._alt_held:
                if dy > 0:
                    self.root.after(0, lambda: self._zoom_by(1))
                elif dy < 0:
                    self.root.after(0, lambda: self._zoom_by(-1))

        self._kb_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._ms_listener = mouse.Listener(on_scroll=on_scroll)
        self._kb_listener.daemon = True
        self._ms_listener.daemon = True
        self._kb_listener.start()
        self._ms_listener.start()

    def _resize_by(self, delta):
        new = max(50, min(500, self.preview_size + delta))
        if new != self.preview_size:
            self.size_var.set(new)
            self._on_size_change()

    def _zoom_by(self, direction):
        steps = self.ZOOM_STEPS
        idx = next((i for i, v in enumerate(steps) if abs(v - self.zoom) < 0.01), -1)
        new_idx = max(0, min(len(steps) - 1, idx + direction))
        if new_idx != idx:
            self.zoom = steps[new_idx]
            self.zoom_var.set(self.zoom)
            self.save_settings()

    # ── capture & display loop ────────────────────────────

    def _capture(self):
        mx, my = pyautogui.position()
        virt = self._virtual

        cap_sz = int(self.preview_size / self.zoom)
        half = cap_sz // 2

        left = max(virt["left"], mx - half)
        top = max(virt["top"], my - half)
        left = min(left, virt["left"] + virt["width"] - cap_sz)
        top = min(top, virt["top"] + virt["height"] - cap_sz)
        right = min(virt["left"] + virt["width"], left + cap_sz)
        bottom = min(virt["top"] + virt["height"], top + cap_sz)

        w = right - left
        h = bottom - top
        if w < cap_sz:
            if left == virt["left"]:
                right = virt["left"] + min(virt["width"], cap_sz)
            else:
                left = virt["left"] + virt["width"] - cap_sz
        if h < cap_sz:
            if top == virt["top"]:
                bottom = virt["top"] + min(virt["height"], cap_sz)
            else:
                top = virt["top"] + virt["height"] - cap_sz

        bbox = (int(left), int(top), int(right), int(bottom))

        if self._hidden_by_us and not self._dragging:
            ax, ay, aw, ah = self._hide_area
            hx = self.handle.winfo_x()
            hy = self.handle.winfo_y()
            in_zone = (ax <= mx <= ax + aw and ay <= my <= ay + ah) or \
                      (hx <= mx <= hx + _HANDLE_SZ and hy <= my <= hy + _HANDLE_SZ)
            if not in_zone:
                self._hidden_by_us = False
                self.root.geometry(f"+{hx + _HANDLE_SZ - self.preview_size}+{hy + _HANDLE_SZ - self.preview_size}")
                self.handle.withdraw()
        else:
            wx = self.root.winfo_x()
            wy = self.root.winfo_y()
            ww = self.root.winfo_width()
            wh = self.root.winfo_height()
            if wx <= mx <= wx + ww and wy <= my <= wy + wh:
                self._hidden_by_us = True
                self._hide_area = (wx, wy, ww, wh)
                self.root.geometry("+99999+99999")
                self.handle.geometry(f"+{wx + ww - _HANDLE_SZ}+{wy + wh - _HANDLE_SZ}")
                self.handle.deiconify()

        screenshot = self.sct.grab(bbox)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        if self.zoom != 1.0:
            img = img.resize((self.preview_size, self.preview_size), Image.LANCZOS)

        img = img.convert("RGBA")
        draw = ImageDraw.Draw(img)

        cap_w = right - left
        cap_h = bottom - top
        cursor_in_frame_x = mx - left
        cursor_in_frame_y = my - top
        scale_x = self.preview_size / cap_w
        scale_y = self.preview_size / cap_h
        cx = cursor_in_frame_x * scale_x
        cy = cursor_in_frame_y * scale_y

        r = 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#4488ff")

        return img

    def _update_preview(self):
        try:
            img = self._capture()
            self.photo = ImageTk.PhotoImage(img)

            if self._preview_image_id is not None:
                self.canvas.delete(self._preview_image_id)
            self._preview_image_id = self.canvas.create_image(
                0, 0, image=self.photo, anchor="nw", tags="preview"
            )
            self.canvas.tag_lower("preview")
        except Exception:
            pass

        self.root.after(33, self._update_preview)

    # ── cleanup ───────────────────────────────────────────

    def _quit(self):
        self.save_settings()
        try:
            self.handle.destroy()
        except Exception:
            pass
        try:
            self._kb_listener.stop()
        except Exception:
            pass
        try:
            self._ms_listener.stop()
        except Exception:
            pass
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    MousePreviewApp()
