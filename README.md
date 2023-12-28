# Gate Controller Project

## Overview
The Gate Controller Project is a Python-based application specifically designed for the Raspberry Pi, interfacing with the RPi Relay Board (B) for automated gate control. 
This project allows for the automated opening, closing, stopping, and toggling of gate systems using the GPIO pins on the Raspberry Pi. 
It also includes a server component built with Flask, offering a simple API for gate control operations. 
The project is tailored for the [Waveshare RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)), ensuring seamless integration and control functionality.

## Requirements
- Python 3.x
- Raspberry Pi with GPIO pins
- [RPi Relay Board (B)](https://www.waveshare.com/wiki/RPi_Relay_Board_(B)) for relay control
- Flask for the server component

## Installation

### Setting Up the Environment
1. Ensure you have Python 3 installed on your Raspberry Pi.
2. Clone the repository to your Raspberry Pi or download the source code.
3. Navigate to the project directory:
   ```
    cd my_project
   ```
4. Install required Python packages:
   ```
    pip3 install -r requirements.txt
   ```

## Configuration

No additional configuration is required for this project. 
The application automatically creates a `runtime_data` directory, if it doesn't exist, for storing runtime-generated data such as relay states.


## Usage

### Running the Application

1. To control the gate:

   ```
    python3 src/gate_controller.py <command>
   ```
   Replace `<command>` with `open`, `close`, `stop`, or `toggle`.

2. To start the server:
   ```
    python3 src/server.py
   ```
   The server provides an API to control the gate and can be accessed via the specified port.

## API Endpoints

The Gate Control API provides the following endpoints for controlling and querying the status of a gate:

- **Open Gate**:
   - `PUT /open`: Sends a command to open the gate.
- **Close Gate**:
   - `PUT /close`: Sends a command to close the gate.
- **Stop Gate**:
   - `PUT /stop`: Stops the gate's current action.
- **Toggle Gate**:
   - `PUT /toggle`: Toggles the gate's next action.
- **Gate Status**:
   - `GET /status`: Retrieves the current status of the gate.

These endpoints are accessible through the server running on `http://localhost:5000/gate`.


### Using Mocks (for Development)
For development on non-Raspberry Pi systems, the project includes a `mocks` directory. The MOCK_GPIO.py file simulates GPIO functionality, allowing for testing and development without a Raspberry Pi.

## License
This project is released under the [MIT License](https://opensource.org/licenses/MIT).
