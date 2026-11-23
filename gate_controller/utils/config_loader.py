import os
import yaml
from importlib.resources import files


def load_config():
    config_paths = [
        # User's home directory
        os.path.expanduser('~/.gate_controller/config.yaml'),

        # System-wide configuration
        '/etc/gate_controller/config.yaml'
    ]

    # Default configuration (packaged with the application)
    default_config = files('gate_controller').joinpath('config/config.yaml')
    config = yaml.safe_load(default_config.read_text(encoding='utf-8'))

    # Override with user-specified configurations
    for path in config_paths:
        if path and os.path.isfile(path):
            with open(path, 'r') as user_config_file:
                user_config = yaml.safe_load(user_config_file)

                # Update default config with user-specified values
                config.update(user_config)

    return config
