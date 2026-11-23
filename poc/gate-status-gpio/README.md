# Reading gate state from GPIO inputs

Scripts that read GPIO inputs with the internal pull-up resistor enabled
(BCM numbering). They were run many times on the device in February 2024.

The purpose is an assumption, not a documented fact: they appear to test
reading the gate's position (for example limit switches) so that
`GET /gate/status` could report something other than `unknown`. Pins 17, 27
and 22 are not used by the relay board, which occupies 5, 6, 13, 16, 19, 20,
21 and 26. What, if anything, is wired to them is not recorded here.

- `gpio_read.py <pin>` reads a single pin once.
- `gpio_read2.py` reads pins 17, 27 and 22 once, after a 0.1 s pause.
- `gpio_read_denoise.py <pin>` takes 1000 readings and returns the majority
  value. An earlier version used 50 samples. The `delay` parameter is never
  used, so the samples are taken back to back.

All three require `RPi.GPIO` and call `GPIO.cleanup()` when done.
