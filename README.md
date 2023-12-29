# Gate Controller Project

## Overview
The Gate Controller Project is a Python-based application specifically designed for the Raspberry Pi, interfacing with the RPi Relay Board (B) for automated gate control. 
This project enables automated opening, closing, stopping, and toggling of gate systems using the Raspberry Pi's GPIO pins. 
It includes a server component built with Flask, offering a simple API for gate control operations. 
Tailored for the [Waveshare RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)), it ensures seamless integration and functionality.

## Requirements
- Python 3.6 or higher
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

1. Ensure Python 3.6+ is installed on your Raspberry Pi.

2. Install the package using pip:

   ```
   pip install gate-controller
   ```

## Configuration

The `gate-controller` uses a `config.yaml` file for configuration. Customize the settings according to your requirements. Below is a table of the available configuration options, their default values, and examples.

### Configuration Options

| Option        | Default Value        | Description                                                                                               | Example                                                                                                             |
|---------------|----------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `host_listen` | `'0.0.0.0'`          | The host IP address on which the Flask server will listen. `'0.0.0.0'` listens on all network interfaces. | To listen only on the local machine, set to `'127.0.0.1'`.                                                          |
| `port`        | `5000`               | The port number on which the server will listen.                                                          | To change the port, set to any valid port number, like `8080`.                                                      |
| `debug`       | `false`              | Enables or disables debug mode. Useful for development.                                                   | Set to `true` for development to enable debug mode.                                                                 |
| `allowed_ips` | `['192.168.0.0/24']` | A list of IP addresses or subnets in CIDR notation that are allowed to access the server.                 | To allow only a specific IP, set to `['192.168.0.5']`. For two subnets, set to `['192.168.0.0/24', '10.0.0.0/24']`. |

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

Replace `<action>` with `open`, `close`, `stop`, or `toggle`.

## API Endpoints

The Gate Control API provides endpoints for controlling the gate and querying its status. 
These endpoints are part of the Flask server and are accessible when the server is running:

- **Open Gate**: `PUT /gate/open`
- **Close Gate**: `PUT /gate/close`
- **Stop Gate**: `PUT /gate/stop`
- **Toggle Gate**: `PUT /gate/toggle`
- **Gate Status**: `GET /gate/status`

## Uninstallation

To uninstall the package, use:

```
pip uninstall gate-controller
```

## Using Mocks (for Development)

For development without a physical Raspberry Pi, the project includes mock modules in the `mocks` directory. The `MOCK_GPIO.py` file simulates GPIO functionality, enabling testing and development on other systems.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
