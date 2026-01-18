import tkinter as tk
from pynput import mouse, keyboard
import threading, time, json, os

CONFIG = "mouse_spammer_config.json"

mouse_ctl = mouse.Controller()

left_hotkey = None
right_hotkey = None
left_active = False
right_active = False
waiting_for = None

left_delay = 0.05
right_delay = 0.05

# ---------- HOTKEY UTILS ----------
def hk_to_str(hk):
    if isinstance(hk, keyboard.Key):
        return f"key:{hk.name}"
    if isinstance(hk, keyboard.KeyCode):
        return f"key:{hk.char}"
    if isinstance(hk, mouse.Button):
        return f"mouse:{hk.name}"

def str_to_hk(s):
    t, v = s.split(":")
    if t == "key":
        try:
            return keyboard.Key[v]
        except KeyError:
            return keyboard.KeyCode.from_char(v)
    if t == "mouse":
        return mouse.Button[v]

# ---------- SAVE / LOAD ----------
def save_cfg():
    global left_delay, right_delay
    try:
        left_delay = float(left_delay_var.get())
        right_delay = float(right_delay_var.get())
    except:
        return

    if not left_hotkey or not right_hotkey:
        status_msg.config(text="Set both keys first", fg="red")
        return

    with open(CONFIG, "w") as f:
        json.dump({
            "left": hk_to_str(left_hotkey),
            "right": hk_to_str(right_hotkey),
            "left_delay": left_delay,
            "right_delay": right_delay
        }, f)

    status_msg.config(text="Saved ✓", fg="green")

def load_cfg():
    global left_hotkey, right_hotkey, left_delay, right_delay
    if not os.path.exists(CONFIG):
        return
    with open(CONFIG, "r") as f:
        d = json.load(f)
    left_hotkey = str_to_hk(d["left"])
    right_hotkey = str_to_hk(d["right"])
    left_delay = float(d.get("left_delay", 0.05))
    right_delay = float(d.get("right_delay", 0.05))

    left_key_lbl.config(text=d["left"])
    right_key_lbl.config(text=d["right"])
    left_delay_var.set(str(left_delay))
    right_delay_var.set(str(right_delay))

# ---------- SPAM THREADS ----------
def left_spam():
    while True:
        if left_active:
            mouse_ctl.click(mouse.Button.left)
            time.sleep(left_delay)
        else:
            time.sleep(0.1)

def right_spam():
    while True:
        if right_active:
            mouse_ctl.click(mouse.Button.right)
            time.sleep(right_delay)
        else:
            time.sleep(0.1)

# ---------- OVERLAY ----------
def update_overlay():
    if left_active and right_active:
        overlay_lbl.config(text="L+R", bg="#7B2CBF")
    elif left_active:
        overlay_lbl.config(text="LEFT", bg="#1E90FF")
    elif right_active:
        overlay_lbl.config(text="RIGHT", bg="#2E8B57")
    else:
        overlay_lbl.config(text="NONE", bg="#B22222")

# ---------- INPUT ----------
def toggle(hk):
    global left_active, right_active
    if hk == left_hotkey:
        left_active = not left_active
        left_status.config(text="ON" if left_active else "OFF",
                           fg="green" if left_active else "red")
    if hk == right_hotkey:
        right_active = not right_active
        right_status.config(text="ON" if right_active else "OFF",
                            fg="green" if right_active else "red")
    update_overlay()

def on_key(key):
    global waiting_for, left_hotkey, right_hotkey
    if waiting_for:
        if waiting_for == "left":
            left_hotkey = key
            left_key_lbl.config(text=hk_to_str(key))
        else:
            right_hotkey = key
            right_key_lbl.config(text=hk_to_str(key))
        waiting_for = None
        status_msg.config(text="Key set (press Save)", fg="orange")
    else:
        toggle(key)

def on_mouse(x, y, btn, pressed):
    if not pressed:
        return
    global waiting_for, left_hotkey, right_hotkey
    if waiting_for:
        if waiting_for == "left":
            left_hotkey = btn
            left_key_lbl.config(text=hk_to_str(btn))
        else:
            right_hotkey = btn
            right_key_lbl.config(text=hk_to_str(btn))
        waiting_for = None
        status_msg.config(text="Key set (press Save)", fg="orange")
    else:
        toggle(btn)

# ---------- GUI ----------
root = tk.Tk()
root.title("Mouse Spammer")
root.geometry("540x380")
root.resizable(False, False)

tk.Label(root, text="Mouse Spammer", font=("Segoe UI", 16, "bold")).pack(pady=8)

frame = tk.Frame(root)
frame.pack(pady=10)

def set_wait(side):
    global waiting_for
    waiting_for = side
    (left_key_lbl if side=="left" else right_key_lbl).config(text="Press key / mouse")

tk.Label(frame, text="Left Click").grid(row=0, column=0)
left_status = tk.Label(frame, text="OFF", fg="red", font=("Segoe UI", 11, "bold"))
left_status.grid(row=0, column=1)
left_key_lbl = tk.Label(frame, text="Not set", width=18)
left_key_lbl.grid(row=0, column=2)
tk.Button(frame, text="Set", command=lambda: set_wait("left")).grid(row=0, column=3)
tk.Label(frame, text="Delay").grid(row=0, column=4)
left_delay_var = tk.StringVar(value="0.05")
tk.Entry(frame, textvariable=left_delay_var, width=6).grid(row=0, column=5)

tk.Label(frame, text="Right Click").grid(row=1, column=0)
right_status = tk.Label(frame, text="OFF", fg="red", font=("Segoe UI", 11, "bold"))
right_status.grid(row=1, column=1)
right_key_lbl = tk.Label(frame, text="Not set", width=18)
right_key_lbl.grid(row=1, column=2)
tk.Button(frame, text="Set", command=lambda: set_wait("right")).grid(row=1, column=3)
tk.Label(frame, text="Delay").grid(row=1, column=4)
right_delay_var = tk.StringVar(value="0.05")
tk.Entry(frame, textvariable=right_delay_var, width=6).grid(row=1, column=5)

tk.Button(root, text="SAVE SETTINGS", font=("Segoe UI", 11, "bold"),
          bg="#023D0E", fg="white", command=save_cfg).pack(pady=10)

status_msg = tk.Label(root, text="", font=("Segoe UI", 10))
status_msg.pack()

# ---------- OVERLAY ----------
overlay = tk.Toplevel()
overlay.overrideredirect(True)
overlay.attributes("-topmost", True)
overlay.attributes("-alpha", 0.6)

w, h = 70, 28
sw, sh = overlay.winfo_screenwidth(), overlay.winfo_screenheight()
overlay.geometry(f"{w}x{h}+{sw-w}+{sh-h}")

overlay_lbl = tk.Label(overlay, text="NONE", fg="white",
                       bg="#B22222", font=("Segoe UI", 10, "bold"))
overlay_lbl.pack(fill="both", expand=True)

# ---------- START ----------
load_cfg()
update_overlay()

threading.Thread(target=left_spam, daemon=True).start()
threading.Thread(target=right_spam, daemon=True).start()

keyboard.Listener(on_press=on_key).start()
mouse.Listener(on_click=on_mouse).start()

root.mainloop()