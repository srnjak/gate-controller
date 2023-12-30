import time
from gate_controller.relay_controller import control_relay

# Define a mapping of high-level commands to relay indices
command_mapping = {
    'toggle': 0,
    'close': 1,
    'open': 2,
    'half': 3
}

# Relay activation duration in seconds
relay_activation_duration = 1


def control_gate(command):
    if command in command_mapping:
        relay_index = command_mapping[command]
        control_relay(relay_index, 'on')  # Turn the relay on
        time.sleep(relay_activation_duration)
        control_relay(relay_index, 'off')  # Turn the relay off
    else:
        raise ValueError("Invalid command received")


def get_status():
    # TODO Placeholder for gate status retrieval logic
    return 'unknown'
