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

def get_stdout(command: str, enforce_dict = False):
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
            info[key] = {'Error': result.stderr}

def get_camera_info():
    info = { "Camera Info": {} }
    data = get_stdout("termux-camera-info")
    for camera in data:
        info["Camera Info"][camera["facing"]] = camera
    return info

def get_generic_info():
    info = {}
    commands = {
        'Battery Status': 'termux-battery-status',
        'Wifi Connection': 'termux-wifi-connectioninfo',
    }

    for key, command in commands.items():
        try:
            info[key] = get_stdout(command, True)
        except Exception as e:
            info[key] = {'Exception': str(e)}
    return info

def get_all_info():
    camera_info = get_camera_info()
    generic_info = get_generic_info()
    merged_info = {**generic_info, **camera_info}
    return merged_info

@app.route('/', methods=['GET'])
def device_info():
    info = get_all_info()
    return render_template("device_info.html", info=info, title=f"{config["serverName"]}" if config["serverName"] else "Server Info", headerLinks=config["headerLinks"], accent=config["accentColor"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5540)