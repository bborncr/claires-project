# Claire's project

A touch-activated heartbeat for a Waveshare ESP32-S3-Zero running CircuitPython 10.3.1.
Touching the wire on IO7 sends red "lub-dub" pulses along an LED strip, from
LED 0 to the end. A matching thump plays through an I2S amplifier on each beat.

## Hardware

| Part | Connection |
|------|------------|
| WS2812B LED strip (data) | IO1 |
| Touch wire (capacitive sense) | IO7 |
| MAX98357A BCLK | IO4 |
| MAX98357A LRC | IO5 |
| MAX98357A DIN | IO6 |
| MAX98357A VIN / GND | 5V / GND |
| Onboard NeoPixel (status) | `board.NEOPIXEL` (IO21) |

The onboard LED is red while the touch sensor calibrates at startup and green
once it is ready. Keep your hands off the wire while it is red.

## Settings (top of `code.py`)

- `PROFILE`: which strip is connected. `strip144` (144 LEDs, GRB) or `strip47`
  (47 LEDs, RGB). Add a new entry to `PROFILES` for another strip. If red shows
  up as green, the strip needs `neopixel.RGB`.
- `peak`: the brightest red value (0-255). Keep it low when the strip runs on USB power.
- `BEAT_PERIOD`, `TRAVEL_TIME`: how fast the heart beats and how fast each beat
  runs down the strip.
- `VOLUME`: how loud the heartbeat sound is (0.0-1.0).

## Putting it on the board

The quickest way: `uv run tools/board.py upload`. It checks `code.py`, copies it
to the board, restarts it and shows the output, ending in `RESULT: OK` or
`RESULT: ERROR`. `uv run tools/board.py console` shows the output again.

The board shows up as a `CIRCUITPY` drive. Copy `code.py` onto the drive and the
board restarts with it. No extra libraries are needed, because `neopixel` is
built into this board's firmware.

For the serial console or to copy files without the drive, use `tools/ibserial.py`
and pass the port (it only finds IdeaBoard CH340 ports by itself):

    uv run tools/ibserial.py --port /dev/ttyACM0 info
    uv run tools/ibserial.py --port /dev/ttyACM0 put code.py /code.py

## Asking an AI agent for changes

The repo is set up for [opencode](https://opencode.ai) (and other agents that
read `AGENTS.md`). Open opencode in this folder and describe the change in
plain words, for example "make the heartbeat blue and a bit slower". `AGENTS.md`
holds the ground rules, and `.opencode/skills/` holds one guide each for the
light, the sound, the touch sensor, the strips and uploading.
