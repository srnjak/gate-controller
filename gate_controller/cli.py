import sys
from gate_controller.gate_controller import control_gate


def cli():
    valid_actions = ['toggle', 'close', 'open', 'half']

    if len(sys.argv) != 2 or sys.argv[1] not in valid_actions:
        print("Usage: gate-controller <action>")
        print("Actions:")
        for action in valid_actions:
            print(f"  {action}")
        sys.exit(1)

    action = sys.argv[1]
    control_gate(action)


if __name__ == "__main__":
    cli()
