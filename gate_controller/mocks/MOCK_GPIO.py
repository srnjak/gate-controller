# Import the datetime module
from datetime import datetime

# Constants
BCM = 'BCM'
BOARD = 'BOARD'
OUT = 'OUT'
IN = 'IN'
LOW = 0
HIGH = 1
PUD_UP = 'PUD_UP'
PUD_DOWN = 'PUD_DOWN'

# Variables to hold the state
mode_set = None
warnings_set = False

# Levels returned by input(). A pin not listed here reads HIGH, as an input
# with the pull-up resistor and nothing pulling it low does.
input_levels = {}

# Helper function to print with timestamp
def print_with_timestamp(message):
    # Get the current timestamp in ISO standard format
    timestamp = datetime.now().isoformat()
    # Print the timestamp and the message
    print(f"{timestamp} - {message}")

def setmode(mode):
    global mode_set
    mode_set = mode
    print_with_timestamp(f"GPIO Mode set to {mode}")

# noinspection SpellCheckingInspection
def setwarnings(flag):
    global warnings_set
    warnings_set = flag
    print_with_timestamp(f"GPIO Warnings set to {'On' if flag else 'Off'}")

def setup(channel, state, pull_up_down=None):
    pull = f" with {pull_up_down}" if pull_up_down else ""
    print_with_timestamp(f"Setting channel {channel} to {state}{pull}")

def input(channel):
    return input_levels.get(channel, HIGH)

def output(channel, state):
    print_with_timestamp(f"Setting channel {channel} to {state}")

def cleanup():
    print_with_timestamp("Cleaning up GPIO")
