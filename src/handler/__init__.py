import os
import json
import yaml

def load_options():
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
        config = json.load(f)
    return config

def info_load_options():
    with open(os.path.join(os.path.dirname(__file__), "info_config.yml"), "r") as f:
        config = yaml.safe_load(f)
    return config