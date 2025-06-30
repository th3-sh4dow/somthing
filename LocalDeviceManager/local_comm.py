import json
import requests
import os

class LocalDeviceManager:
    def __init__(self, device_file='device_list.json'):
        with open(device_file, 'r') as f:
            self.devices = json.load(f)

    def send_command(self, device_name, command):
        device = self.devices.get(device_name)
        if not device:
            return f"[ERROR] Device '{device_name}' not found."

        if device["interface"] == "http":
            try:
                url = f"http://{device['ip']}:5000/command"
                response = requests.post(url, json={"command": command})
                return response.text
            except Exception as e:
                return f"[HTTP ERROR] {e}"

        elif device["interface"] == "adb":
            try:
                if command == "open_camera":
                    os.system("adb shell am start -a android.media.action.IMAGE_CAPTURE")
                elif command == "vibrate":
                    os.system("adb shell cmd vibrator vibrate 1000")
                return f"Command '{command}' executed via ADB."
            except Exception as e:
                return f"[ADB ERROR] {e}"

        return f"[ERROR] Unknown interface for {device_name}"
