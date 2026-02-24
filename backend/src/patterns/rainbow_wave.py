# Rainbow Wave - Smooth HSV rainbow that flows across the strip
from backend import PatternBase
import time
import queue
import math


def hsv_to_rgb(h, s, v):
    """Convert HSV (0-1 range) to RGB (0-255 range)"""
    if s == 0:
        c = int(v * 255)
        return (c, c, c)
    h6 = h * 6.0
    i = int(h6) % 6
    f = h6 - int(h6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    rgb = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
    return tuple(int(c * 255) for c in rgb)


class RainbowWavePattern(PatternBase):
    @property
    def name(self): return "Rainbow Wave"

    @property
    def description(self): return "A smooth HSV rainbow that flows across all LEDs"

    def run(self, neo, stop_event, alert_queue=None, speed=0.03):
        num_leds = neo.num_leds
        offset = 0.0

        while not stop_event.is_set():
            if alert_queue:
                try:
                    alert_queue.get_nowait()
                except queue.Empty:
                    pass

            for i in range(num_leds):
                hue = (offset + i / num_leds) % 1.0
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                neo.set_led_color(i, r, g, b)

            neo.update_strip()
            offset = (offset + 0.02) % 1.0
            time.sleep(speed)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
