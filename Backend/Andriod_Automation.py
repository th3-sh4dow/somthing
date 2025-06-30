# Android_Automation.py
# This module prepares automation commands to be executed by the Android device only.

SUPPORTED_APPS = {
    "whatsapp": "com.whatsapp",
    "chrome": "com.android.chrome",
    "youtube": "com.google.android.youtube",
    "gmail": "com.google.android.gm",
    "settings": "com.android.settings",
    "camera": "com.android.camera"
}

def TranslateAndroidCommand(command: str) -> dict:
    """
    Translates Android-targeted commands into structured response:
    {
        'response': str,
        'device_action': {
            'target': 'android',
            'command': 'open whatsapp'
        }
    }
    """
    cmd = command.lower().strip()

    if cmd.startswith("open "):
        app = cmd.removeprefix("open ").strip()
        if app in SUPPORTED_APPS:
            return {
                "response": f"Opening {app.capitalize()} on your device.",
                "device_action": {
                    "target": "android",
                    "command": f"open {app}"
                }
            }
        else:
            return {
                "response": f"Sorry, the app '{app}' is not supported on Android.",
                "device_action": None
            }

    elif cmd.startswith("close "):
        app = cmd.removeprefix("close ").strip()
        if app in SUPPORTED_APPS:
            return {
                "response": f"Closing {app.capitalize()} on your device.",
                "device_action": {
                    "target": "android",
                    "command": f"close {app}"
                }
            }
        else:
            return {
                "response": f"Sorry, I can't close '{app}' on Android.",
                "device_action": None
            }

    else:
        return {
            "response": f"This command is not handled by Android automation module: {cmd}",
            "device_action": None
        }

def TranslateCommand(command_list):
    """
    Accepts a list of commands and processes each for Android automation.
    """
    for command in command_list:
        cmd = command.lower().strip()

        if cmd.startswith("open "):
            app = cmd.removeprefix("open ").strip()
            if app in SUPPORTED_APPS:
                print(f"[ANDROID OPEN] Trying to open app: {app}")
                # Here you would trigger the Android automation (e.g., via intent or network)
            else:
                print(f"[ANDROID OPEN] App '{app}' not supported.")
        elif cmd.startswith("close "):
            app = cmd.removeprefix("close ").strip()
            if app in SUPPORTED_APPS:
                print(f"[ANDROID CLOSE] Trying to close app: {app}")
            else:
                print(f"[ANDROID CLOSE] App '{app}' not supported.")
        else:
            print(f"[ANDROID] Command not handled: {cmd}")
