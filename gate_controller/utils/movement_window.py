import math
import threading
import time


class MovementWindow:
    """
    Keeps gate movements at least a given number of seconds apart, whatever
    started them. A refused movement does not extend the window.
    """

    def __init__(self, seconds, clock=time.monotonic, wall_clock=time.time):
        if seconds < 0:
            raise ValueError(
                f'command_cooldown must not be negative, got {seconds}')
        self._seconds = seconds
        self._clock = clock
        self._wall_clock = wall_clock
        self._lock = threading.Lock()
        self._last_movement = None
        self._last_movement_wall = None

    def try_start(self):
        """
        Accept a movement and start a new window, returning None, or return
        the whole seconds left until a movement will be accepted again.
        """
        with self._lock:
            now = self._clock()
            if self._last_movement is not None:
                remaining = self._last_movement + self._seconds - now
                if remaining > 0:
                    return math.ceil(remaining)
            self._start(now)
            return None

    def record(self):
        """Start a new window for a movement that was not asked for here."""
        with self._lock:
            self._start(self._clock())

    def until(self):
        """
        The wall-clock time (seconds since the epoch) from which the next
        movement will be accepted, or None when one would be accepted now.
        """
        with self._lock:
            if self._last_movement is None:
                return None
            if self._clock() >= self._last_movement + self._seconds:
                return None
            return self._last_movement_wall + self._seconds

    def _start(self, now):
        self._last_movement = now
        self._last_movement_wall = self._wall_clock()
