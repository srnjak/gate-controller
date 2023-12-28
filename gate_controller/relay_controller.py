#!/usr/bin/python3
# -*- coding: UTF-8 -*-

try:
    import RPi.GPIO as GPIO
except ImportError:
    from mocks import MOCK_GPIO as GPIO

import json
import os

# Define the relay pins
Relay = [5, 6, 13, 16, 19, 20, 21, 26]

# File to store relay states
runtime_data_dir = "runtime_data"
if not os.path.exists(runtime_data_dir):
    os.makedirs(runtime_data_dir)
state_file = "runtime_data/relay_states.json"


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
        # Initialize file with all relays off if it doesn't exist
        init_state = {"relays": {str(i): "off" for i in range(8)}}
        with open(state_file, "w") as file:
            json.dump(init_state, file, indent=4)
        return init_state["relays"]


# Function to write relay states to the file
def write_relay_states(states):
    with open(state_file, "w") as file:
        json.dump({"relays": states}, file, indent=4)


# Function to control a relay
def control_relay(relay_index, state):
    states = read_relay_states()
    states[str(relay_index)] = state
    write_relay_states(states)
    # Apply the new state to the relay
    GPIO.output(Relay[relay_index], GPIO.LOW if state == "on" else GPIO.HIGH)


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
