---
name: change-sound
description: Use when the artist wants the heartbeat sound changed, for example louder, quieter, deeper, higher, longer or shorter thumps, a different rhythm, a recorded sound from a WAV file, or no sound at all. Covers the VOLUME setting, how the thump is generated, using a WAV file on the board, the limits of the small speaker, and what to check when there is no sound.
---

# Change the heartbeat sound

The sound plays through a MAX98357A amplifier on `board.IO4`/`IO5`/`IO6`
(`audiobusio.I2SOut`) into a small speaker. It plays once each time a new beat
leaves the first LED, and only while someone is touching the wire.

Back up first, change, then `uv run tools/board.py upload`.

## Volume

`VOLUME` near the top, from 0.0 to 1.0. 0.02 is barely audible. `VOLUME = 0`
turns the sound off.

## The generated thump

The sound is made once at startup by the block that starts with `RATE = 8000`:

| What | Where | Notes |
|---|---|---|
| Rhythm | `THUMPS = ((0.02, 1.0), (0.27, 0.6))` | each pair is (start time in seconds, loudness 0-1). Add a third pair for a triple beat. |
| Pitch | `110 + 70 * math.exp(-tau / 0.03)` | starts at 180 Hz (110 + 70) and drops to 110 Hz. |
| Length of each thump | `math.exp(-tau / 0.06)` | bigger than 0.06 = longer, boomier |
| Buzz | `0.3 * math.sin(2 * phase)` | how much of the octave above is mixed in. 0 gives a pure, softer tone. |
| Total length | `int(RATE * 0.55)` | seconds of sound. Must cover the last thump. |

**Speaker limit:** the small speaker cannot play below about 100 Hz. Keep the
lowest pitch (the `110`) at 100 or above. For a "deeper" sound, lower the
`0.3` buzz and make the thump longer instead. Lowering the pitch only makes it
quieter.

**Startup time and memory:** the sound is calculated in Python at power-on, so a
longer sound or a higher `RATE` makes startup slower and uses memory. Keep
`RATE` at 8000 or 16000, and the total length at 1 s or less. A `MemoryError`
means the sound is too long.

## Keep sound and light together

The light's lub and dub peak at 0.05 s and 0.30 s (see `change-heartbeat`). The
thump start times (0.02 and 0.27) are set slightly earlier so they line up. If
you move the light's beats, move these by the same amount. If the sound is
longer than `BEAT_PERIOD`, each new beat cuts off the end of the previous sound.

## Using a recorded WAV file instead

1. Convert it to mono 16-bit, 22050 Hz, no longer than one beat (`BEAT_PERIOD`),
   and quieter if needed:

       ffmpeg -i input.mp3 -ac 1 -ar 22050 -sample_fmt s16 -t 0.8 -filter:a volume=0.5 heartbeat.wav

2. The board's drive holds less than 1 MB, so keep the file under 300 KB. Copy it
   to the drive next to `code.py`. On Linux that is `/run/media/$USER/CIRCUITPY/`,
   on macOS `/Volumes/CIRCUITPY/`, and on Windows the drive named CIRCUITPY.
   `uv run tools/board.py check` prints the location.
3. In `code.py`, replace the line `thump = audiocore.RawSample(sound, sample_rate=RATE)` with:

       thump = audiocore.WaveFile(open("heartbeat.wav", "rb"))

   Also delete the generated-sound block above it (from `RATE = 8000` to the end
   of the `for` loop) to speed up startup. `VOLUME` no longer has an effect, so
   set the loudness with ffmpeg's `volume=`.

## No sound at all

1. Check that `VOLUME` is not 0, and that the artist is touching the wire. The
   sound only plays during a touch.
2. If the board output shows an error, see `upload-and-check`.
3. If there is no error, it is probably the wiring. Ask the artist to check the
   amplifier: VIN to 5V, GND to GND, BCLK to IO4, LRC to IO5, DIN to IO6, and both
   speaker wires. Do not guess other causes or suggest other pins.
