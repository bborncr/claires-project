# Claire's heartbeat: guide for the coding agent

This is an art piece. Touching a wire makes red "lub-dub" heartbeat pulses run
along an LED strip, with a thump from a small speaker on each beat. The person
asking you for changes is an artist, not a programmer. Describe things in terms
of what they will see and hear, answer in the language they write in, and do
not show code unless they ask for it.

## The hardware (read this before anything else)

- The board is a **Waveshare ESP32-S3-Zero** running **CircuitPython 10.3.1**.
  It is **not an IdeaBoard**. Do not use the `ideaboard`, `ideasense`,
  `sumobot`, `sumobotv2` or `libraries` skills here, even if they are available.
  Their pins and tools are wrong for this board.
- The whole program is one file, `code.py`. The board runs it at power-on.
- Pins in use. Do not change them unless the artist has rewired something:

| Part | Pin |
|------|-----|
| LED strip data | `board.IO1` |
| Touch wire | `board.IO7` |
| Speaker amplifier (MAX98357A) BCLK / LRC / DIN | `board.IO4` / `board.IO5` / `board.IO6` |
| Small status LED on the board | `board.NEOPIXEL` (red = calibrating, green = ready) |

- This board has no `board.I2C()` or `board.SPI()`. A new part on those buses
  needs `busio` with pins chosen by the person who wires it, so ask; do not guess.

## Rules

1. **Change the settings at the top of `code.py` first.** Most requests
   (colour, speed, brightness, volume) are a single number there. Only touch the
   code below the settings when no setting can do it.
2. **Never invent pins, parts or libraries** that are not in this file or the
   skills. If something is not covered, say that you do not know and ask.
3. **Before editing, back up:** `cp code.py code.py.bak`
4. **After every change, upload and check it** with exactly this command:

       uv run tools/board.py upload

   It refuses code with a syntax error, copies `code.py` to the board, restarts
   it and prints the board's output. It always ends with a `RESULT:` line.
   - `RESULT: OK`: tell the artist what to look and listen for, and ask them to
     touch the wire and say if it looks right. You cannot see the LEDs or hear
     the sound, so never claim that they look or sound right. Only the artist
     can say that.
   - `RESULT: ERROR`: read the error, fix it and upload again. If two attempts
     fail, restore the backup (`cp code.py.bak code.py`), upload that, and
     explain the problem to the artist in plain words.
5. **Never run `tools/ibserial.py run code.py`.** It does not stop, because the
   program loops forever. To see the output again without uploading, run
   `uv run tools/board.py console`. Run it only once per question. Nobody
   touches the wire unless you have asked the artist to, so running it again
   and again shows nothing new.
6. Keep the speed of the main `while True:` loop in mind. It updates every LED
   many times a second, and slow code there makes the animation stutter.
7. Do not commit or push with git unless the artist asks.

## Skills for this project

Load the skill that matches the request before you change anything:

| The artist says something like | Skill |
|---|---|
| faster, slower, colour, brighter, dimmer, longer trail, different beat | `change-heartbeat` |
| louder, quieter, deeper, different sound, no sound | `change-sound` |
| it beats on its own, it does not react, it will not stop, too sensitive | `touch-problems` |
| new or different strip, more LEDs, wrong colours, flicker, wiring | `led-strips` |
| put it on the board, it does not start, error, is it working | `upload-and-check` |
