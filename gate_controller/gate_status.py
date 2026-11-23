"""
Reads the gate position from the gate drive's status outputs.

Each output is a potential-free contact wired between a GPIO input and GND.
The inputs use the internal pull-up resistor, so an input reads LOW while its
contact is closed (the signal is active) and HIGH while it is open.
"""

try:
    import RPi.GPIO as GPIO
except ImportError:
    from gate_controller.mocks import MOCK_GPIO as GPIO

from gate_controller.utils.config_loader import load_config

OPEN = 'open'
CLOSED = 'closed'
MOVING = 'moving'
INTERMEDIATE = 'intermediate'

_pins = load_config()['status_inputs']
CLOSED_PIN = int(_pins['closed'])
OPEN_PIN = int(_pins['open'])
MOVING_PIN = int(_pins['moving'])


class GateSignalError(Exception):
    """The status inputs report a combination the gate cannot be in."""


def initialize_inputs():
    """
    Configure the status pins as inputs with the internal pull-up resistor.
    """
    GPIO.setmode(GPIO.BCM)
    for pin in (CLOSED_PIN, OPEN_PIN, MOVING_PIN):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


initialize_inputs()  # Perform GPIO initialization when module is imported


def _is_active(pin):
    return GPIO.input(pin) == GPIO.LOW


def get_status():
    """
    Return the gate position: 'moving', 'closed', 'open' or 'intermediate'.

    'moving' takes precedence: the end position signal is still active for a
    moment after the gate starts to move. 'intermediate' means the gate is at
    rest between the end positions, for example after a half-open command.
    """
    if _is_active(MOVING_PIN):
        return MOVING

    closed = _is_active(CLOSED_PIN)
    is_open = _is_active(OPEN_PIN)
    if closed and is_open:
        raise GateSignalError(
            'Both end position signals are active '
            f'(closed: GPIO{CLOSED_PIN}, open: GPIO{OPEN_PIN}).')
    if closed:
        return CLOSED
    if is_open:
        return OPEN
    return INTERMEDIATE
