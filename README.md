# Gate Controller Project

## Overview
The Gate Controller Project is a Python-based application specifically designed for the Raspberry Pi, interfacing with the RPi Relay Board (B) for automated gate control. 
This project enables automated opening, closing, half opening, and toggling of gate systems using the Raspberry Pi's GPIO pins. 
It includes a server component built with Flask, offering a simple API for gate control operations. 
Tailored for the [Waveshare RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)), it ensures seamless integration and functionality.

## Requirements
- Python 3.9 or higher
- Raspberry Pi with GPIO pins
- [RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)) for relay control
- Flask for the server component

## Installation

Before installing `gate-controller`, you need to configure pip to use the custom repository where the package is hosted.

### Configuring Pip to Use the Custom Repository

1. Create or edit the `pip.conf` file in your home directory. 
   For Linux, this is typically located at `~/.config/pip/pip.conf`.

2. Add the following lines to `pip.conf`:

   ```
   [global]
   index-url = https://ci.srnjak.com/nexus/repository/py-public-group/simple/
   ```

   This tells pip to use your custom repository hosted on Nexus.

### Installing the RPI.GPIO package
1. Install the `RPi.GPIO` package, which is required for Raspberry Pi functionality:

   ```
   pip install RPi.GPIO
   ```


### Installing the Gate Controller

After configuring pip:

1. Ensure Python 3.9+ is installed on your Raspberry Pi.

2. Install the package using pip:

   ```
   pip install gate-controller
   ```

## Configuration

The `gate-controller` uses a `config.yaml` file for configuration. Customize the settings according to your requirements. Below is a table of the available configuration options, their default values, and examples.

### Configuration Options

| Option        | Default Value                    | Description                                                                                               | Example                                                                                                             |
|---------------|----------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `host_listen` | `'0.0.0.0'`                      | The host IP address on which the Flask server will listen. `'0.0.0.0'` listens on all network interfaces. | To listen only on the local machine, set to `'127.0.0.1'`.                                                          |
| `port`        | `5000`                           | The port number on which the server will listen.                                                          | To change the port, set to any valid port number, like `8080`.                                                      |
| `debug`       | `false`                          | Enables or disables debug mode. Useful for development.                                                   | Set to `true` for development to enable debug mode.                                                                 |
| `allowed_ips` | `['127.0.0.1','192.168.0.0/24']` | A list of IP addresses or subnets in CIDR notation that are allowed to access the server.                 | To allow only a specific IP, set to `['192.168.0.5']`. For two subnets, set to `['192.168.0.0/24', '10.0.0.0/24']`. |
| `trusted_proxies` | `0` | Number of reverse proxies in front of the server. With a value above `0`, the client address checked against `allowed_ips` is taken from the `X-Forwarded-For` header those proxies set. Keep `0` when clients connect directly, or any client can choose its own address with that header. | Behind a single nginx, set to `1`. |
| `status_inputs` | `{closed: 27, open: 22, moving: 17}` | GPIO inputs (BCM numbering) wired to the gate drive's status outputs. Each output must connect its input to GND while the signal is active; the inputs use the internal pull-up resistor. | To read the closed end position from GPIO 23, set `closed: 23`. The whole mapping is replaced, so list all three keys. |
| `command_cooldown` | `5` | Seconds after an accepted gate command during which the server rejects further commands from any client with `429 Too Many Requests`. `0` turns the limit off. | To allow a command every 10 seconds, set to `10`. |

### Customizing the Configuration

Create your own `config.yaml` file and specify the custom values based on the options in the table above. The application searches for this file in the following order:

1. A file located at `~/.gate_controller/config.yaml`.
2. A file located at `/etc/gate_controller/config.yaml`.

If no custom configuration file is found, the application uses the default settings packaged with the application.

## Usage

### Running the Server

Start the server by running the following command:

```
gate-controller-server
```

The server listens on `http://localhost:5000` by default. 
The port and other settings can be adjusted in the configuration file.

### Running the Gate Controller

To control the gate directly (without the server), use the following command:

```
gate-controller <action>
```

Replace `<action>` with `open`, `close`, `half`, or `toggle`.

The server and the command line record the last state of each relay in `~/.gate_controller/relay_states.json`.

## API Endpoints

The Gate Control API offers a range of endpoints for controlling the gate and querying its status, as well as accessing the OpenAPI documentation. 
These endpoints are part of the Flask server and are accessible when the server is running:

- **Open Gate**:
   - `POST /gate/open` - Sends a command to open the gate.

- **Close Gate**:
   - `POST /gate/close` - Sends a command to close the gate.

- **Half Open Gate**:
   - `POST /gate/half` - Half opens the gate.

- **Toggle Gate**:
   - `POST /gate/toggle` - Toggles the gate.

- **Gate Status**:
   - `GET /gate/status` - Retrieves the current status of the gate: `open`, `closed`, `moving`, or `intermediate` (at rest between the end positions).

- **OpenAPI Documentation**:
   - `GET /openapi` - Retrieves the OpenAPI documentation for the Gate Control API.

A command answers `200` once the relay pulse has been sent, and `500` if switching the relay or recording its state failed; the pulse may still have reached the gate drive, so check `GET /gate/status` before repeating the command.
A command that arrives within `command_cooldown` seconds after the previous accepted command, from any client, is rejected with `429 Too Many Requests` and a `Retry-After` header giving the seconds to wait; a rejected command does not extend the wait. The `gate-controller` command line runs in its own process and is not subject to this limit.
A client whose address is not listed in `allowed_ips` gets `403 Forbidden` from every endpoint.


## Uninstallation

To uninstall the package, use:

```
pip uninstall gate-controller
```

## Using Mocks (for Development)

For development without a physical Raspberry Pi, the project includes mock modules in the `mocks` directory. The `MOCK_GPIO.py` file simulates GPIO functionality, enabling testing and development on other systems.

When `RPi.GPIO` is not installed, `gate-controller-server` drives the mock GPIO with a simulated gate. It starts closed; the relay pulses of the gate commands move it, and `GET /gate/status` reports `moving`, `open`, `closed` or `intermediate` with the timing of the real drive. The optional `simulator` configuration section adjusts it:

```yaml
simulator:
  # Seconds for a full travel between the end positions (default 28).
  travel_time: 5
  # Where the half-open command stops, from 0 (closed) to 1 (open) (default 0.5).
  half_position: 0.5
```

The simulator state lives in the server process and starts from closed on every restart.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
