import json
import os

# Load the JSON configuration


def get_env():
    path = os.path.dirname(os.path.dirname(__file__)) + '/src/config.json'
    with open(path) as config_file:
        config = json.load(config_file)

    return config['env']

def main():

    get_env()

    return