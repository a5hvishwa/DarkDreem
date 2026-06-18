"""
generate_tone.py — Generates a synthesized alert/alarm WAV file for the simulation.
Uses pure math (sine waves) to create an unsettling but non-harmful alert tone.
No external audio files required.
"""

import wave
import struct
import math
import os

SAMPLE_RATE = 44100
DURATION_SECONDS = 130  # ~2 min 10 sec (extra buffer)
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alert_tone.wav")


def generate_alert_tone():
    """Generate a multi-layered alert tone that sounds like an alarm/warning siren."""
    num_samples = SAMPLE_RATE * DURATION_SECONDS
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE

        # Slow siren sweep between 400Hz and 800Hz (period ~3 seconds)
        siren_freq = 600 + 200 * math.sin(2 * math.pi * 0.33 * t)
        siren = 0.4 * math.sin(2 * math.pi * siren_freq * t)

        # Pulsing beep at 1000Hz, pulsing on/off every 0.5 seconds
        pulse = 0.5 * (1 + math.sin(2 * math.pi * 2 * t))  # 2 Hz pulse envelope
        beep = 0.25 * pulse * math.sin(2 * math.pi * 1000 * t)

        # Low rumble at 80Hz for menacing undertone
        rumble = 0.15 * math.sin(2 * math.pi * 80 * t)

        # Combine and clamp
        combined = siren + beep + rumble
        combined = max(-1.0, min(1.0, combined))

        # Convert to 16-bit integer
        sample_int = int(combined * 32000)
        samples.append(sample_int)

    # Write WAV file (batch pack for speed)
    with wave.open(OUTPUT_FILE, "w") as wf:
        wf.setnchannels(1)       # mono
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    print(f"[✓] Alert tone generated: {OUTPUT_FILE}")
    print(f"    Duration: {DURATION_SECONDS} seconds | Sample Rate: {SAMPLE_RATE} Hz")


if __name__ == "__main__":
    generate_alert_tone()
