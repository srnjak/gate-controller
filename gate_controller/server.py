import json
import queue
import threading
import yaml
from importlib.resources import files
from flask import Flask, Response, jsonify, request, make_response
from gate_controller.gate_controller import control_gate
from gate_controller.gate_monitor import GateMonitor, STOPPED
from gate_controller.utils.movement_window import MovementWindow
from gate_controller.gate_status import (
    is_moving, note_movement, note_stop, read_state)
from werkzeug.middleware.proxy_fix import ProxyFix
from gate_controller.utils.ip_filter import is_ip_allowed
from gate_controller.utils.config_loader import load_config
from gate_controller import relay_controller
from gate_controller.mocks import MOCK_GPIO
from gate_controller.mocks.gate_simulator import attach_simulator

app = Flask(__name__)

# Load configuration using the config_loader module
config_data = load_config()

# Extract configuration options
SERVER_HOST_LISTEN = config_data.get('host_listen', '0.0.0.0')
SERVER_PORT = int(config_data.get('port', 5000))
DEBUG_MODE = config_data.get('debug', False)
TRUSTED_PROXIES = int(config_data.get('trusted_proxies', 0))

if TRUSTED_PROXIES < 0:
    raise ValueError(
        f'trusted_proxies must not be negative, got {TRUSTED_PROXIES}')

# Take the client address from the X-Forwarded-* headers only when they are
# set by trusted reverse proxies; a client could forge them otherwise
if TRUSTED_PROXIES > 0:
    app.wsgi_app = ProxyFix(app.wsgi_app,
                            x_for=TRUSTED_PROXIES, x_proto=TRUSTED_PROXIES)


# Custom middleware to filter requests based on allowed IPs
@app.before_request
def limit_remote_addr():
    if not is_ip_allowed():
        return "Forbidden", 403


def generate_openapi_spec(host, api_port):
    openapi_template = files('gate_controller').joinpath(
        'static/openapi_template.yaml').read_text(encoding='utf-8')
    return yaml.safe_load(openapi_template.format(host=host, port=api_port))


# Gate movements must be at least this many seconds apart, whether a client,
# the command line or a remote control started them
movement_window = MovementWindow(
    float(config_data.get('command_cooldown', 5)))

gate_monitor = GateMonitor(movement_window)

# Seconds between heartbeat comments on an idle event stream
HEARTBEAT_INTERVAL = 15

# One command at a time: each is judged by the gate state left by the
# previous one
command_lock = threading.Lock()


def run_command(command, message):
    with command_lock:
        # While the gate moves, any command stops it, and a stop is never
        # refused; at rest, the command starts a movement
        stop = is_moving()
        if not stop:
            retry_after = movement_window.try_start()
            if retry_after is not None:
                response = jsonify({
                    'status': 'Too soon after the previous gate movement; '
                              f'retry in {retry_after} s.'})
                response.headers['Retry-After'] = str(retry_after)
                return response, 429
        gate_monitor.note_command(command)
        control_gate(command)
        if stop:
            note_stop()
        else:
            note_movement()
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


@app.route('/gate/stop', methods=['POST'])
def stop_gate_route():
    # Unlike the other commands, a stop never starts a movement: at rest it
    # sends nothing, and it does not touch the movement window
    with command_lock:
        if not is_moving():
            return jsonify({'status': 'The gate is not moving; '
                                      'no command was sent.'}), 409
        gate_monitor.note_command('stop')
        control_gate('toggle')
        note_stop()
    return jsonify({'status': 'Stop gate command sent successfully.'}), 200


@app.route('/gate/status', methods=['GET'])
def gate_status_route():
    status, basis = read_state()
    return jsonify({'status': status, 'basis': basis}), 200


@app.route('/gate/events', methods=['GET'])
def gate_events_route():
    subscriber = gate_monitor.subscribe()

    def stream():
        try:
            while True:
                try:
                    event = subscriber.get(timeout=HEARTBEAT_INTERVAL)
                except queue.Empty:
                    yield ': heartbeat\n\n'
                    continue
                if event is STOPPED:
                    return
                yield (f'event: {event.name}\n'
                       f'data: {json.dumps(event.data)}\n\n')
        finally:
            gate_monitor.unsubscribe(subscriber)

    return Response(stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache'})


@app.route('/openapi', methods=['GET'])
def get_openapi_spec():
    host = request.host.split(':')[0]  # Extracts the hostname
    port = SERVER_PORT
    openapi_spec = generate_openapi_spec(host, port)
    return make_response(yaml.dump(openapi_spec), 200,
                         {'Content-Type': 'application/x-yaml'})


def main():
    if relay_controller.GPIO is MOCK_GPIO:
        attach_simulator(config_data.get('simulator', {}))
    gate_monitor.start()
    # Each event stream holds a thread for as long as its client is connected
    app.run(host=SERVER_HOST_LISTEN, port=SERVER_PORT, debug=DEBUG_MODE,
            threaded=True)


if __name__ == '__main__':
    main()
