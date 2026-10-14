#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyserial>=3.5"]
# ///
"""
board.py - upload code.py to the Waveshare ESP32-S3-Zero and check that it runs.

    uv run tools/board.py check            find the board (drive and serial port)
    uv run tools/board.py upload           check code.py, copy it to the board, show its output
    uv run tools/board.py upload FILE.py   the same with another file (it becomes /code.py)
    uv run tools/board.py console [SECS]   restart the program and show its output (default 8 s)

`upload` and `console` end with one line: "RESULT: OK ..." or "RESULT: ERROR ...".
They always stop by themselves, so they are safe to run from an agent.

Without uv:  pip install pyserial  then  python tools/board.py upload
"""

import os
import platform
import py_compile
import shutil
import string
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is missing. Run:  pip install pyserial   (or use: uv run tools/board.py ...)")

BOARD_ID = "waveshare_esp32_s3_zero"
USB_VID = 0x303A  # Espressif; a WCH-Link or IdeaBoard uses a different id
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_drive():
    """Return the CIRCUITPY drive folder, or None."""
    user = os.environ.get("USER") or os.environ.get("USERNAME") or ""
    if platform.system() == "Windows":
        candidates = [f"{c}:\\" for c in string.ascii_uppercase]
    else:
        candidates = [f"/run/media/{user}/CIRCUITPY", f"/media/{user}/CIRCUITPY",
                      "/media/CIRCUITPY", "/Volumes/CIRCUITPY"]
    for path in candidates:
        try:
            with open(os.path.join(path, "boot_out.txt")) as f:
                if BOARD_ID in f.read():
                    return path
        except OSError:
            pass
    return None


def find_port():
    """Return the board's serial port, or None."""
    env = os.environ.get("BOARD_PORT")
    if env:
        return env
    for p in list_ports.comports():
        if p.vid == USB_VID:
            return p.device
    return None


def read_console(port, seconds):
    """Restart code.py over serial and return everything it prints for `seconds`."""
    with serial.Serial(port, 115200, timeout=0.2) as s:
        s.write(b"\x03")  # Ctrl-C: stop the running program
        time.sleep(0.3)
        s.write(b"\x04")  # Ctrl-D: restart code.py
        out = b""
        end = time.time() + seconds
        while time.time() < end:
            out += s.read(512)
    text = out.decode(errors="replace")
    # Drop the terminal title escapes CircuitPython sends (ESC ] 0; ... ESC \).
    while "\x1b]" in text:
        a = text.index("\x1b]")
        b = text.find("\x1b\\", a)
        text = text[:a] + ("" if b < 0 else text[b + 2:])
    text = text.replace("\x1b[2K\x1b[0G", "")
    # Keep only the fresh run: before "soft reboot" is the Ctrl-C we just sent.
    if "soft reboot" in text:
        text = text[text.rindex("soft reboot"):]
    return text


def verdict(text):
    if "Traceback" in text or "Error" in text:
        print("RESULT: ERROR - the program crashed. The error is shown above.")
        return 1
    if "baseline" in text:
        print("RESULT: OK - the program started and calibrated the touch sensor.")
        return 0
    print("RESULT: ERROR - no 'baseline' line seen; the program may not have started.")
    return 1


def need_port():
    port = find_port()
    if not port:
        sys.exit("RESULT: ERROR - board serial port not found. Is the USB cable plugged in?")
    return port


def cmd_check():
    drive, port = find_drive(), find_port()
    print("drive:", drive or "NOT FOUND")
    print("port: ", port or "NOT FOUND")
    return 0 if drive and port else 1


def cmd_upload(src):
    src = os.path.abspath(src)
    try:
        py_compile.compile(src, doraise=True)
    except py_compile.PyCompileError as e:
        print(e.msg)
        print("RESULT: ERROR - code has a syntax error; nothing was uploaded.")
        return 1
    drive = find_drive()
    if not drive:
        print("RESULT: ERROR - CIRCUITPY drive not found. Is the board plugged in?")
        return 1
    port = need_port()
    dest = os.path.join(drive, "code.py")
    shutil.copyfile(src, dest)
    with open(dest, "rb+") as f:
        os.fsync(f.fileno())
    if hasattr(os, "sync"):
        os.sync()
    print("copied", os.path.relpath(src, ROOT), "->", dest)
    time.sleep(2)  # let the board notice the new file before restarting it
    text = read_console(port, 8)
    print(text)
    return verdict(text)


def cmd_console(seconds):
    text = read_console(need_port(), seconds)
    print(text)
    return verdict(text)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "check":
        return cmd_check()
    if args[0] == "upload":
        return cmd_upload(args[1] if len(args) > 1 else os.path.join(ROOT, "code.py"))
    if args[0] == "console":
        return cmd_console(float(args[1]) if len(args) > 1 else 8)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
