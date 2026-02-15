import json

def load_json(path):

    with open(path) as f:
        file = json.load(f)

    return file


def write_json_file(path, data):

    with open(path, 'w') as f:
        json.dump(data, f)