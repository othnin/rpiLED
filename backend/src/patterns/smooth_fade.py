# Smooth fade animation based on cosine
from math import cos
from backend import PatternBase
import time
import queue


class SmoothFadePattern(PatternBase):
    @property
    def name(self): return "Smooth Fade Pattern"
    
    @property  
    def description(self): return "Smooth fade animation based on cosine"

    def run(self, neo, stop_event, alert_queue=None):
        """
        Run the smooth fade pattern
        
        Args:
            neo: NeoPixel strip object
            stop_event: Threading event to stop pattern
            alert_queue: Queue for receiving HookMessage alerts (not used here)
        """
        while not stop_event.is_set():
            t = time.time()
            for i in range(neo.num_leds):
                if stop_event.is_set():
                    return  # Exit immediately
                intensity = int((cos(i * 0.01 + t) * 0.5 + 0.5) * 255)
                neo.set_led_color(i, intensity, intensity, intensity)
            neo.update_strip(sleep_duration=0.01)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()




'''
def smooth_fade(neo):
    t = time.time()
    for i in range(neo.num_leds):
        intensity = int((cos(i * 0.01 + t) * 0.5 + 0.5) * 255)
        neo.set_led_color(i, intensity, intensity, intensity)
    neo.update_strip(sleep_duration=0.01)


# Initialize Pi5Neo with 300 LEDs
neo = Pi5Neo('/dev/spidev0.0', num_leds=300, spi_speed_khz=800)

# Smooth fade effect
while True:
    smooth_fade(neo)
'''