"""
Watches the gate drive's status inputs and publishes every change of the gate
state to subscribers, such as the clients of GET /gate/events.

The inputs are polled rather than watched with edge detection, so the monitor
behaves the same on the Raspberry Pi, with the mock GPIO and with the gate
simulator.
"""

import itertools
import queue
import threading
import time
from datetime import datetime, timezone

from gate_controller.gate_status import (
    CLOSED, GateSignalError, MOVING, OPEN, get_status)

# How often the status inputs are read
POLL_INTERVAL = 0.05
# A reading must stay the same this long before it is accepted as a change
STABLE_TIME = 0.1
# A change this soon after a relay pulse of the controller is caused by it
COMMAND_CAUSE_TIME = 2.0

OPENING = 'opening'
CLOSING = 'closing'
UNKNOWN = 'unknown'

_COMMAND_DIRECTIONS = {'open': OPENING, 'half': OPENING, 'close': CLOSING}

# Put into a subscriber's queue when the monitor has stopped
STOPPED = object()


def format_time(timestamp):
    """An ISO 8601 UTC time with whole seconds, such as 2026-11-23T18:04:11Z."""
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime(
        '%Y-%m-%dT%H:%M:%SZ')


class GateEvent:
    """
    One accepted gate state. `name` is the SSE event name: 'gate' for a status
    or 'error' when the status inputs report an impossible combination.
    """

    def __init__(self, name, data):
        self.name = name
        self.data = data


class GateMonitor:

    def __init__(self, movement_window, read_status=get_status,
                 clock=time.monotonic, wall_clock=time.time,
                 poll_interval=POLL_INTERVAL, stable_time=STABLE_TIME):
        """
        :param movement_window: a MovementWindow; a movement the controller
            did not start opens a new window, and every event reports when
            the window ends
        :param read_status: returns the gate status or raises GateSignalError
        """
        self._movement_window = movement_window
        self._read_status = read_status
        self._clock = clock
        self._wall_clock = wall_clock
        self._poll_interval = poll_interval
        self._stable_time = stable_time

        self._lock = threading.Lock()
        self._seq = itertools.count(1)
        self._subscribers = []
        self._current = None          # the last published GateEvent
        self._accepted = None         # the reading behind it
        self._candidate = None        # a different reading waiting to settle
        self._candidate_since = None
        self._candidate_wall = None
        self._last_command = None     # (name, clock time) of the last pulse
        self._failure = None
        self._thread = None

    def start(self):
        """Read the current state and keep watching in a daemon thread."""
        with self._lock:
            if self._thread is not None:
                raise RuntimeError('The gate monitor is already running.')
            reading = self._read()
            self._accept(reading, None, self._wall_clock())
            self._thread = threading.Thread(
                target=self._run, name='gate-monitor', daemon=True)
        self._thread.start()

    def note_command(self, command):
        """Record that the controller is about to pulse `command`."""
        with self._lock:
            self._last_command = (command, self._clock())

    def subscribe(self):
        """
        Return a queue that receives the current GateEvent first and then
        every accepted change; STOPPED ends it.
        """
        with self._lock:
            if self._failure is not None:
                raise RuntimeError(
                    'The gate monitor has stopped.') from self._failure
            if self._current is None:
                raise RuntimeError('The gate monitor has not been started.')
            subscriber = queue.Queue()
            subscriber.put(self._current)
            self._subscribers.append(subscriber)
            return subscriber

    def unsubscribe(self, subscriber):
        with self._lock:
            self._subscribers.remove(subscriber)

    def poll(self):
        """Read the status inputs once; the thread calls this repeatedly."""
        reading = self._read()
        with self._lock:
            now = self._clock()
            if reading == self._accepted:
                self._candidate = None
                return
            if reading != self._candidate:
                self._candidate = reading
                self._candidate_since = now
                self._candidate_wall = self._wall_clock()
                return
            if now - self._candidate_since >= self._stable_time:
                self._accept(reading, self._candidate_since,
                             self._candidate_wall)

    def _run(self):
        try:
            while True:
                time.sleep(self._poll_interval)
                self.poll()
        except BaseException as failure:
            with self._lock:
                self._failure = failure
                for subscriber in self._subscribers:
                    subscriber.put(STOPPED)
            raise

    def _read(self):
        """A reading: ('gate', status) or ('error', message)."""
        try:
            return 'gate', self._read_status()
        except GateSignalError as error:
            return 'error', str(error)

    def _accept(self, reading, since, at):
        """Publish `reading`, first seen at `since` (None on start)."""
        previous = self._accepted
        self._accepted = reading
        self._candidate = None

        kind, value = reading
        if kind == 'error':
            data = {'seq': next(self._seq), 'error': value}
        else:
            cause = None if since is None else self._cause(since)
            direction = None
            if value == MOVING:
                direction = self._direction(previous, cause)
                if cause == 'external':
                    self._movement_window.record()
            data = {'seq': next(self._seq), 'status': value,
                    'direction': direction, 'cause': cause}
        until = self._movement_window.until()
        data['cooldownUntil'] = None if until is None else format_time(
            # Round up, so that a movement at that time is accepted
            -(-until // 1))
        data['at'] = format_time(at)

        self._current = GateEvent(kind, data)
        for subscriber in self._subscribers:
            subscriber.put(self._current)

    def _cause(self, since):
        if self._last_command is not None:
            command, pulsed = self._last_command
            if 0 <= since - pulsed <= COMMAND_CAUSE_TIME:
                return f'command:{command}'
        return 'external'

    @staticmethod
    def _direction(previous, cause):
        if previous == ('gate', CLOSED):
            return OPENING
        if previous == ('gate', OPEN):
            return CLOSING
        if cause is not None and cause.startswith('command:'):
            return _COMMAND_DIRECTIONS.get(cause[len('command:'):], UNKNOWN)
        return UNKNOWN
