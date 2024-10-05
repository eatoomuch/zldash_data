import json
import os

# Load the JSON configuration

def get_config():
    path = os.path.dirname(os.path.dirname(__file__)) + '/src/config.json'
    with open(path) as config_file:
        config = json.load(config_file)

    return config

def get_env():
    config = get_config()

    return config['env']

def get_websocket_port():
    config = get_config()

    return config['websocket_port']

def get_server_url():
    config = get_config()
    return config['server_url']

def main():

    get_env()

    return