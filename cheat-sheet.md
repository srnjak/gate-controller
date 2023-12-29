# Gate Controller Installation Cheat Sheet

## 1. Configure Pip for Custom Repository
Configure `pip` to use the custom repository where `gate-controller` is hosted.

- **Edit Pip Configuration**:
  1. Create or edit `~/.config/pip/pip.conf`.
  2. Add the following lines:
     ```
     [global]
     index-url = https://ci.srnjak.com/nexus/repository/py-public-group/simple/
     ```

## 2. Set Up a Virtual Environment (Recommended)
Create and activate a virtual environment for the project.

- **Create Virtual Environment**:
  ```
  python3 -m venv /path/to/venv/gate-controller-env
  ```
- **Activate Virtual Environment**:
    ```
    source /path/to/venv/gate-controller-env/bin/activate
    ```

## 3. Install Gate Controller
Install the package and its Raspberry Pi dependency within the virtual environment.

- **Installation Command**:
  ```
  pip install RPi.GPIO
  pip install gate-controller
  ```

## 4. Set Up Gate Controller as a Daemon

To set up `gate-controller-server` to run as a systemd service, use the provided script. This will configure the service to start automatically when the system boots.

### Download and Run the Setup Script

1. **Download the Script**:
   Download `setup_service.sh` from the GitHub repository to your local machine.
   ```
   wget https://raw.githubusercontent.com/srnjak/gate-controller/master/scripts/setup_service.sh
   ```
   or
   ```
   curl -O https://raw.githubusercontent.com/srnjak/gate-controller/master/scripts/setup_service.sh
   ```

2. **Make the Script Executable**:
   Change the script's permissions to make it executable.
   ```
   chmod +x setup_service.sh
   ```

3. **Run the Setup Script**:
   Execute the script, providing the path to your virtual environment.
   ```
   ./setup_service.sh setup /path/to/venv/gate-controller-env
   ```

   Replace `/path/to/venv/gate-controller-env` with the actual path to your virtual environment.

### Notes:

- The script will create and configure a systemd service for `gate-controller-server`.
- Ensure you have the necessary permissions to execute the script, especially for creating a service in `/etc/systemd/system` and controlling systemd.
- Running the script might require `sudo` privileges depending on your system's configuration.

## 5. Customize Configuration (Optional)
Modify the `config.yaml` file for custom settings in one of the following locations:

1. A file specified by the `--config` command line argument.
2. `~/.gate_controller/config.yaml` for user-specific configuration.
3. `/etc/gate_controller/config.yaml` for system-wide configuration.

## 6. Remove the Gate Controller Service
Before uninstalling the package, use the script to remove the systemd service.

- **Run Cleanup Script**:
  ```
  ./setup_service.sh cleanup
  ```
### Notes
- Running the cleanup script will disable and remove the systemd service for `gate-controller-server`, ensuring a clean uninstallation.
- After running the cleanup, you can safely uninstall the package using `pip`.
- Ensure you deactivate the virtual environment when you're finished to return to your system's global Python environment.

## 7. Uninstall Gate Controller
To remove the package and its dependencies, use the following command within the virtual environment.

- **Uninstallation Command**:
  ```
  pip uninstall gate-controller
  ```

## Configuration Options
- `host_listen`: Host IP for the server (default `'0.0.0.0'`).
- `port`: Port number for the server (default `5000`).
- `debug`: Enable/disable debug mode (default `false`).
- `allowed_ips`: List of allowed IPs/subnets (default `['192.168.0.0/24']`).

## Additional Notes
- Refer to the project's README for detailed API endpoints and further usage instructions.
- The default configuration is suitable for most setups. Customize only if necessary.
- Ensure the virtual environment is activated whenever working with `gate-controller`.
