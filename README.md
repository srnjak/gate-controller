# Gate Controller Project

## Overview
The Gate Controller Project is a Python-based application specifically designed for the Raspberry Pi, interfacing with the RPi Relay Board (B) for automated gate control. 
This project enables the automated opening, closing, stopping, and toggling of gate systems using the GPIO pins on the Raspberry Pi. 
It includes a server component built with Flask, offering a simple API for gate control operations. 
Tailored for the [Waveshare RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)), it provides seamless integration and functionality.

## Requirements
- Python 3.6 or higher
- Raspberry Pi with GPIO pins
- [RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)) for relay control
- Flask for the server component

## Installation

### Setting Up the Environment
1. Ensure Python 3.6+ is installed on your Raspberry Pi.
2. Clone the repository or download the source code:
   ```
    git clone https://github.com/srnjak/gate-controller.git
   ```
3. Navigate to the project directory:
   ```
    cd gate-controller
   ```
4. Install required Python packages using the provided `requirements.txt`:
   ```
    pip3 install -r requirements.txt
   ```

## Configuration

The project uses `config.yaml` for configuration and automatically creates a `runtime_data` directory, if it doesn't exist, to store runtime-generated data such as relay states.

## Usage

### Running the Application

1. To control the gate, use the following command with the appropriate action:
   ```
    python3 gate_controller/gate_controller.py <action>
   ```
   Replace `<action>` with `open`, `close`, `stop`, or `toggle`.

2. To start the server and access the API for gate control:
   ```
    python3 gate_controller/server.py
   ```
   The server listens on `http://localhost:5000` by default.

## API Endpoints

The Gate Control API offers endpoints for controlling the gate and querying its status:

- **Open Gate**:
   - `PUT /gate/open`: Opens the gate.
- **Close Gate**:
   - `PUT /gate/close`: Closes the gate.
- **Stop Gate**:
   - `PUT /gate/stop`: Stops the gate's motion.
- **Toggle Gate**:
   - `PUT /gate/toggle`: Toggles the gate's state.
- **Gate Status**:
   - `GET /gate/status`: Retrieves the current status of the gate.

These endpoints are part of the Flask server, accessible when the server is running.

### Using Mocks (for Development)
To facilitate development without a physical Raspberry Pi, the project includes mock modules in the `mocks` directory. The `MOCK_GPIO.py` file simulates GPIO functionality, enabling testing and development on other systems.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
