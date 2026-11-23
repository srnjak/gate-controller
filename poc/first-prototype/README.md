# First prototype

The first gate API, written in December 2023 and later replaced by the
`gate_controller` package. It is kept as the project's starting point.

- `server.py` is a Flask app with `PUT /gate/{open,close,stop,toggle}`,
  `GET /gate/status` and `GET /openapi`. It runs with `debug=True` and calls
  the gate synchronously.
- `gate_control.py` maps commands to relays and pulses a relay for one second
  by running `test.py` as a subprocess.
- `test.py` sets one relay on or off, keeps the states in
  `relay_states.json` and applies them to the GPIO pins.
- `static/openapi.yaml` describes the API. Its server URL has been replaced
  with `localhost`; everything else is as it was.

The relay mapping differs from the current one: here `open`=0, `close`=1,
`stop`=2 and `toggle`=3, whereas the package uses `toggle`=0, `close`=1,
`open`=2 and `half`=3.
