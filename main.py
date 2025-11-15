from flask import Flask, render_template
import subprocess
import json

app = Flask(__name__)
config = {}
ddata = {}

with open("config.json", "r") as f:
    config = json.load(f)

with open("dummy.json", "r") as f:
    ddata = json.load(f)

def get_stdout_json(command: str, enforce_dict = False):
    if (ddata['useDummyData']):
        result = ddata['dummyData'][command]
        if isinstance(result, list) and enforce_dict:
            return {str(i): v for i, v in enumerate(result)}
        else:
            return result
    else:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            parsed = json.loads(result.stdout)
            if isinstance(parsed, list) and enforce_dict:
                return {str(i): v for i, v in enumerate(parsed)}
            else:
                return parsed
        else:
            return {'Error': result.stderr}

def parse_json_list_to_dict(command, key, ltdLabel):
    info = { f"{key}": {} }
    data = get_stdout_json(command)
    for item in data:
        info[key][item[ltdLabel]] = item
    return info

def parse_json(command, key):
    info = {}
    try:
        info[key] = get_stdout_json(command, True)
    except Exception as e:
        info[key] = {'Exception': str(e)}
    return info

def get_all_info():
    merged_info = {}
    for command, attr in config["modules"].items():
        if attr["type"] == "json":
            result = parse_json(command, attr["title"])
            merged_info = {**merged_info, **result}
        if attr["type"] == "json-enforce-dict":
            result = parse_json(command, attr["title"])
            merged_info = {**merged_info, **result}
        if attr["type"] == "json-list-to-dict":
            result = parse_json_list_to_dict(command, attr["title"], attr["ltdLabel"])
            merged_info = {**merged_info, **result}
    return merged_info

@app.route('/', methods=['GET'])
def device_info():
    info = get_all_info()
    return render_template("device_info.html", info=info, title=f"{config["serverName"]}" if config["serverName"] else "Server Info", headerLinks=config["headerLinks"], accent=config["accentColor"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config["port"])