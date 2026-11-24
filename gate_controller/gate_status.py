"""
Reads the gate position from the gate drive's status outputs.

Each output is a potential-free contact wired between a GPIO input and GND.
The inputs use the internal pull-up resistor, so an input reads LOW while its
contact is closed (the signal is active) and HIGH while it is open.

The moving input is wired to the drive's relay output for the warning lamp.
The output is active while the gate moves, but it also stays active while
the gate stands stopped part way, until a movement ends at its target. The
input alone therefore cannot tell a gate stopped part way from a moving one.
The controller remembers the stop pulses it sent itself, and takes a signal
that stays active for longer than a movement can take for a gate at rest.
"""

import threading
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    from gate_controller.mocks import MOCK_GPIO as GPIO

from gate_controller.utils.config_loader import load_config

OPEN = 'open'
CLOSED = 'closed'
MOVING = 'moving'
INTERMEDIATE = 'intermediate'

BASIS_SIGNALS = 'signals'
BASIS_STOP = 'stop'
BASIS_TIMEOUT = 'timeout'

_config = load_config()
_pins = _config['status_inputs']
CLOSED_PIN = int(_pins['closed'])
OPEN_PIN = int(_pins['open'])
MOVING_PIN = int(_pins['moving'])

# Seconds after which an active moving signal is taken for a gate at rest
MAX_TRAVEL_TIME = float(_config['max_travel_time'])
if MAX_TRAVEL_TIME <= 0:
    raise ValueError(
        f'max_travel_time must be positive, got {MAX_TRAVEL_TIME}')

_clock = time.monotonic


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


_lock = threading.Lock()
# When the moving signal was first seen active, or when the controller last
# started a movement; None while the signal is off
_active_since = None
# Set by a stop pulse of this controller while the moving signal is active;
# the gate stands still from then on, although the signal stays active
_stopped = False


def note_stop():
    """
    Record that the controller has just stopped the moving gate. Until the
    moving signal goes off or the controller starts a movement, the gate is
    reported at rest.
    """
    global _stopped
    with _lock:
        _stopped = True


def note_movement():
    """Record that the controller has just started a movement."""
    global _stopped, _active_since
    with _lock:
        _stopped = False
        _active_since = _clock()


def read_state():
    """
    Return the gate status and the basis it rests on, as a tuple.

    The status is 'moving', 'closed', 'open' or 'intermediate'. 'moving'
    takes precedence: the end position signal is still active for a moment
    after the gate starts to move. 'intermediate' means the gate is at rest
    between the end positions.

    The basis is 'signals' when the status is read from the status inputs,
    'stop' when the gate is reported at rest because the controller stopped
    it, and 'timeout' when it is assumed at rest because the moving signal
    has been active for longer than a movement can take.
    """
    global _stopped, _active_since
    with _lock:
        if not _is_active(MOVING_PIN):
            # Any movement has ended: a stop or a timer no longer applies
            _stopped = False
            _active_since = None
            return _rest_status(), BASIS_SIGNALS
        now = _clock()
        if _active_since is None:
            _active_since = now
        if _stopped:
            basis = BASIS_STOP
        elif now - _active_since > MAX_TRAVEL_TIME:
            basis = BASIS_TIMEOUT
        else:
            return MOVING, BASIS_SIGNALS
    status = _rest_status()
    return status, BASIS_SIGNALS if status != INTERMEDIATE else basis


def get_status():
    """The gate status alone; see read_state()."""
    return read_state()[0]


def is_moving():
    """Whether the gate is reported in motion; see read_state()."""
    return get_status() == MOVING


def _rest_status():
    """The position of a gate at rest, from the end position signals."""
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
