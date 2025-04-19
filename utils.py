import json
import os
from bson import json_util

def load_config():
    base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, "config.json")
    with open(config_path, "r") as file:
        return json.load(file)

def get_sample_documents(collections):
    samples = {}
    for name, col in collections.items():
        doc = list(col.find({}, {"_id": 0}).limit(1))
        if doc:
            samples[name] = doc
    return samples

def format_json(data):
    return json.dumps(data, indent=2, default=json_util.default)