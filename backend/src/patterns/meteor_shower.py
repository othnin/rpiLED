# Meteor / Shooting Star - A comet-like streak with a fading tail
from backend import PatternBase
import time
import queue


class MeteorPattern(PatternBase):
    @property
    def name(self): return "Meteor Shower"

    @property
    def description(self): return "A comet-like streak with a glowing fading tail that shoots across the strip"

    def run(self, neo, stop_event, alert_queue=None, color=(255, 255, 255), tail_length=6, delay=0.04):
        num_leds = neo.num_leds
        current_color = color
        fade_factor = 0.55  # How aggressively the tail fades (0=instant, 1=no fade)

        # Track brightness per LED for smooth tail
        brightness = [0.0] * num_leds

        position = 0  # Head of the meteor

        while not stop_event.is_set():
            if alert_queue:
                try:
                    msg = alert_queue.get_nowait()
                    current_color = msg.color
                except queue.Empty:
                    pass

            # Fade all LEDs
            for i in range(num_leds):
                brightness[i] *= fade_factor

            # Set head and draw tail
            for t in range(tail_length):
                idx = position - t
                if 0 <= idx < num_leds:
                    tail_brightness = 1.0 * ((tail_length - t) / tail_length) ** 2
                    brightness[idx] = max(brightness[idx], tail_brightness)

            # Render
            for i in range(num_leds):
                r = int(current_color[0] * brightness[i])
                g = int(current_color[1] * brightness[i])
                b = int(current_color[2] * brightness[i])
                neo.set_led_color(i, r, g, b)

            neo.update_strip()

            position += 1
            # After meteor has fully passed, reset with a short pause
            if position >= num_leds + tail_length:
                position = 0
                time.sleep(0.3)  # Pause before next streak

            time.sleep(delay)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
