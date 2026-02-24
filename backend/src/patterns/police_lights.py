# Police Lights - Alternating red/blue flashing halves, like emergency lights
from backend import PatternBase
import time
import queue


class PoliceLightsPattern(PatternBase):
    @property
    def name(self): return "Police Lights"

    @property
    def description(self): return "Alternating red and blue flashing halves like police emergency lights"

    def run(self, neo, stop_event, alert_queue=None):
        num_leds = neo.num_leds
        half = num_leds // 2
        flash_delay = 0.08
        phase = 0  # 0 or 1 to alternate sides

        while not stop_event.is_set():
            if alert_queue:
                try:
                    alert_queue.get_nowait()
                except queue.Empty:
                    pass

            neo.fill_strip(0, 0, 0)

            if phase == 0:
                # Red on left half, blue on right half
                for i in range(half):
                    neo.set_led_color(i, 255, 0, 0)
                for i in range(half, num_leds):
                    neo.set_led_color(i, 0, 0, 255)
            else:
                # Blue on left half, red on right half
                for i in range(half):
                    neo.set_led_color(i, 0, 0, 255)
                for i in range(half, num_leds):
                    neo.set_led_color(i, 255, 0, 0)

            neo.update_strip()
            phase = 1 - phase

            # Double-flash effect: flash twice quickly then pause
            time.sleep(flash_delay)
            if stop_event.is_set():
                break
            neo.fill_strip(0, 0, 0)
            neo.update_strip()
            time.sleep(flash_delay * 0.5)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()
