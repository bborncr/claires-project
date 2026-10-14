---
name: led-strips
description: Use when the LED strip changes or shows the wrong thing, for example switching between the 144-LED and 47-LED strips, adding a new strip with a different number of LEDs, red showing as green, only part of the strip lighting, flicker, the board restarting when the strip lights up, or questions about wiring and power. Covers PROFILES and PROFILE in code.py, colour order and power limits.
---

# LED strips

The strip is WS2812B ("NeoPixel"), and its data wire is on `board.IO1`.
`neopixel` is built into the board's firmware, so no library needs to be copied.

## Choosing the strip

Near the top of `code.py`:

    PROFILES = {
        "strip144": {"leds": 144, "order": neopixel.GRB, "peak": 60},
        "strip47": {"leds": 47, "order": neopixel.RGB, "peak": 60},
    }
    PROFILE = "strip144"

Set `PROFILE` to the strip that is plugged in. The two known strips are:

- `strip144`: 144 LEDs, colour order GRB.
- `strip47`: 47 LEDs, colour order RGB.

## Adding a new strip

Add a line to `PROFILES` with a new name, the number of LEDs, the colour order
and a `peak` (start at 40). Then set `PROFILE` to that name. Ask the artist to
count the LEDs, or read the number off the reel, rather than guessing.

## Wrong colours

Red showing as green (or blue as something else) means the colour order is
wrong. Most strips are `neopixel.GRB`, and some are `neopixel.RGB`. Change
`"order"` in the strip's profile and upload again. Do not change `COLOR` to
work around it.

## Only part of the strip lights up

- `"leds"` is smaller than the real number of LEDs. Fix the count.
- Or the strip draws too much power and the far end gets too little: lower `peak`.

## Power

Everything runs from the board's USB port, which gives about 0.5 A. A full-white
LED draws about 60 mA, so 144 LEDs at full brightness would need about 8 A.
That is why `peak` is low (60 of 255) and why only the moving pulses are lit.
Signs of too much current: flicker, the far end turning orange or dim, or the
board restarting (status LED going red again) when the heartbeat starts. The
fix is a lower `peak`. A brighter piece needs a separate 5 V power supply
for the strip. Tell the artist this is a wiring job and not a code change.

## Wiring (for reference; do not change pins without being asked)

Only the data wire is fixed: the strip's DIN (data in) goes to IO1. The strip's
5V and GND go to the board's 5V and GND. Wire colours differ between strips, so
check the labels printed on the strip rather than going by colour.

## The small LED on the board

`board.NEOPIXEL` (IO21) is the status LED: red while calibrating, green when
ready. It uses RGB order (`pixel_order=neopixel.RGB`), unlike most strips.
Leave it alone unless the artist asks.
