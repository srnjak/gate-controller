import math
import threading
import time


class CommandCooldown:
    """
    Accepts a gate command only when a cooldown has passed since the previous
    accepted command. Rejected commands do not extend the cooldown.
    """

    def __init__(self, seconds, clock=time.monotonic):
        if seconds < 0:
            raise ValueError(
                f'command_cooldown must not be negative, got {seconds}')
        self._seconds = seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._last_accepted = None

    def try_accept(self):
        """
        Accept a command and start a new cooldown, returning None, or return
        the whole seconds left until a command will be accepted again.
        """
        with self._lock:
            now = self._clock()
            if self._last_accepted is not None:
                remaining = self._last_accepted + self._seconds - now
                if remaining > 0:
                    return math.ceil(remaining)
            self._last_accepted = now
            return None
