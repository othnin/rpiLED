# Theater Chase - Classic marquee-style lights that chase in groups of 3
from backend import PatternBase
import time
import queue


CHASE_COLORS = [
    (255, 100, 0),   # Warm amber
    (0, 200, 255),   # Cyan
    (200, 0, 255),   # Purple
    (0, 255, 80),    # Green
    (255, 50, 50),   # Red
]


class TheaterChasePattern(PatternBase):
    @property
    def name(self): return "Theater Chase"

    @property
    def description(self): return "Classic marquee/Broadway-style chasing lights cycling through colors"

    def run(self, neo, stop_event, alert_queue=None, color=None):
        num_leds = neo.num_leds
        color_index = 0
        current_color = color or CHASE_COLORS[0]
        use_cycle = color is None  # If no color given, cycle through presets
        offset = 0

        while not stop_event.is_set():
            if alert_queue:
                try:
                    msg = alert_queue.get_nowait()
                    current_color = msg.color
                    use_cycle = False  # Lock to alert color
                    print(f"Theater Chase: Color locked to {current_color}")
                except queue.Empty:
                    pass

            neo.fill_strip(0, 0, 0)

            for i in range(offset, num_leds, 3):
                neo.set_led_color(i, *current_color)

            neo.update_strip()
            offset = (offset + 1) % 3

            # Advance color every full cycle
            if offset == 0 and use_cycle:
                color_index = (color_index + 1) % len(CHASE_COLORS)
                current_color = CHASE_COLORS[color_index]

            time.sleep(0.1)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
