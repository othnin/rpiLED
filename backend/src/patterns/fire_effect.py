# Fire Effect - Randomized warm flicker simulating a flame
from backend import PatternBase
import time
import queue
import random


class FirePattern(PatternBase):
    @property
    def name(self): return "Fire Effect"

    @property
    def description(self): return "Randomized warm flickering that simulates a realistic flame"

    def run(self, neo, stop_event, alert_queue=None):
        num_leds = neo.num_leds
        # heat array - each LED has a heat value 0-255
        heat = [0] * num_leds

        while not stop_event.is_set():
            if alert_queue:
                try:
                    alert_queue.get_nowait()
                except queue.Empty:
                    pass

            # Step 1: Cool down every cell a little
            for i in range(num_leds):
                cooldown = random.randint(0, 40)
                heat[i] = max(0, heat[i] - cooldown)

            # Step 2: Heat drifts up and diffuses
            for i in range(num_leds - 1, 1, -1):
                heat[i] = (heat[i - 1] + heat[i - 2] + heat[i - 2]) // 3

            # Step 3: Randomly ignite new sparks near the bottom
            if random.random() < 0.6:
                spark = random.randint(0, min(3, num_leds - 1))
                heat[spark] = min(255, heat[spark] + random.randint(160, 255))

            # Step 4: Map heat to colors (black → red → yellow → white)
            for i in range(num_leds):
                h = heat[i]
                if h < 85:
                    r, g, b = h * 3, 0, 0
                elif h < 170:
                    r, g, b = 255, (h - 85) * 3, 0
                else:
                    r, g, b = 255, 255, (h - 170) * 3

                # Reverse so fire "rises" from LED 0
                neo.set_led_color(num_leds - 1 - i, r, g, b)

            neo.update_strip()
            time.sleep(0.05)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
