import array
import math
import time
import audiobusio
import audiocore
import board
import neopixel
import touchio

# One profile per LED strip. Set PROFILE to the strip that is connected.
#   leds:  number of LEDs on the strip
#   order: colour order; if red shows as green, the strip needs neopixel.RGB
#   peak:  brightness at the top of a beat (0-255); keep it low on USB power
PROFILES = {
    "strip144": {"leds": 144, "order": neopixel.GRB, "peak": 60},
    "strip47": {"leds": 47, "order": neopixel.RGB, "peak": 60},
}
PROFILE = "strip144"

NUM_LEDS = PROFILES[PROFILE]["leds"]
PEAK = PROFILES[PROFILE]["peak"]
COLOR = (255, 0, 0)  # beat colour as (red, green, blue), each 0-255; PEAK sets brightness
BEAT_PERIOD = 0.9  # seconds per heartbeat (about 67 beats per minute)
TRAVEL_TIME = 1.0  # seconds for a beat to run from LED 0 to the last LED

VOLUME = 1.0  # heartbeat sound loudness (0.0-1.0); 0.02 is barely audible

BASELINE_RATE = 0.0005  # how quickly the baseline follows slow drift (about 40 s)
MAX_TOUCH = 90  # seconds; a touch this long is taken as a shifted baseline

strip = neopixel.NeoPixel(board.IO1, NUM_LEDS, brightness=1.0, auto_write=False,
                          pixel_order=PROFILES[PROFILE]["order"])
touch = touchio.TouchIn(board.IO7)

# The onboard LED takes colours in RGB order, not the usual GRB.
status = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1, pixel_order=neopixel.RGB)
status[0] = (255, 0, 0)  # red: calibrating, keep hands off the wire

# The first readings after setup are not valid, so take the baseline after a pause.
time.sleep(1)
total = 0
for _ in range(10):
    total += touch.raw_value
    time.sleep(0.01)
baseline = total / 10


def set_levels():
    # Switch on above +3% and off below +1.5% so a light touch does not flicker.
    global on_level, off_level
    on_level = baseline * 1.03
    off_level = baseline * 1.015


set_levels()
print("baseline", int(baseline))
status[0] = (0, 255, 0)  # green: ready

# One heartbeat, a strong beat followed by a softer one, as a table of
# brightness values so each frame only looks values up instead of doing maths per LED.
STEPS = 180
beat = []
for n in range(STEPS):
    t = n * BEAT_PERIOD / STEPS
    lub = math.exp(-((t - 0.05) / 0.05) ** 2)
    dub = 0.6 * math.exp(-((t - 0.30) / 0.06) ** 2)
    beat.append(max(lub, dub))

LED_DELAY = TRAVEL_TIME / NUM_LEDS  # how much later each LED sees the beat

# The matching sound: two low thumps ("lub-dub") timed like the LED beat. Each
# thump starts near 180 Hz and drops to 110 Hz (lower is too deep for a small
# speaker), with a little of the octave above mixed in.
RATE = 8000
THUMPS = ((0.02, 1.0), (0.27, 0.6))  # (start time in s, loudness)
sound = array.array("h", [0] * int(RATE * 0.55))
for onset, loud in THUMPS:
    phase = 0.0
    for n in range(int(onset * RATE), len(sound)):
        tau = n / RATE - onset
        phase += 2 * math.pi * (110 + 70 * math.exp(-tau / 0.03)) / RATE
        env = (1 - math.exp(-tau / 0.004)) * math.exp(-tau / 0.06)
        wave = math.sin(phase) + 0.3 * math.sin(2 * phase)
        sound[n] += int(loud * env * wave * 32767 * VOLUME / 1.3)
thump = audiocore.RawSample(sound, sample_rate=RATE)
audio = audiobusio.I2SOut(bit_clock=board.IO4, word_select=board.IO5, data=board.IO6)

touched = False
start = 0  # time.monotonic_ns() at the touch
last_beat = -1
fade = 0.0
strip.fill(0)
strip.show()

while True:
    raw = touch.raw_value
    if not touched and raw > on_level:
        touched = True
        start = time.monotonic_ns()
        fade = 1.0
        last_beat = -1
        print("touched", raw)
    elif touched and raw < off_level:
        touched = False
        print("released", raw)
    elif touched and time.monotonic_ns() - start > MAX_TOUCH * 1_000_000_000:
        # Nobody holds on this long; the wire has probably moved or the air
        # changed. Take the current reading as the new baseline and let go.
        touched = False
        baseline = raw
        set_levels()
        print("touch too long, new baseline", int(baseline))

    # While nobody is touching, let the baseline slowly follow the reading so
    # changes in temperature, humidity or wire position do not cause false touches.
    # A reading clearly below the baseline (for example after the reset above,
    # if someone really was holding on) is followed quickly so touches work again.
    if not touched and raw < off_level:
        rate = 0.2 if raw < baseline * 0.98 else BASELINE_RATE
        baseline += (raw - baseline) * rate
        set_levels()

    if not touched:
        if fade <= 0:
            time.sleep(0.02)
            continue
        fade = max(0.0, fade - 0.05)  # fade out after release

    # Elapsed time since the touch, from integer nanoseconds: time.monotonic()
    # is a float that loses precision after the board has been on for hours.
    now = (time.monotonic_ns() - start) / 1e9
    scale = PEAK * fade / 255
    r, g, b = COLOR[0] * scale, COLOR[1] * scale, COLOR[2] * scale

    # Start the sound each time a new beat leaves LED 0, so it stays in step
    # with the light. After release the last thump plays out but no new one starts.
    if touched and int(now // BEAT_PERIOD) != last_beat:
        last_beat = int(now // BEAT_PERIOD)
        audio.play(thump)
    for i in range(NUM_LEDS):
        t = now - i * LED_DELAY
        if t < 0:
            strip[i] = 0  # the first beat has not reached this LED yet
        else:
            # min(): float rounding can give exactly STEPS, past the table end
            step = min(int((t % BEAT_PERIOD) / BEAT_PERIOD * STEPS), STEPS - 1)
            v = beat[step]
            strip[i] = (int(r * v), int(g * v), int(b * v))
    strip.show()
