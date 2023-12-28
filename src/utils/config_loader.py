import os
import yaml
from app_root import APP_ROOT


def load_config():
    # Load configuration from the main configuration file in the project root
    config_path = os.path.join(APP_ROOT, 'config.yaml')
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)
