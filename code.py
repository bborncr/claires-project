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
#   peak:  brightest red value (0-255); keep it low for long strips on USB power
PROFILES = {
    "strip144": {"leds": 144, "order": neopixel.GRB, "peak": 60},
    "strip47": {"leds": 47, "order": neopixel.RGB, "peak": 60},
}
PROFILE = "strip47"

NUM_LEDS = PROFILES[PROFILE]["leds"]
PEAK = PROFILES[PROFILE]["peak"]
BEAT_PERIOD = 0.9  # seconds per heartbeat (about 67 beats per minute)
TRAVEL_TIME = 1.0  # seconds for a beat to run from LED 0 to the last LED

VOLUME = 1.0  # heartbeat sound loudness (0.0-1.0); 0.02 is barely audible

BASELINE_RATE = 0.0005  # how quickly the baseline follows slow drift (about 40 s)

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

# One heartbeat, a strong beat followed by a softer one, as a table of red
# values so each frame only looks values up instead of doing maths per LED.
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
start = 0
last_beat = -1
fade = 0.0
strip.fill(0)
strip.show()

while True:
    raw = touch.raw_value
    if not touched and raw > on_level:
        touched = True
        start = time.monotonic()
        fade = 1.0
        last_beat = -1
        print("touched", raw)
    elif touched and raw < off_level:
        touched = False
        print("released", raw)

    # While nobody is touching, let the baseline slowly follow the reading so
    # changes in temperature, humidity or wire position do not cause false touches.
    if not touched and raw < off_level:
        baseline += (raw - baseline) * BASELINE_RATE
        set_levels()

    if not touched:
        if fade <= 0:
            time.sleep(0.02)
            continue
        fade = max(0.0, fade - 0.05)  # fade out after release

    now = time.monotonic() - start
    scale = PEAK * fade

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
            step = int((t % BEAT_PERIOD) / BEAT_PERIOD * STEPS)
            strip[i] = (int(scale * beat[step]), 0, 0)
    strip.show()
