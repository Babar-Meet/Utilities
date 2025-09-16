import keyboard
import time
import tkinter as tk
from threading import Thread
import ctypes
from ctypes import wintypes
import sys

# Windows API
user32 = ctypes.windll.user32

# Speeds
caps_lock_speed = 1
normal_speed = 12
shift_speed = 4
scroll_speed = 30
fast_scroll_speed = 120  # faster scroll when shift is held

# Double-click timing
double_click_delay = 0.3
last_click_time = {'left': 0, 'right': 0}

# States
program_active = False
key_states = {k: False for k in [
    'up', 'down', 'left', 'right',
    'click_left', 'click_right', 'click_middle',
    'scroll_up', 'scroll_down'
]}

# Mapping keys
ACTION_KEYS = {
    'up': 'num 8',
    'down': 'num 5',
    'left': 'num 4',
    'right': 'num 6',
    'click_left': 'num 7',
    'click_right': 'num 9',
    'click_middle': 'num 2',
    'scroll_down': 'num 1',
    'scroll_up': 'num 3'
}

listener_handlers = []
toggle_hotkey_handle = None

# Helpers
def is_caps_lock_on():
    return user32.GetKeyState(0x14) & 1

def move_mouse(dx, dy):
    user32.mouse_event(0x0001, dx, dy, 0, 0)

def click_mouse(button, down=True):
    flags = {
        ('left', True): 0x0002, ('left', False): 0x0004,
        ('right', True): 0x0008, ('right', False): 0x0010,
        ('middle', True): 0x0020, ('middle', False): 0x0040,
    }
    user32.mouse_event(flags[(button, down)], 0, 0, 0, 0)

def double_click(button):
    click_mouse(button, True)
    click_mouse(button, False)
    time.sleep(0.05)
    click_mouse(button, True)
    click_mouse(button, False)

def scroll_mouse(direction, fast=False):
    amt = fast_scroll_speed if fast else scroll_speed
    if direction == 'up':
        user32.mouse_event(0x0800, 0, 0, amt, 0)
    else:
        user32.mouse_event(0x0800, 0, 0, -amt, 0)

# Action handling
def handle_action(action, is_down):
    if not program_active:
        return

    if action in ['up', 'down', 'left', 'right', 'scroll_up', 'scroll_down']:
        key_states[action] = is_down
    elif action in ['click_left', 'click_right']:
        btn = 'left' if action == 'click_left' else 'right'
        if is_down:
            now = time.time()
            if now - last_click_time[btn] < double_click_delay:
                double_click(btn)
                key_states[action] = False
            else:
                click_mouse(btn, True)
                key_states[action] = True
            last_click_time[btn] = now
        else:
            if key_states[action]:
                click_mouse(btn, False)
                key_states[action] = False
    elif action == 'click_middle':
        if is_down:
            click_mouse('middle', True)
            key_states['click_middle'] = True
        else:
            if key_states['click_middle']:
                click_mouse('middle', False)
                key_states['click_middle'] = False

# Listener mgmt
def register_listeners():
    global listener_handlers
    for action, keyname in ACTION_KEYS.items():
        h1 = keyboard.on_press_key(keyname, lambda e, a=action: handle_action(a, True), suppress=True)
        h2 = keyboard.on_release_key(keyname, lambda e, a=action: handle_action(a, False), suppress=True)
        listener_handlers.extend([h1, h2])

def unregister_listeners():
    global listener_handlers
    for h in listener_handlers:
        try: keyboard.unhook(h)
        except: pass
    listener_handlers = []

# Toggle
def toggle_program():
    global program_active
    program_active = not program_active
    if program_active:
        register_listeners()
    else:
        unregister_listeners()
    update_gui()

# Mouse control loop
def mouse_loop():
    while True:
        if not program_active:
            time.sleep(0.1)
            continue

        speed = caps_lock_speed if is_caps_lock_on() else (shift_speed if keyboard.is_pressed('shift') else normal_speed)
        dx = (key_states['right'] - key_states['left']) * speed
        dy = (key_states['down'] - key_states['up']) * speed
        if dx or dy: move_mouse(dx, dy)

        if key_states['scroll_up']:
            scroll_mouse('up', fast=keyboard.is_pressed('shift'))
            time.sleep(0.05)
        if key_states['scroll_down']:
            scroll_mouse('down', fast=keyboard.is_pressed('shift'))
            time.sleep(0.05)

        time.sleep(0.01)

# GUI
root = tk.Tk()
root.title("Numpad Mouse")
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"60x30+{sw-60}+{sh-30}")
status_label = tk.Label(root, text="Off", bg="#FA8072", fg="white")
status_label.pack(fill="both", expand=True)
root.overrideredirect(True)
root.attributes("-topmost", True)

def update_gui():
    status_label.config(text="ON" if program_active else "Off",
                        bg="#66CDAA" if program_active else "#FA8072")

toggle_hotkey_handle = keyboard.add_hotkey('f9', toggle_program, suppress=True, trigger_on_release=True)

Thread(target=mouse_loop, daemon=True).start()

def on_exit():
    unregister_listeners()
    try: keyboard.remove_hotkey(toggle_hotkey_handle)
    except: pass
    root.destroy(); sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_exit)

try:
    update_gui()
    root.mainloop()
except KeyboardInterrupt:
    on_exit()
