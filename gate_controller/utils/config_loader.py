import os
import yaml
import pkg_resources


def load_config():
    config_paths = [
        # Environment variable
        os.environ.get('GATE_CONTROLLER_CONFIG'),

        # User's home directory
        os.path.expanduser('~/.gate_controller/config.yaml'),

        # System-wide configuration
        '/etc/gate_controller/config.yaml'
    ]

    # Default configuration (packaged with the application)
    default_config_path = pkg_resources.resource_filename(
        'gate_controller', 'config/config.yaml')
    with open(default_config_path, 'r') as default_config_file:
        config = yaml.safe_load(default_config_file)

    # Override with user-specified configurations
    for path in config_paths:
        if path and os.path.isfile(path):
            with open(path, 'r') as user_config_file:
                user_config = yaml.safe_load(user_config_file)

                # Update default config with user-specified values
                config.update(user_config)

    return config
