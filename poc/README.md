# Proof-of-concept code

Exploratory scripts written directly on the Raspberry Pi that runs the gate
controller, before or alongside the packaged application. They are kept here
for reference only: they are not part of the `gate_controller` package, are
not installed by `pip`, and are not maintained.

| Directory | Written | Purpose |
|-----------|---------|---------|
| [`first-prototype/`](first-prototype/) | December 2023 | The first Flask gate API, the predecessor of this project. |
| [`gate-status-gpio/`](gate-status-gpio/) | February 2024 | Reading GPIO inputs, presumably towards `GET /gate/status`. |
