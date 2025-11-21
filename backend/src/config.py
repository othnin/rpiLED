"""
Environment Configuration
Stores constants for the NeoPixel system
"""

# NeoPixel Strip Configuration
NEO_DEVICE = '/dev/spidev0.0'
NEO_NUM_LEDS = 17
NEO_SPI_SPEED = 800

# Patterns to start automatically when the PatternManager is initialized.
# Use names that match the pattern's `name` property.
STARTUP_PATTERNS = []  # e.g. ["My Pattern"]

# Optional mapping from hook event name -> pattern name. When a hook with
# the matching event_name triggers, the linked pattern will be started
# automatically by the manager.
HOOK_LINKS = {}  # e.g. {"cpu_over_20": "Loading Bar Pattern"}


PATTERN_FILE = '/opt/WOPR/backend/config/last_pattern.txt'
HOOK_FILE =    '/opt/WOPR/backend/config/last_hook.txt'