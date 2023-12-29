import sys
import time
from gate_controller.relay_controller import control_relay

# Define a mapping of high-level commands to relay indices
command_mapping = {
    'open': 0,  # Assuming relay 0 is connected to the open command
    'close': 1,  # Assuming relay 1 is connected to the close command
    'stop': 2,  # Assuming relay 2 is connected to the stop command
    'toggle': 3  # Assuming relay 3 is connected to the toggle command
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


if __name__ == "__main__":
    try:
        action = sys.argv[1]
        if action == 'status':
            print(get_status())
        else:
            control_gate(action)
    except IndexError:
        print("Usage: python gate_control.py <command>")
        sys.exit(1)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
