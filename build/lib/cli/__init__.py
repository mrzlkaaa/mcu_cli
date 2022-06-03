import os
import json

def load_options():
    print(os.path.join(os.path.dirname(__file__), "config.json"))
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
        options = json.load(f)
    return options