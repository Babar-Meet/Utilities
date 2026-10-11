# Dr Clock & Battery

A small desktop overlay showing the current time and the battery level. `Time_Battry_info.py`
is the program; `Run_clock.bat` is a Windows launcher that changes to this directory and starts
it. This README is the third and last file in the directory.

## Run it

```
Run_clock.bat
```

or run the script directly:

```
python Time_Battry_info.py
```

It needs `tkinter` (standard library) and `psutil` (third party):

```
pip install psutil
```

`tkinter` is included with the standard CPython installer on Windows. On some Linux
distributions it is packaged separately.

No title bar, no border and no close button. Nothing is written to the console, so a
terminal that stays blank after running it is the expected result, not a failure.

## What it shows

- **Time**: 12-hour clock, no AM/PM, leading zero stripped. 13:05 shows as `1:05`,
  23:05 as `11:05`, 9:05 as `9:05`.
- **Battery**: whole-number percent, truncated rather than rounded, so 99.7 shows as
  `99` and 0.4 shows as `0`. A `+` is appended only while the machine reports it is
  plugged in.
- **`--`**: shown when psutil cannot supply a reading: it reports no battery, it reports
  no percentage, or the query itself fails. `psutil` reports no battery when none is
  installed, on Windows, Linux and macOS, so a desktop shows `--`. `psutil` is a hard
  requirement, though: if it is not installed the script does not start and prints
  `ModuleNotFoundError` instead of showing `--`.

Battery reporting depends on the operating system. Where psutil supplies a percentage the
indicator shows one; where it does not, it shows `--`, whether psutil reported no battery,
no percentage, or a failed query. Whether a given machine has a battery is a property of
that machine.

## The window

Always on top, anchored to the bottom-left corner. Drag it with the left mouse button.
Dragging is not clamped to the screen: the overlay can be moved entirely off-screen, and
there is no menu, no tray icon and no keyboard shortcut to bring it back. The only way to
recover it is to stop the process and run the command above again.

Opacity is `WINDOW_ALPHA = 0.70` and the refresh interval is `REFRESH_MS = 1000`
milliseconds. Both are values set in the script, not facts about your platform.

At startup the window sizes itself once, from two fixed sample strings, `12:59` and
`100+`; it never re-measures, so a font or DPI change at runtime leaves the old size.
Measured on Windows with Segoe UI at Tk size 9 (points), `12:59` measured 27px and
`100+` measured 26px, producing a 27x30px window. That figure depends on those fonts and
that display; it is not a guarantee for other setups.

## Configuration

Appearance and behaviour are set by the constants grouped under
`# ===== Easy-to-edit configuration =====` at the top of the file: font family and sizes,
line gap, background and text colour, opacity, refresh rate, and an initial window size
that is overwritten at startup (WINDOW_WIDTH and WINDOW_HEIGHT are placeholders; editing
them has no effect).

## Project state

One Python source file plus a launcher. No test suite, no CI, and no dependency manifest;
the only third-party dependency is `psutil`, installed on demand.

## Verified on

Windows, 2026-10-10, with Python 3.14.2, psutil 7.1.3 and Tk 8.6. The script launched,
stayed alive and responsive, and produced no output on stdout or stderr.
`psutil.sensors_battery()` reported `percent=68`, `secsleft=1538`,
`power_plugged=False`, and the window displayed `68`.