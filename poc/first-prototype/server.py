from flask import Flask, jsonify, send_from_directory
from gate_control import control_gate, get_status

app = Flask(__name__)

@app.route('/gate/open', methods=['PUT'])
def open_gate_route():
    control_gate('open')
    return jsonify({'status': 'Opening gate command sent successfully.'}), 200

@app.route('/gate/close', methods=['PUT'])
def close_gate_route():
    control_gate('close')
    return jsonify({'status': 'Closing gate command sent successfully.'}), 200

@app.route('/gate/stop', methods=['PUT'])
def stop_gate_route():
    control_gate('stop')
    return jsonify({'status': 'Stopping gate command sent successfully.'}), 200

@app.route('/gate/toggle', methods=['PUT'])
def toggle_gate_route():
    control_gate('toggle')
    return jsonify({'status': 'Toggling gate action command sent successfully.'}), 200

@app.route('/gate/status', methods=['GET'])
def gate_status_route():
    status = get_status()
    return jsonify({'status': status}), 200

@app.route('/openapi', methods=['GET'])
def get_openapi_spec():
    return send_from_directory('static', 'openapi.yaml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
