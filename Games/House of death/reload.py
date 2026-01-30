import tkinter as tk
from pynput import mouse, keyboard
import threading, time, json, os

CONFIG = "mouse_combo_config.json"

mouse_ctl = mouse.Controller()

hotkey = None
waiting_for = False
delay = 0.05

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

# ---------- CLICK ACTION ----------
def combo_click():
    for _ in range(2):
        mouse_ctl.click(mouse.Button.left)
        time.sleep(0.01)
    mouse_ctl.click(mouse.Button.right)

# ---------- SAVE / LOAD ----------
def save_cfg():
    global delay
    try:
        delay = float(delay_var.get())
    except:
        return

    if not hotkey:
        status_msg.config(text="Set key first", fg="red")
        return

    with open(CONFIG, "w") as f:
        json.dump({
            "key": hk_to_str(hotkey),
            "delay": delay
        }, f)

    status_msg.config(text="Saved ✓", fg="green")

def load_cfg():
    global hotkey, delay
    if not os.path.exists(CONFIG):
        return

    with open(CONFIG, "r") as f:
        d = json.load(f)

    hotkey = str_to_hk(d["key"])
    delay = float(d.get("delay", 0.05))

    key_lbl.config(text=d["key"])
    delay_var.set(str(delay))

# ---------- INPUT ----------
def on_key(key):
    global waiting_for, hotkey
    if waiting_for:
        hotkey = key
        key_lbl.config(text=hk_to_str(key))
        waiting_for = False
        status_msg.config(text="Key set (press Save)", fg="orange")
    else:
        if key == hotkey:
            threading.Thread(target=combo_click, daemon=True).start()

def on_mouse(x, y, btn, pressed):
    if not pressed:
        return
    global waiting_for, hotkey
    if waiting_for:
        hotkey = btn
        key_lbl.config(text=hk_to_str(btn))
        waiting_for = False
        status_msg.config(text="Key set (press Save)", fg="orange")
    else:
        if btn == hotkey:
            threading.Thread(target=combo_click, daemon=True).start()

# ---------- GUI ----------
root = tk.Tk()
root.title("Mouse Combo")
root.geometry("420x260")
root.resizable(False, False)

tk.Label(root, text="Mouse Combo", font=("Segoe UI", 16, "bold")).pack(pady=8)

frame = tk.Frame(root)
frame.pack(pady=15)

def set_wait():
    global waiting_for
    waiting_for = True
    key_lbl.config(text="Press key / mouse")

tk.Label(frame, text="Action").grid(row=0, column=0, padx=5)
tk.Label(frame, text="3 LEFT + 1 RIGHT").grid(row=0, column=1, padx=5)

tk.Label(frame, text="Hotkey").grid(row=1, column=0)
key_lbl = tk.Label(frame, text="Not set", width=18)
key_lbl.grid(row=1, column=1)
tk.Button(frame, text="Set", command=set_wait).grid(row=1, column=2, padx=5)

tk.Label(frame, text="Delay").grid(row=2, column=0)
delay_var = tk.StringVar(value="0.05")
tk.Entry(frame, textvariable=delay_var, width=6).grid(row=2, column=1, sticky="w")

tk.Button(root, text="SAVE SETTINGS", font=("Segoe UI", 11, "bold"),
          bg="#023D0E", fg="white", command=save_cfg).pack(pady=15)

status_msg = tk.Label(root, text="", font=("Segoe UI", 10))
status_msg.pack()

# ---------- START ----------
load_cfg()

keyboard.Listener(on_press=on_key).start()
mouse.Listener(on_click=on_mouse).start()

root.mainloop()
