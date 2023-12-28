from flask import request
from config_loader import load_config

# Load configuration using the config_loader module
config_data = load_config()

# Extract configuration options
ALLOWED_IPS = config_data.get('allowed_ips', [])


def is_ip_allowed():
    client_ip = request.remote_addr
    return any(client_ip in ip_range for ip_range in ALLOWED_IPS)
