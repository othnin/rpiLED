# Twinkle / Starfield - Random LEDs blink on and fade out like stars twinkling
from backend import PatternBase
import time
import queue
import random


class TwinklePattern(PatternBase):
    @property
    def name(self): return "Twinkle Stars"

    @property
    def description(self): return "Random LEDs blink and fade like a twinkling starfield"

    def run(self, neo, stop_event, alert_queue=None, color=None):
        """
        color: if None, each star gets a random color. Pass an RGB tuple to use a fixed color.
        """
        num_leds = neo.num_leds
        fixed_color = color

        # Each LED: [r, g, b, brightness (0.0-1.0), fading (bool)]
        stars = [[0, 0, 0, 0.0, False] for _ in range(num_leds)]

        def random_color():
            if fixed_color:
                return list(fixed_color)
            return [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)]

        while not stop_event.is_set():
            if alert_queue:
                try:
                    msg = alert_queue.get_nowait()
                    fixed_color = msg.color
                except queue.Empty:
                    pass

            # Randomly spawn new stars
            for i in range(num_leds):
                if stars[i][3] == 0.0 and random.random() < 0.08:
                    c = random_color()
                    stars[i] = [c[0], c[1], c[2], 1.0, True]

            # Fade out active stars
            for i in range(num_leds):
                if stars[i][3] > 0.0:
                    stars[i][3] = max(0.0, stars[i][3] - random.uniform(0.03, 0.08))

            # Render
            for i in range(num_leds):
                bri = stars[i][3]
                r = int(stars[i][0] * bri)
                g = int(stars[i][1] * bri)
                b = int(stars[i][2] * bri)
                neo.set_led_color(i, r, g, b)

            neo.update_strip()
            time.sleep(0.05)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
