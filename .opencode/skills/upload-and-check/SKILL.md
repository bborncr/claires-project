---
name: upload-and-check
description: Use whenever code.py has been changed and must go onto the heartbeat board, or when the artist says "put it on the board", "it does not start", "nothing happens", "the light on the board is red", "is it working", or shows an error. Covers tools/board.py (upload, console, check), reading the board's output, common CircuitPython errors on the Waveshare ESP32-S3-Zero, and undoing a bad change.
---

# Upload and check

## The commands

Run them from the project folder:

| Command | What it does |
|---|---|
| `uv run tools/board.py upload` | checks `code.py` for syntax errors, copies it to the board, restarts it, prints the output (about 10 s) |
| `uv run tools/board.py console` | restarts the program and prints its output for 8 s (`console 20` for 20 s) |
| `uv run tools/board.py check` | shows whether the board's drive and serial port were found |

All three stop by themselves and print a final `RESULT: OK` or `RESULT: ERROR`
line. Without `uv`, use `pip install pyserial` and then `python tools/board.py ...`.

**Never run `tools/ibserial.py run code.py`, `screen`, `miniterm` or `tio`.** They
do not stop, and the agent will hang.

## What normal output looks like

    code.py output:
    baseline 17973

`baseline` is the touch reading with nobody touching the wire, normally a number
between about 12000 and 19000. Touching the wire prints `touched 18650`, and
letting go prints `released 18200`. To catch those lines, run
`uv run tools/board.py console 20` and ask the artist to touch the wire while it runs.

The status LED on the board is red for about one second while it calibrates,
then green. The artist must not touch the wire while it is red.

## When something goes wrong

| Output | Meaning and fix |
|---|---|
| `syntax error; nothing was uploaded` | The edit broke Python. Fix the line it names. |
| `NameError: name 'X' is not defined` | Misspelled or missing setting. Check the settings at the top. |
| `IndexError` | A list position past the end, often in the LED loop. |
| `MemoryError` | Too much data. Usually the sound is too long or the sample rate too high (see `change-sound`). |
| `ValueError: ... in use` | Two parts use the same pin. Check the pin table in `AGENTS.md`. |
| `CIRCUITPY drive not found` | The board is unplugged, or the USB cable is a charge-only cable. Ask the artist. |
| `serial port not found` | The same, or another program (Thonny, Mu, a serial monitor) holds the port. Ask the artist to close it. Set `BOARD_PORT=/dev/ttyACM1` (Linux), `/dev/cu.usbmodem...` (macOS) or `COM5` (Windows) if needed. |
| No `baseline` line, no error | The program is stuck before calibration. Run `console 15` and look again. |

## Undoing a change

- Undo the last change: `cp code.py.bak code.py`, then upload.
- Go back to the last version saved in git: `git diff code.py` shows what
  changed. **Ask the artist first**, then `git checkout code.py` and upload.
  This throws away every change since the last commit.
