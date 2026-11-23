import os
import yaml
from flask import Flask, jsonify, request, make_response
from gate_controller.gate_controller import control_gate
from gate_controller.utils.command_cooldown import CommandCooldown
from gate_controller.gate_status import get_status
from werkzeug.middleware.proxy_fix import ProxyFix
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


# Custom middleware to filter requests based on allowed IPs
@app.before_request
def limit_remote_addr():
    if not is_ip_allowed():
        return "Forbidden", 403


def generate_openapi_spec(host, api_port):
    with open(os.path.join('static', 'openapi_template.yaml'), 'r') as file:
        openapi_template = file.read()
    return yaml.safe_load(openapi_template.format(host=host, port=api_port))


# A command from any client that arrives within this many seconds after the
# previous accepted command is rejected; the CLI is not covered
command_cooldown = CommandCooldown(
    float(config_data.get('command_cooldown', 5)))


def run_command(command, message):
    retry_after = command_cooldown.try_accept()
    if retry_after is not None:
        response = jsonify({'status': 'Too soon after the previous gate '
                                      f'command; retry in {retry_after} s.'})
        response.headers['Retry-After'] = str(retry_after)
        return response, 429
    control_gate(command)
    return jsonify({'status': message}), 200


@app.route('/gate/toggle', methods=['POST'])
def toggle_gate_route():
    return run_command('toggle', 'Toggling gate command sent successfully.')


@app.route('/gate/close', methods=['POST'])
def close_gate_route():
    return run_command('close', 'Closing gate command sent successfully.')


@app.route('/gate/open', methods=['POST'])
def open_gate_route():
    return run_command('open', 'Opening gate command sent successfully.')


@app.route('/gate/half', methods=['POST'])
def half_gate_route():
    return run_command('half', 'Half open gate command sent successfully.')


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
