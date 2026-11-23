"""
A simulated gate drive behind the mock GPIO.

Relay pulses on the command outputs move the simulated gate, and the status
inputs follow the timing measured on the real drive. The position runs from
0.0 (closed) to 1.0 (open) at a constant speed.
"""

import threading
import time

# Delay between the command pulse and the start of the movement; the moving
# signal becomes active when the movement starts.
START_DELAY = 0.45
# The signal of the end position the gate leaves stays active this long after
# the movement starts.
END_POSITION_RELEASE = 1.2

CLOSED_POSITION = 0.0
OPEN_POSITION = 1.0


class GateSimulator:

    def __init__(self, relay_commands, closed_pin, open_pin, moving_pin,
                 low, high, travel_time=28.0, half_position=0.5,
                 clock=time.monotonic):
        """
        :param relay_commands: maps a relay output pin to its command
            ('open', 'close', 'half' or 'toggle')
        :param travel_time: seconds for a full travel between end positions
        :param half_position: where 'half' stops, between 0.0 and 1.0
        """
        if travel_time <= 0:
            raise ValueError(f'travel_time must be positive: {travel_time}')
        if not CLOSED_POSITION < half_position < OPEN_POSITION:
            raise ValueError(
                f'half_position must lie between the end positions: '
                f'{half_position}')
        unknown = set(relay_commands.values()) - {
            'open', 'close', 'half', 'toggle'}
        if unknown:
            raise ValueError(f'Unknown relay commands: {sorted(unknown)}')

        self._relay_commands = dict(relay_commands)
        self._closed_pin = closed_pin
        self._open_pin = open_pin
        self._moving_pin = moving_pin
        self._low = low
        self._high = high
        self._travel_time = travel_time
        self._half_position = half_position
        self._clock = clock
        self._lock = threading.Lock()

        self._relay_levels = {pin: high for pin in relay_commands}
        self._position = CLOSED_POSITION
        self._target = None          # None while the gate is at rest
        self._from_position = CLOSED_POSITION
        self._movement_start = 0.0
        self._last_direction = -1    # the gate last moved towards closed

    def on_output(self, pin, level):
        """Called by the mock GPIO for every output change."""
        if pin not in self._relay_commands:
            return
        with self._lock:
            previous = self._relay_levels[pin]
            self._relay_levels[pin] = level
            # A relay is switched on by driving its pin low.
            if previous == self._high and level == self._low:
                self._command(self._relay_commands[pin], self._clock())

    def level(self, pin):
        """Called by the mock GPIO to read an input."""
        with self._lock:
            now = self._clock()
            self._advance(now)
            if pin == self._moving_pin:
                active = self._is_moving(now)
            elif pin == self._closed_pin:
                active = self._end_position_active(CLOSED_POSITION, now)
            elif pin == self._open_pin:
                active = self._end_position_active(OPEN_POSITION, now)
            else:
                return self._high
            return self._low if active else self._high

    def position(self):
        """The simulated position, 0.0 (closed) to 1.0 (open)."""
        with self._lock:
            self._advance(self._clock())
            return self._position

    def _command(self, command, now):
        self._advance(now)
        if command == 'open':
            self._move_to(OPEN_POSITION, now)
        elif command == 'close':
            self._move_to(CLOSED_POSITION, now)
        elif command == 'half':
            self._move_to(self._half_position, now)
        elif self._target is not None:
            # toggle while moving: stop where the gate is
            self._target = None
        elif self._position == CLOSED_POSITION:
            self._move_to(OPEN_POSITION, now)
        elif self._position == OPEN_POSITION:
            self._move_to(CLOSED_POSITION, now)
        elif self._last_direction > 0:
            self._move_to(CLOSED_POSITION, now)
        else:
            self._move_to(OPEN_POSITION, now)

    def _move_to(self, target, now):
        if self._target is None and self._position == target:
            return
        self._from_position = self._position
        self._target = target
        self._movement_start = now + START_DELAY
        self._last_direction = 1 if target > self._position else -1

    def _advance(self, now):
        if self._target is None or now < self._movement_start:
            return
        travelled = (now - self._movement_start) / self._travel_time
        if self._target > self._from_position:
            self._position = min(self._from_position + travelled,
                                 self._target)
        else:
            self._position = max(self._from_position - travelled,
                                 self._target)
        if self._position == self._target:
            self._target = None

    def _is_moving(self, now):
        return self._target is not None and now >= self._movement_start

    def _end_position_active(self, end_position, now):
        if self._target is None:
            return self._position == end_position
        return (self._from_position == end_position
                and now < self._movement_start + END_POSITION_RELEASE)


def attach_simulator(settings):
    """
    Drive the mock GPIO with a simulated gate wired like the real one.

    :param settings: the 'simulator' configuration section; 'travel_time'
        and 'half_position' are optional
    """
    from gate_controller.mocks import MOCK_GPIO
    from gate_controller import gate_status, relay_controller
    from gate_controller.gate_controller import command_mapping

    if relay_controller.GPIO is not MOCK_GPIO:
        raise RuntimeError('The gate simulator needs the mock GPIO.')

    relay_commands = {relay_controller.Relay[index]: command
                      for command, index in command_mapping.items()}
    travel_time = float(settings.get('travel_time', 28.0))
    MOCK_GPIO.simulator = GateSimulator(
        relay_commands,
        closed_pin=gate_status.CLOSED_PIN,
        open_pin=gate_status.OPEN_PIN,
        moving_pin=gate_status.MOVING_PIN,
        low=MOCK_GPIO.LOW,
        high=MOCK_GPIO.HIGH,
        travel_time=travel_time,
        half_position=float(settings.get('half_position', 0.5)))
    MOCK_GPIO.print_with_timestamp(
        'Gate simulator attached: the gate is closed, full travel takes '
        f'{travel_time:g} s')
    return MOCK_GPIO.simulator
