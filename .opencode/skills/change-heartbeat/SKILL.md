---
name: change-heartbeat
description: Use when the artist wants the heartbeat light to look different, for example faster or slower beats, a new colour, brighter or dimmer, pulses moving faster or slower down the strip, wider or narrower pulses, a stronger or softer second beat, or running in the other direction. Explains every setting at the top of code.py that controls the light, with safe values.
---

# Change how the heartbeat looks

Back up first (`cp code.py code.py.bak`), make the change, then
`uv run tools/board.py upload`. All the settings below are near the top of `code.py`.

## Settings

| Request | Setting | Notes |
|---|---|---|
| Colour | `COLOR = (255, 0, 0)` | (red, green, blue), each 0-255. Examples: blue `(0, 0, 255)`, purple `(160, 0, 255)`, orange `(255, 80, 0)`, pink `(255, 20, 80)`, warm white `(255, 140, 60)` |
| Brighter or dimmer | `"peak"` in the active entry of `PROFILES` | 0-255, now 60. See the power warning below. |
| Faster or slower heartbeat | `BEAT_PERIOD` | seconds per beat = 60 / beats per minute. 60 bpm = 1.0, 80 bpm = 0.75, 100 bpm = 0.6 |
| Pulses move faster or slower down the strip | `TRAVEL_TIME` | seconds for one beat to reach the end. Smaller = faster, and each pulse also looks wider. |

How `TRAVEL_TIME` and `BEAT_PERIOD` work together: the number of pulses on the
strip at once is about `TRAVEL_TIME / BEAT_PERIOD`. Each pulse is about
`0.1 * NUM_LEDS / TRAVEL_TIME` LEDs wide.

## Power warning (brightness and colour)

The strip runs from the board's USB power. More brightness, and colours that mix
channels (white, pink, cyan, yellow), draw more current. Keep `peak` at 100 or
less for a single colour such as red or blue, and about 60 or less for
mixtures. If the board restarts, or the status LED goes red when someone
touches the wire, the strip is drawing too much: lower `peak`.

## The beat shape (only if a setting cannot do it)

The shape is built once in the `beat` table, just below the line `STEPS = 180`:

    lub = math.exp(-((t - 0.05) / 0.05) ** 2)
    dub = 0.6 * math.exp(-((t - 0.30) / 0.06) ** 2)

- `0.05` and `0.30` are when the first ("lub") and second ("dub") beat peak, in seconds.
- `/ 0.05` and `/ 0.06` are how long each one lasts. A bigger number gives a softer, longer glow.
- `0.6` is how strong the second beat is compared with the first (0-1).
- The dub must be over before the next beat starts, so `BEAT_PERIOD` must be
  at least about `0.30 + 0.15 = 0.45` s (130 bpm). For a faster heart, scale
  all four times by the same factor. For example, ×0.6 gives 0.03, 0.18, 0.03
  and 0.036. Also change the sound so it still matches (see `change-sound`,
  "Keep sound and light together").

## Reverse direction

In the LED loop at the bottom of `code.py`, change the two `strip[i] = ...`
lines to `strip[NUM_LEDS - 1 - i] = ...`. Nothing else needs to change.

## Fade after letting go

`fade = max(0.0, fade - 0.05)` near the bottom: a smaller number, such as
`0.02`, fades more slowly.

## Things to avoid

- Do not add maths (such as `math.sin` or `math.exp`) inside the `for i in range(NUM_LEDS)`
  loop. It runs for every LED in every frame, and the animation will stutter.
  Calculate things once before `while True:`, as the `beat` table does.
- Do not change `brightness=1.0` in the `neopixel.NeoPixel(...)` line. Use `peak`.
