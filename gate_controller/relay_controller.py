#!/usr/bin/python3
# -*- coding: UTF-8 -*-

try:
    import RPi.GPIO as GPIO
except ImportError:
    from gate_controller.mocks import MOCK_GPIO as GPIO

import json
import os
import tempfile
import threading

# Define the relay pins
Relay = [5, 6, 13, 16, 19, 20, 21, 26]

# File to store relay states, next to the user configuration
state_file = os.path.expanduser('~/.gate_controller/relay_states.json')

# Serialises the read-modify-write of the state file between threads
state_lock = threading.Lock()


def initialize_gpio():
    """
    Initialize GPIO settings.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for i in range(0, 8):
        GPIO.setup(Relay[i], GPIO.OUT)
        GPIO.output(Relay[i], GPIO.HIGH)


initialize_gpio()  # Perform GPIO initialization when module is imported


# Function to read relay states from the file
def read_relay_states():
    try:
        with open(state_file, "r") as file:
            data = json.load(file)
            return data.get("relays", {})
    except FileNotFoundError:
        # Nothing recorded yet: all relays are off
        return {str(i): "off" for i in range(8)}


# Function to write relay states to the file
def write_relay_states(states):
    # Write a temporary file and rename it over the state file, so that a
    # reader never sees a partially written file
    state_dir = os.path.dirname(state_file)
    os.makedirs(state_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=state_dir, suffix='.tmp')
    try:
        with os.fdopen(fd, "w") as file:
            json.dump({"relays": states}, file, indent=4)
        os.replace(temp_path, state_file)
    except BaseException:
        os.unlink(temp_path)
        raise


# Function to control a relay
def control_relay(relay_index, state):
    # Apply the new state to the relay first, so that a failure to record
    # it cannot leave the relay in its previous state
    GPIO.output(Relay[relay_index], GPIO.LOW if state == "on" else GPIO.HIGH)
    with state_lock:
        states = read_relay_states()
        states[str(relay_index)] = state
        write_relay_states(states)


# Function to apply relay states from the file
def apply_relay_states():
    states = read_relay_states()
    for i in range(8):
        GPIO.output(Relay[i], GPIO.LOW if states[str(i)] == "on" else GPIO.HIGH)


# Main execution for standalone running
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 relay_controller.py <relay_number> <on|off>")
        sys.exit(1)

    relay_number = int(sys.argv[1])
    state = sys.argv[2].lower()

    if relay_number < 0 or relay_number > 7:
        print("Invalid relay number. Please choose a number between 0 and 7.")
        sys.exit(1)

    if state not in ["on", "off"]:
        print("Invalid state. Please choose 'on' or 'off'.")
        sys.exit(1)

    control_relay(relay_number, state)
    apply_relay_states()
