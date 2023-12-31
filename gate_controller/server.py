import os
import yaml
from flask import Flask, jsonify, request, make_response
from gate_controller.gate_controller import control_gate, get_status
from werkzeug.middleware.proxy_fix import ProxyFix
from threading import Thread
from gate_controller.utils.ip_filter import is_ip_allowed
from gate_controller.utils.config_loader import load_config

app = Flask(__name__)

# Load configuration using the config_loader module
config_data = load_config()

# Extract configuration options
SERVER_HOST_LISTEN = config_data.get('host_listen', '0.0.0.0')
SERVER_PORT = int(config_data.get('port', 5000))
DEBUG_MODE = config_data.get('debug', False)

# Configure the application to handle proxy headers for correct IP handling
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


def async_control_gate(action):
    """Function to run control_gate() in a separate thread."""
    Thread(target=control_gate, args=(action,)).start()


# Custom middleware to filter requests based on allowed IPs
@app.before_request
def limit_remote_addr():
    if not is_ip_allowed():
        return "Unauthorized", 401


def generate_openapi_spec(host, api_port):
    with open(os.path.join('static', 'openapi_template.yaml'), 'r') as file:
        openapi_template = file.read()
    return yaml.safe_load(openapi_template.format(host=host, port=api_port))


@app.route('/gate/toggle', methods=['PUT'])
def toggle_gate_route():
    async_control_gate('toggle')
    return jsonify({'status': 'Toggling gate command sent successfully.'}), 200


@app.route('/gate/close', methods=['PUT'])
def close_gate_route():
    async_control_gate('close')
    return jsonify({'status': 'Closing gate command sent successfully.'}), 200


@app.route('/gate/open', methods=['PUT'])
def open_gate_route():
    async_control_gate('open')
    return jsonify({'status': 'Opening gate command sent successfully.'}), 200


@app.route('/gate/half', methods=['PUT'])
def half_gate_route():
    async_control_gate('half')
    return jsonify(
        {'status': 'Half open gate command sent successfully.'}), 200


@app.route('/gate/status', methods=['GET'])
def gate_status_route():
    status = get_status()
    return jsonify({'status': status}), 200


@app.route('/openapi', methods=['GET'])
def get_openapi_spec():
    host = request.host.split(':')[0]  # Extracts the hostname
    port = SERVER_PORT
    openapi_spec = generate_openapi_spec(host, port)
    return make_response(yaml.dump(openapi_spec), 200,
                         {'Content-Type': 'application/x-yaml'})


def main():
    app.run(host=SERVER_HOST_LISTEN, port=SERVER_PORT, debug=DEBUG_MODE)


if __name__ == '__main__':
    main()
