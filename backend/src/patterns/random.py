#Random LED Blink
import time
import random
from backend import PatternBase
import queue

class RandomBlinkPattern(PatternBase):
    @property
    def name(self): return "Random Blink Pattern"
    
    @property  
    def description(self): return "Randomly blinks LEDs with random colors"

    def run(self, neo, stop_event, alert_queue=None):
        """
        Run the random blink pattern
        
        Args:
            neo: NeoPixel strip object
            stop_event: Threading event to stop pattern
            alert_queue: Queue for receiving HookMessage alerts (not used here)
        """
        while not stop_event.is_set():
            # Random number of LEDs to blink (1 to 1/3 of total LEDs)
            num_leds_to_blink = random.randint(1, max(1, neo.num_leds // 3))
            
            # Select random LED positions
            led_indices = random.sample(range(neo.num_leds), num_leds_to_blink)
            
            # Light up selected LEDs with random colors
            for led_index in led_indices:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                neo.set_led_color(led_index, *color)
            
            neo.update_strip()
            time.sleep(0.2)
            
            # Turn off all the LEDs
            for led_index in led_indices:
                neo.set_led_color(led_index, 0, 0, 0)
            
            neo.update_strip()
            time.sleep(0.1)

    def cleanup(self, neo):
        neo.clear_strip()
        neo.update_strip()



'''
def random_blink(neo, num_blinks=10, delay=0.2):
    for _ in range(num_blinks):
        led_index = random.randint(0, neo.num_leds - 1)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random color
        neo.set_led_color(led_index, *color)
        neo.update_strip()
        time.sleep(delay)
        neo.set_led_color(led_index, 0, 0, 0)  # Turn off the LED
        neo.update_strip()

# Initialize Pi5Neo with 10 LEDs
neo = Pi5Neo('/dev/spidev0.0', 10, 800)
random_blink(neo)
'''