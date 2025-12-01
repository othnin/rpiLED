"""
Environment Configuration
Stores constants for the NeoPixel system
"""

#LED Strip Configuration
DEVICE = '/dev/spidev0.0'
NUM_LEDS = 17
SPI_SPEED = 800

# Patterns to start automatically when the PatternManager is initialized.
# Use names that match the pattern's `name` property.
STARTUP_PATTERNS = []  # e.g. ["My Pattern"]

# Optional mapping from hook event name -> pattern name. When a hook with
# the matching event_name triggers, the linked pattern will be started
# automatically by the manager.
HOOK_LINKS = {}  # e.g. {"cpu_over_20": "Loading Bar Pattern"}


PATTERN_FILE = 'pattern.txt'
PATTERN_LOCATION = "/opt/WOPR/backend/data/"
HOOK_FILE =    'hook.txt'