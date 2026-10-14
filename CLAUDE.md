# Notes for working on this project

Board: Waveshare ESP32-S3-Zero, CircuitPython 10.3.1 (`board_id: waveshare_esp32_s3_zero`).

- Native USB: serial on `/dev/ttyACM*` plus a CIRCUITPY drive at
  `/run/media/$USER/CIRCUITPY`. Copying `code.py` to the drive is the simplest
  way to deploy. Before using a port, check that it really is the board: a
  WCH-Link programmer can also show up as `/dev/ttyACM0`.
- `tools/ibserial.py` (copied from circuitpython-ideaboard) works with
  `--port /dev/ttyACM0`. It does not autodetect this board.
- There is no `board.I2C()`/`board.SPI()`. Create the buses with `busio` and
  choose the pins yourself.
- The onboard NeoPixel (`board.NEOPIXEL`, IO21) uses RGB order, so it needs
  `pixel_order=neopixel.RGB`.
- touchio (IO1-IO14): the first reading after init is 65535, and the automatic
  threshold is useless. Wait about 1 s, average a baseline and compare
  `raw_value` with hysteresis (on at +3%, off at +1.5%). Untouched readings are
  about 12-16k, and a finger only adds 5-10%.
- Strips: the 144-LED strip is GRB. The 47-LED strip is RGB. Both run from USB
  power, so keep the brightness low.
- MAX98357A on IO4/5/6 (BCLK/LRC/DIN) through `audiobusio.I2SOut`. A
  small speaker cannot play anything below about 100 Hz.
