import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
import psutil

# ===== Easy-to-edit configuration =====
# Font family and sizes
FONT_FAMILY = "Segoe UI"
TIME_SIZE = 9
BATTERY_SIZE = 9

# Spacing between lines (in pixels)
LINE_GAP = 0

# Colors and transparency
BG_COLOR = "#000000"   # Background color
FG_COLOR = "#FFFFFF"   # Text color
WINDOW_ALPHA = 0.70     # 0.0 (fully transparent) .. 1.0 (opaque)

# Refresh rate (milliseconds)
REFRESH_MS = 1000

# Initial placeholder window size (will be recalculated precisely)
WINDOW_WIDTH = 100
WINDOW_HEIGHT = 46

def get_battery_text() -> str:
    """Return battery percentage with one decimal; minimal text."""
    try:
        batt = psutil.sensors_battery()
    except Exception:
        batt = None

    if not batt or batt.percent is None:
        return "--"

    # Show a '+' when plugged in; otherwise show just the percentage
    return f"{int(batt.percent)}+" if getattr(batt, "power_plugged", False) else f"{int(batt.percent)}"


def update_gui():
    """Update time and battery labels."""    
    # 12-hour format (no AM/PM) and remove leading zero
    now = datetime.now().strftime("%I:%M").lstrip("0")
    time_label.config(text=now)

    battery_text = get_battery_text()
    battery_label.config(text=battery_text)

    # Schedule next update
    root.after(REFRESH_MS, update_gui)


def start_move(event):
    """Record the mouse position when starting to drag the window."""
    root._drag_start_x = event.x
    root._drag_start_y = event.y

def do_move(event):
    """Move the window according to mouse drag while keeping size static."""
    x = event.x_root - root._drag_start_x
    y = event.y_root - root._drag_start_y
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

# Create GUI in bottom-left corner
root = tk.Tk()
root.title("Clock & Battery")

# Calculate position for bottom-left
root.update_idletasks()  # Ensure screen size is available
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
pos_x = 0
pos_y = screen_height - WINDOW_HEIGHT
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{pos_x}+{pos_y}")

# Appearance and window behavior
root.configure(bg=BG_COLOR)
root.resizable(False, False)  # Static size
root.overrideredirect(True)   # Borderless
root.attributes("-topmost", True)
root.attributes("-alpha", WINDOW_ALPHA)

# Content: time (HH:MM) and battery status
container = tk.Frame(root, bg=BG_COLOR, bd=0, highlightthickness=0)
container.pack(fill="both", expand=False)

# Create concrete font objects so we can measure exact sizes
time_font_obj = tkfont.Font(family=FONT_FAMILY, size=TIME_SIZE)
battery_font_obj = tkfont.Font(family=FONT_FAMILY, size=BATTERY_SIZE)

time_label = tk.Label(
    container,
    text="--:--",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=time_font_obj,
    bd=0,
    padx=0,
    pady=0,
    highlightthickness=0,
)
time_label.pack(anchor="w")

battery_label = tk.Label(
    container,
    text="--",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=battery_font_obj,
    bd=0,
    padx=0,
    pady=0,
    highlightthickness=0,
)
battery_label.pack(anchor="w", pady=(LINE_GAP, 0))

# Compute exact window size based on max expected text widths and line heights (12-hour format)
max_time_sample = "12:59"
max_batt_sample = "100+"  # account for '+' when plugged in
text_width = max(
    time_font_obj.measure(max_time_sample),
    battery_font_obj.measure(max_batt_sample),
)
line_height = time_font_obj.metrics('linespace') + battery_font_obj.metrics('linespace')

# Window size should be exactly what's needed, no more no less
WINDOW_WIDTH = text_width
WINDOW_HEIGHT = line_height + LINE_GAP

# Apply computed geometry at bottom-left
pos_x = 0
pos_y = screen_height - WINDOW_HEIGHT
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{pos_x}+{pos_y}")

# Allow dragging the window
root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", do_move)

# Kick off updates
update_gui()

# Start event loop
if __name__ == "__main__":
    root.mainloop()