import os
import yaml

def info_load_options():
    with open(os.path.join(os.path.dirname(__file__), "info_config.yml"), "r") as f:
        config = yaml.safe_load(f)
    return config