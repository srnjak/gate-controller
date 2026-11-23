#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO
import sys
import json

# Define the relay pins
Relay = [5, 6, 13, 16, 19, 20, 21, 26]

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup Relay pins
for i in range(0, 8):
    GPIO.setup(Relay[i], GPIO.OUT)
    GPIO.output(Relay[i], GPIO.HIGH)

# File to store relay states
state_file = "relay_states.json"

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

# Function to apply relay states from the file
def apply_relay_states():
    states = read_relay_states()
    for i in range(8):
        GPIO.output(Relay[i], GPIO.LOW if states[str(i)] == "on" else GPIO.HIGH)

# Main
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 test.py <relay_number> <on|off>")
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
