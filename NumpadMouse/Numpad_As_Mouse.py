import keyboard
import time
import tkinter as tk
from threading import Thread
import ctypes
from ctypes import wintypes
import sys

# Use ctypes for mouse control and Caps Lock detection
user32 = ctypes.windll.user32

# Mouse movement settings
caps_lock_speed = 1   # Speed when Caps Lock is on (slow)
normal_speed = 12      # Speed when Caps Lock is off and Shift not held (normal)
fast_speed = 4       # Speed when Shift is held (fast)
scroll_speed = 30

# Double-click settings
double_click_delay = 0.3  # Time window for double-click in seconds

# Key state tracking - using your specific scan codes for numpad keys
NUMPAD_KEYS = {
    72: 'up',        # Numpad 8
    76: 'down',      # Numpad 5
    75: 'left',      # Numpad 4
    77: 'right',     # Numpad 6
    71: 'click_left',  # Numpad 7
    73: 'click_right', # Numpad 9
    80: 'click_middle',# Numpad 2
    79: 'scroll_down', # Numpad 1
    81: 'scroll_up',   # Numpad 3
}

# Mapping actions to keyboard key names for suppression/handlers
ACTION_KEYNAMES = {
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

# Track movement key states
key_states = {
    'up': False,
    'down': False,
    'left': False,
    'right': False,
    'click_left': False,
    'click_right': False,
    'click_middle': False,
    'scroll_up': False,
    'scroll_down': False
}

# Track double-click timing
last_click_time = {
    'left': 0,
    'right': 0
}

# GUI state
program_active = False  # Start with program inactive
listeners_registered = False  # Track if listeners are registered
toggle_hotkey_handle = None  # Handle for the off-state toggle hotkey
listener_handlers = []  # Track exact handler references so we can reliably unhook and avoid lingering suppression

def is_caps_lock_on():
    # Check if Caps Lock is on using ctypes
    return user32.GetKeyState(0x14) & 0xffff != 0

def toggle_program():
    global program_active
    program_active = not program_active
    if program_active:
        # Going ON: register suppressed listeners
        register_listeners()
    else:
        # Going OFF: unregister suppressed listeners
        unregister_listeners()
    update_gui()

def update_gui():
    if program_active:
        status_label.config(text="ON", bg="#66CDAA")  # Active (green)
    else:
        status_label.config(text="Off", bg="#FA8072")  # Inactive (red)

# Mouse control functions using ctypes
def move_mouse(dx, dy):
    user32.mouse_event(0x0001, dx, dy, 0, 0)

def click_mouse(button, down=True):
    if button == 'left':
        if down:
            user32.mouse_event(0x0002, 0, 0, 0, 0)  # Left down
        else:
            user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left up
    elif button == 'right':
        if down:
            user32.mouse_event(0x0008, 0, 0, 0, 0)  # Right down
        else:
            user32.mouse_event(0x0010, 0, 0, 0, 0)  # Right up
    elif button == 'middle':
        if down:
            user32.mouse_event(0x0020, 0, 0, 0, 0)  # Middle down
        else:
            user32.mouse_event(0x0040, 0, 0, 0, 0)  # Middle up

def double_click(button):
    if button == 'left':
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # Left down
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left up
        time.sleep(0.05)
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # Left down
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left up
    elif button == 'right':
        user32.mouse_event(0x0008, 0, 0, 0, 0)  # Right down
        user32.mouse_event(0x0010, 0, 0, 0, 0)  # Right up
        time.sleep(0.05)
        user32.mouse_event(0x0008, 0, 0, 0, 0)  # Right down
        user32.mouse_event(0x0010, 0, 0, 0, 0)  # Right up

def scroll_mouse(direction):
    if direction == 'up':
        user32.mouse_event(0x0800, 0, 0, scroll_speed, 0)  # Wheel up
    elif direction == 'down':
        user32.mouse_event(0x0800, 0, 0, -scroll_speed, 0)  # Wheel down

def handle_action(action, is_down):
    if not program_active:
        return

    if action in ['up', 'down', 'left', 'right', 'scroll_up', 'scroll_down']:
        key_states[action] = is_down
    elif action == 'click_left':
        if is_down:
            current_time = time.time()
            if current_time - last_click_time['left'] < double_click_delay:
                double_click('left')
                key_states['click_left'] = False
            else:
                click_mouse('left', True)
                key_states['click_left'] = True
            last_click_time['left'] = current_time
        else:
            if key_states['click_left']:
                click_mouse('left', False)
                key_states['click_left'] = False
    elif action == 'click_right':
        if is_down:
            current_time = time.time()
            if current_time - last_click_time['right'] < double_click_delay:
                double_click('right')
                key_states['click_right'] = False
            else:
                click_mouse('right', True)
                key_states['click_right'] = True
            last_click_time['right'] = current_time
        else:
            if key_states['click_right']:
                click_mouse('right', False)
                key_states['click_right'] = False
    elif action == 'click_middle':
        if is_down:
            click_mouse('middle', True)
            key_states['click_middle'] = True
        else:
            if key_states['click_middle']:
                click_mouse('middle', False)
                key_states['click_middle'] = False

def register_listeners():
    global listeners_registered, listener_handlers
    if not listeners_registered:
        for action, keyname in ACTION_KEYNAMES.items():
            h1 = keyboard.on_press_key(keyname, lambda e, a=action: handle_action(a, True), suppress=True)
            h2 = keyboard.on_release_key(keyname, lambda e, a=action: handle_action(a, False), suppress=True)
            listener_handlers.append(h1)
            listener_handlers.append(h2)
        listeners_registered = True

def unregister_listeners():
    global listeners_registered, listener_handlers
    if listeners_registered:
        # Unhook the exact handlers we registered to ensure suppression is removed
        for h in listener_handlers:
            try:
                keyboard.unhook(h)
            except Exception:
                pass
        listener_handlers = []
        listeners_registered = False

# Mouse control function
def mouse_control_loop():
    while True:
        if not program_active:
            time.sleep(0.1)
            continue
            
        # Speed priority: Caps Lock (slow) > Shift (fast) > Normal
        if is_caps_lock_on():
            current_speed = caps_lock_speed
        else:
            try:
                # keyboard.is_pressed handles either Shift key
                current_speed = fast_speed if keyboard.is_pressed('shift') else normal_speed
            except Exception:
                # Fallback to normal if detection fails
                current_speed = normal_speed
        dx, dy = 0, 0
        
        if key_states['up']:
            dy -= current_speed
        if key_states['down']:
            dy += current_speed
        if key_states['left']:
            dx -= current_speed
        if key_states['right']:
            dx += current_speed
        
        # Move mouse if there's any movement
        if dx != 0 or dy != 0:
            move_mouse(dx, dy)
        
        # Handle continuous scrolling
        if key_states['scroll_up']:
            scroll_mouse('up')
            time.sleep(0.05)
            
        if key_states['scroll_down']:
            scroll_mouse('down')
            time.sleep(0.05)
        
        time.sleep(0.01)

# Create GUI in bottom right corner
root = tk.Tk()
root.title("Numpad Mouse")

# Position at bottom-right corner
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 60
window_height = 30
root.geometry(f"{window_width}x{window_height}+{screen_width-window_width}+{screen_height-window_height}")

# Status label
status_label = tk.Label(root, text="Off", bg="#FA8072", fg="white", font=("Arial", 10))
status_label.pack(fill="both", expand=True)

# Remove window border and keep on top
root.overrideredirect(True)
root.attributes("-topmost", True)

# Register global toggle hotkey (F6)
# Use suppress=True and trigger_on_release for a clean toggle
toggle_hotkey_handle = keyboard.add_hotkey(
    'f9',
    lambda: toggle_program(),
    suppress=True,
    trigger_on_release=True
)

# Start mouse movement thread
mouse_thread = Thread(target=mouse_control_loop, daemon=True)
mouse_thread.start()

# Function to clean up on exit
def on_exit():
    # Cleanup listeners and hotkey
    unregister_listeners()
    try:
        keyboard.remove_hotkey(toggle_hotkey_handle)
    except Exception:
        pass
    root.destroy()
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_exit)

# Start GUI
try:
    update_gui()  # Set initial GUI state
    root.mainloop()
except KeyboardInterrupt:
    on_exit()