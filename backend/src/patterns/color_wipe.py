# Color Wipe - Fills the strip one LED at a time, then wipes it off, cycling colors
from backend import PatternBase
import time
import queue


WIPE_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 165, 0),
    (128, 0, 128),
    (0, 255, 200),
]


class ColorWipePattern(PatternBase):
    @property
    def name(self): return "Color Wipe"

    @property
    def description(self): return "Fills LEDs one by one with a color then wipes them off, cycling through colors"

    def run(self, neo, stop_event, alert_queue=None):
        num_leds = neo.num_leds
        color_index = 0

        while not stop_event.is_set():
            current_color = WIPE_COLORS[color_index % len(WIPE_COLORS)]

            # Check for alert override
            if alert_queue:
                try:
                    msg = alert_queue.get_nowait()
                    current_color = msg.color
                except queue.Empty:
                    pass

            # Wipe ON
            for i in range(num_leds):
                if stop_event.is_set():
                    return
                neo.set_led_color(i, *current_color)
                neo.update_strip()
                time.sleep(0.05)

            time.sleep(0.3)

            # Wipe OFF
            for i in range(num_leds):
                if stop_event.is_set():
                    return
                neo.set_led_color(i, 0, 0, 0)
                neo.update_strip()
                time.sleep(0.05)

            color_index += 1
            time.sleep(0.1)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
