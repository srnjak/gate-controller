#!/bin/bash

SERVICE_NAME=gate-controller
SERVICE_FILE=/etc/systemd/system/${SERVICE_NAME}.service
USER=pi  # Replace with the username under which the service should run

function setup_service() {
    # Check if the virtual environment path is passed as an argument
    if [ "$#" -ne 1 ]; then
        echo "Usage: $0 setup /path/to/virtualenv"
        exit 1
    fi

    VENV_PATH="$1"

    # Full path to the Python executable in the virtual environment
    PYTHON_EXEC="$VENV_PATH/bin/python"

    # Full path to the gate-controller-server script within the virtual environment
    GATE_CONTROLLER_SERVER_SCRIPT="$VENV_PATH/bin/gate-controller-server"

    if [ ! -f "$PYTHON_EXEC" ] || [ ! -f "$GATE_CONTROLLER_SERVER_SCRIPT" ]; then
        echo "Python executable or gate-controller-server not found in the provided virtual environment."
        exit 1
    fi

    echo "Creating systemd service for gate-controller-server..."

    # Create the systemd service file
    cat <<EOF | sudo tee $SERVICE_FILE
[Unit]
Description=Gate Controller Service
After=network.target

[Service]
User=$USER
ExecStart=$PYTHON_EXEC $GATE_CONTROLLER_SERVER_SCRIPT
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd, enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable ${SERVICE_NAME}.service
    sudo systemctl start ${SERVICE_NAME}.service

    echo "Service has been set up and started."
}

function cleanup_service() {
    echo "Removing systemd service for gate-controller-server..."

    # Stop the service if running
    sudo systemctl stop ${SERVICE_NAME}.service

    # Disable the service
    sudo systemctl disable ${SERVICE_NAME}.service

    # Remove the service file
    sudo rm -f $SERVICE_FILE

    # Reload systemd
    sudo systemctl daemon-reload

    echo "Service has been removed."
}

# Check if setup or cleanup is called
case "$1" in
    setup)
        setup_service "$2"
        ;;
    cleanup)
        cleanup_service
        ;;
    *)
        echo "Usage: $0 {setup|cleanup}"
        exit 1
        ;;
esac
