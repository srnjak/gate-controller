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

### Installing the Gate Controller

After configuring pip:

1. Ensure Python 3.6+ is installed on your Raspberry Pi.

2. Install the package using pip:

   ```
   pip install gate-controller
   ```

## Configuration

The project uses `config.yaml` for its default configuration. 
The configuration can be customized in the following order of priority:
1. A file specified by the `--config` command line argument.
2. A file located at `~/.gate_controller/config.yaml`.
3. A file located at `/etc/gate_controller/config.yaml`.

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
