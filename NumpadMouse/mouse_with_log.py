import keyboard
import time
import tkinter as tk
from threading import Thread
import ctypes
from ctypes import wintypes
import sys
import logging
import traceback
from datetime import datetime

# Set up logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mouse_movement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

# State recovery and fail-safe variables
last_known_good_state = False
state_recovery_attempts = 0
max_recovery_attempts = 10
keyboard_library_healthy = True
last_keyboard_check = time.time()
keyboard_check_interval = 5.0  # Check keyboard library health every 5 seconds

def safe_execute(func, *args, **kwargs):
    """Safely execute a function with comprehensive exception handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def check_keyboard_library_health():
    """Check if keyboard library is functioning properly"""
    global keyboard_library_healthy, last_keyboard_check
    current_time = time.time()
    
    if current_time - last_keyboard_check < keyboard_check_interval:
        return keyboard_library_healthy
    
    try:
        # Test a simple keyboard operation
        test_result = keyboard.is_pressed('shift')
        keyboard_library_healthy = True
        logger.debug("Keyboard library health check passed")
    except Exception as e:
        keyboard_library_healthy = False
        logger.error(f"Keyboard library health check failed: {str(e)}")
    
    last_keyboard_check = current_time
    return keyboard_library_healthy

def reset_all_states():
    """Reset all key states to prevent stuck conditions"""
    global key_states, state_recovery_attempts
    logger.warning("Resetting all key states due to error recovery")
    
    # Reset all key states
    for key in key_states:
        key_states[key] = False
    
    # Release any stuck mouse buttons
    try:
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left up
        user32.mouse_event(0x0010, 0, 0, 0, 0)  # Right up
        user32.mouse_event(0x0040, 0, 0, 0, 0)  # Middle up
    except Exception as e:
        logger.error(f"Error releasing mouse buttons: {str(e)}")
    
    state_recovery_attempts += 1
    logger.info(f"State recovery attempt {state_recovery_attempts}")

def is_caps_lock_on():
    """Check if Caps Lock is on using ctypes with exception handling"""
    try:
        return user32.GetKeyState(0x14) & 0xffff != 0
    except Exception as e:
        logger.error(f"Error checking Caps Lock state: {str(e)}")
        return False  # Default to False if detection fails

def toggle_program():
    """Toggle program state with comprehensive error handling"""
    global program_active, last_known_good_state
    
    try:
        program_active = not program_active
        last_known_good_state = program_active
        
        logger.info(f"Toggling program state to: {'ON' if program_active else 'OFF'}")
        
        if program_active:
            # Going ON: register suppressed listeners
            safe_execute(register_listeners)
        else:
            # Going OFF: unregister suppressed listeners
            safe_execute(unregister_listeners)
        
        safe_execute(update_gui)
        
    except Exception as e:
        logger.error(f"Error in toggle_program: {str(e)}")
        logger.error(traceback.format_exc())
        # Try to restore last known good state
        program_active = last_known_good_state
        safe_execute(update_gui)

def update_gui():
    """Update GUI display with exception handling"""
    try:
        if program_active:
            status_label.config(text="ON", bg="#66CDAA")  # Active (green)
        else:
            status_label.config(text="Off", bg="#FA8072")  # Inactive (red)
    except Exception as e:
        logger.error(f"Error updating GUI: {str(e)}")

# Mouse control functions using ctypes with exception handling
def move_mouse(dx, dy):
    """Move mouse with exception handling"""
    try:
        user32.mouse_event(0x0001, dx, dy, 0, 0)
    except Exception as e:
        logger.error(f"Error moving mouse: {str(e)}")

def click_mouse(button, down=True):
    """Click mouse button with exception handling"""
    try:
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
    except Exception as e:
        logger.error(f"Error clicking mouse {button}: {str(e)}")

def double_click(button):
    """Double click with exception handling"""
    try:
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
    except Exception as e:
        logger.error(f"Error double clicking {button}: {str(e)}")

def scroll_mouse(direction):
    """Scroll mouse with exception handling"""
    try:
        if direction == 'up':
            user32.mouse_event(0x0800, 0, 0, scroll_speed, 0)  # Wheel up
        elif direction == 'down':
            user32.mouse_event(0x0800, 0, 0, -scroll_speed, 0)  # Wheel down
    except Exception as e:
        logger.error(f"Error scrolling mouse {direction}: {str(e)}")

def handle_action(action, is_down):
    """Handle keyboard actions with comprehensive error handling"""
    global state_recovery_attempts
    
    try:
        if not program_active:
            return

        # Check keyboard library health before processing
        if not check_keyboard_library_health():
            logger.warning("Keyboard library unhealthy, attempting recovery")
            reset_all_states()
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
        
        # Reset recovery attempts on successful action
        state_recovery_attempts = 0
        
    except Exception as e:
        logger.error(f"Error handling action {action}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Attempt state recovery if too many errors
        if state_recovery_attempts < max_recovery_attempts:
            reset_all_states()
        else:
            logger.error("Max recovery attempts reached, forcing program restart")
            # Force toggle to reset state
            safe_execute(toggle_program)
            safe_execute(toggle_program)  # Toggle back to original state

def register_listeners():
    """Register keyboard listeners with exception handling"""
    global listeners_registered, listener_handlers
    
    try:
        if not listeners_registered and check_keyboard_library_health():
            for action, keyname in ACTION_KEYNAMES.items():
                try:
                    h1 = keyboard.on_press_key(keyname, lambda e, a=action: handle_action(a, True), suppress=True)
                    h2 = keyboard.on_release_key(keyname, lambda e, a=action: handle_action(a, False), suppress=True)
                    listener_handlers.append(h1)
                    listener_handlers.append(h2)
                except Exception as e:
                    logger.error(f"Error registering listener for {keyname}: {str(e)}")
                    continue
            
            listeners_registered = True
            logger.info("Keyboard listeners registered successfully")
    except Exception as e:
        logger.error(f"Error registering listeners: {str(e)}")
        logger.error(traceback.format_exc())

def unregister_listeners():
    """Unregister keyboard listeners with exception handling"""
    global listeners_registered, listener_handlers
    
    try:
        if listeners_registered:
            # Unhook the exact handlers we registered to ensure suppression is removed
            for h in listener_handlers:
                try:
                    keyboard.unhook(h)
                except Exception:
                    pass
            listener_handlers = []
            listeners_registered = False
            logger.info("Keyboard listeners unregistered successfully")
    except Exception as e:
        logger.error(f"Error unregistering listeners: {str(e)}")

# Mouse control function with infinite loop and fail-safe
def mouse_control_loop():
    """Main mouse control loop that never terminates"""
    loop_count = 0
    
    while True:
        try:
            loop_count += 1
            
            # Periodic health check and logging
            if loop_count % 1000 == 0:  # Log every 1000 iterations
                logger.debug(f"Mouse control loop running - iteration {loop_count}")
                check_keyboard_library_health()
            
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
            
        except Exception as e:
            logger.error(f"Error in mouse control loop: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Reset states and continue
            reset_all_states()
            
            # Brief pause to prevent error spam
            time.sleep(0.1)

# Create GUI in bottom right corner with exception handling
try:
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

    # Register global toggle hotkey (F6) with exception handling
    try:
        toggle_hotkey_handle = keyboard.add_hotkey(
            'f9',
            lambda: safe_execute(toggle_program),
            suppress=True,
            trigger_on_release=True
        )
        logger.info("Toggle hotkey registered successfully")
    except Exception as e:
        logger.error(f"Error registering toggle hotkey: {str(e)}")

    # Start mouse movement thread
    mouse_thread = Thread(target=mouse_control_loop, daemon=True)
    mouse_thread.start()
    logger.info("Mouse control thread started")

    # Function to clean up on exit
    def on_exit():
        """Cleanup function with exception handling"""
        logger.info("Program exiting, performing cleanup...")
        try:
            # Cleanup listeners and hotkey
            safe_execute(unregister_listeners)
            try:
                keyboard.remove_hotkey(toggle_hotkey_handle)
            except Exception:
                pass
            root.destroy()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        finally:
            sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_exit)

    # Start GUI with infinite loop protection
    logger.info("Starting GUI main loop")
    print("Numpad mouse working with fail-safe protection")
    
    while True:
        try:
            update_gui()  # Set initial GUI state
            root.mainloop()
            break  # Exit if mainloop completes normally
        except Exception as e:
            logger.error(f"GUI main loop error: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Try to recreate GUI if it fails
            try:
                root.destroy()
            except:
                pass
            
            # Wait before attempting to restart GUI
            time.sleep(1)
            
            # Recreate GUI
            try:
                root = tk.Tk()
                root.title("Numpad Mouse")
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                window_width = 60
                window_height = 30
                root.geometry(f"{window_width}x{window_height}+{screen_width-window_width}+{screen_height-window_height}")
                status_label = tk.Label(root, text="Off", bg="#FA8072", fg="white", font=("Arial", 10))
                status_label.pack(fill="both", expand=True)
                root.overrideredirect(True)
                root.attributes("-topmost", True)
                root.protocol("WM_DELETE_WINDOW", on_exit)
                logger.info("GUI recreated successfully")
            except Exception as e:
                logger.error(f"Error recreating GUI: {str(e)}")
                time.sleep(5)  # Wait longer before next attempt

except KeyboardInterrupt:
    logger.info("Keyboard interrupt received")
    safe_execute(on_exit)
except Exception as e:
    logger.error(f"Fatal error during program initialization: {str(e)}")
    logger.error(traceback.format_exc())
    
    # Try to keep the program running even if GUI fails
    logger.info("Attempting to run without GUI...")
    try:
        # Start just the mouse control thread
        mouse_thread = Thread(target=mouse_control_loop, daemon=True)
        mouse_thread.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            check_keyboard_library_health()
    except Exception as e:
        logger.error(f"Critical failure: {str(e)}")
        # Last resort - infinite sleep to prevent termination
        while True:
            time.sleep(10)