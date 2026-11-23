import subprocess
import sys
import time

# Define a mapping of high-level commands to relay numbers
command_mapping = {
    'open': '0',
    'close': '1',
    'stop': '2',  # Assuming relay 2 is connected to the stop command
    'toggle': '3'  # Assuming relay 3 is connected to the toggle command
}

# Relay activation duration in seconds
relay_activation_duration = 1

def control_relay(relay_number, state):
    # Trigger the relay to turn on
    subprocess.run(['python', './test.py', relay_number, state], check=True)
    # Wait for the specified duration
    time.sleep(relay_activation_duration)
    # Turn the relay off if the state was 'on'
    if state == 'on':
        subprocess.run(['python', './test.py', relay_number, 'off'], check=True)

def control_gate(command):
    if command in command_mapping:
        relay_number = command_mapping[command]
        control_relay(relay_number, 'on')
    else:
        raise ValueError("Invalid command received")

def get_status():
    # Placeholder for gate status retrieval logic
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
