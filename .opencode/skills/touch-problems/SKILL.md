---
name: touch-problems
description: Use when the touch wire misbehaves or its sensitivity should change, for example the heartbeat starts by itself (phantom beats), it does not react or needs a hard squeeze, it keeps beating after letting go, it stops on its own while someone holds on, it reacts from a distance, or a longer wire or a metal plate is used. Explains how the touch sensing in code.py works and which numbers to change.
---

# Touch problems

The wire on `board.IO7` is a capacitive touch sensor (`touchio.TouchIn`).
`code.py` uses `touch.raw_value`, a number that rises a little when a hand
comes close.

**Do not use `touch.value` or the automatic threshold**. It does not work on
this board.

## How it works

1. At startup (status LED red) the program waits 1 s, then averages 10 readings
   with nobody touching. This is the `baseline`, printed as `baseline 17973`.
   The very first reading after startup is always 65535 and is meaningless,
   which is why it waits.
2. Touch starts when the reading goes above `baseline * 1.03` (+3%). It ends
   when the reading falls below `baseline * 1.015` (+1.5%). The gap between the
   two stops flicker. Both numbers are in `set_levels()`.
3. While nobody touches, the baseline slowly follows the reading, so
   temperature, humidity or a moved wire do not cause false touches
   (`BASELINE_RATE`, about 40 s to adjust).
4. If a touch lasts longer than `MAX_TOUCH` seconds (90), the program assumes
   the reading shifted, takes the current reading as the new baseline and stops
   the heartbeat.

Typical numbers: about 12000-19000 untouched. A finger adds 5-10%. With nobody
touching, the reading only varies by about 0.1%.

## See the real numbers first

Before changing anything, look at what the sensor does.

- Touch events from the running program: `uv run tools/board.py console 20`,
  and ask the artist to touch and let go a few times while it runs. Compare the
  `touched` and `released` numbers with the `baseline`.
- Live readings, 5 per second for 10 s (this stops the main program). Use the
  port from `uv run tools/board.py check`:

      uv run tools/ibserial.py --port PORT exec "import board, touchio, time
      t = touchio.TouchIn(board.IO7)
      time.sleep(1)
      for _ in range(50):
          print(t.raw_value)
          time.sleep(0.2)
      t.deinit()"

  Ask the artist to stay away for the first few seconds, then touch. Afterwards
  run `uv run tools/board.py console` to start the heartbeat again.

## Fixes

| Problem | Change in `set_levels()` |
|---|---|
| Starts by itself, reacts from a distance | more margin: on `1.04`, off `1.02` (or `1.05` / `1.025`) |
| Needs a hard touch, does not react | less margin: on `1.02`, off `1.01`. Do not go below about `1.01` / `1.005`: noise is about 0.1%. |
| Keeps beating after letting go | raise off, but keep it below on, for example on `1.03`, off `1.02` |

Keep the "on" number bigger than the "off" number.

Other causes and settings:

- **Someone was touching during the red LED at startup.** The baseline is then
  too high, and touches stop working. Restart (`uv run tools/board.py console`)
  with hands off the wire.
- **The heartbeat stops while someone holds on.** `MAX_TOUCH` is too short for the
  piece. Raise it, for example `MAX_TOUCH = 300`.
- **A longer wire or a metal plate** raises the baseline and can change how big
  a touch is in %. Measure first (above), then set on and off between the
  untouched and touched readings.
- **Phantom beats near the strip's power cable or other electronics:** move the
  wire away from them. This is physical, not code.
