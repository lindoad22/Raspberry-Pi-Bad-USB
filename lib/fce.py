import json

def load_json(path):

    with open(path) as f:
        file = json.load(f)

    return file


def write_json_file(path, data):

    with open(path, 'w') as f:
        json.dump(data, f)


def write_to_csv(filename, status, error, script_name):

    with open(filename, "a") as f:
        
        clean_name = script_name.replace(",", " ")
        clean_error = error.replace(",", " ")
        
        log = status + "," + clean_error + "," + clean_name + "\n"
        f.write(log)


def read_csv_logs(filename):

    logs = []
    
    with open(filename, "r") as f:
        for line in f:
            parts = line.split(",")
            logs.append({
                "status": parts[0],
                "error": parts[1],
                "script_name": parts[2]
            })
    
    return logs

def open_html(path):
        with open(path) as f:
            return f.read()