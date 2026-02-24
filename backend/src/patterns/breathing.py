# Breathing / Pulse - A single color that slowly fades in and out like breathing
from backend import PatternBase
import time
import queue
import math


class BreathingPattern(PatternBase):
    @property
    def name(self): return "Breathing"

    @property
    def description(self): return "A gentle fade in/out pulse, like breathing. Supports alert color changes."

    def run(self, neo, stop_event, alert_queue=None, color=(0, 100, 255)):
        num_leds = neo.num_leds
        current_color = color
        step = 0.0
        speed = 0.02  # Controls how fast the breath cycles

        while not stop_event.is_set():
            if alert_queue:
                try:
                    msg = alert_queue.get_nowait()
                    current_color = msg.color
                    print(f"Breathing: Color changed to {current_color}")
                except queue.Empty:
                    pass

            # Sine wave from 0 to 1, giving a smooth breath shape
            brightness = (math.sin(step * math.pi * 2) + 1) / 2

            r = int(current_color[0] * brightness)
            g = int(current_color[1] * brightness)
            b = int(current_color[2] * brightness)

            neo.fill_strip(r, g, b)
            neo.update_strip()

            step = (step + speed) % 1.0
            time.sleep(0.03)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
