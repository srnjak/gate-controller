from flask import request
import ipaddress
from gate_controller.utils.config_loader import load_config

# Load configuration using the config_loader module
config_data = load_config()

# Extract configuration options
ALLOWED_IPS = config_data.get('allowed_ips', [])


def is_ip_allowed():
    client_ip = request.remote_addr
    client_ip_address = ipaddress.ip_address(client_ip)

    for ip_range in ALLOWED_IPS:
        if '/' in ip_range:
            # It's a CIDR range
            if client_ip_address in ipaddress.ip_network(ip_range):
                return True
        else:
            # It's a specific IP
            if client_ip_address == ipaddress.ip_address(ip_range):
                return True

    return False
