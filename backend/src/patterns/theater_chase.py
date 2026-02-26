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

# How many full chase cycles to show each color before switching
CYCLES_PER_COLOR = 15


class TheaterChasePattern(PatternBase):
    @property
    def name(self): return "Theater Chase"

    @property
    def description(self): return "Classic marquee/Broadway-style chasing lights cycling through colors"

    def run(self, neo, stop_event, alert_queue=None, color=None):
        num_leds = neo.num_leds
        color_index = 0
        alert_color = None        # Set when an alert overrides the color
        offset = 0
        frame_count = 0           # Counts every rendered frame

        while not stop_event.is_set():
            # Check for alert color override
            if alert_queue:
                try:
                    msg = alert_queue.get_nowait()
                    alert_color = msg.color
                    print(f"Theater Chase: Color overridden to {alert_color}")
                except queue.Empty:
                    pass

            # Determine which color to use this frame
            if alert_color:
                current_color = alert_color
            elif color:
                current_color = color
            else:
                current_color = CHASE_COLORS[color_index]

            # Render the chase frame
            neo.fill_strip(0, 0, 0)
            for i in range(offset, num_leds, 3):
                neo.set_led_color(i, *current_color)
            neo.update_strip()

            offset = (offset + 1) % 3
            frame_count += 1

            # Advance to the next preset color after CYCLES_PER_COLOR full 3-frame cycles
            # Only cycle when not locked to a fixed or alert color
            if not color and not alert_color:
                if frame_count >= CYCLES_PER_COLOR * 3:
                    frame_count = 0
                    color_index = (color_index + 1) % len(CHASE_COLORS)
                    print(f"Theater Chase: Advancing to color {CHASE_COLORS[color_index]}")

            time.sleep(0.1)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
