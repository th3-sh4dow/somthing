# ======================== Android_Automation.py ========================

SUPPORTED_APPS = {
    "whatsapp": "com.whatsapp",
    "chrome": "com.android.chrome",
    "youtube": "com.google.android.youtube",
    "gmail": "com.google.android.gm",
    "settings": "com.android.settings",
    "camera": "com.android.camera",
    "spotify": "com.spotify.music",
    "telegram": "org.telegram.messenger",
    "instagram": "com.instagram.android",
    "facebook": "com.facebook.katana",
    "twitter": "com.twitter.android",
    "maps": "com.google.android.apps.maps",
    "play store": "com.android.vending",
    "gallery": "com.android.gallery3d",
    "calculator": "com.android.calculator2",
    "clock": "com.android.deskclock",
    "contacts": "com.android.contacts",
    "phone": "com.android.dialer",
    "messages": "com.android.mms",
    "file manager": "com.android.documentsui"
}

def TranslateAndroidCommand(commands):
    """Enhanced Android command translator with parameter support."""
    if isinstance(commands, str):
        commands = [commands]

    results = []
    
    for command in commands:
        cmd = command.lower().strip()
        result = {"command": cmd, "action": "unknown", "response": "", "parameters": {}}
        
        # Extract parameters if present
        params = {}
        if "[" in cmd and "]" in cmd:
            import re
            param_match = re.search(r"\[(.*?)\]", cmd)
            if param_match:
                param_str = param_match.group(1)
                for param in param_str.split():
                    if ":" in param:
                        key, value = param.split(":", 1)
                        try:
                            if value.isdigit():
                                params[key] = int(value)
                            elif value.lower() in ["true", "false"]:
                                params[key] = value.lower() == "true"
                            else:
                                params[key] = value
                        except:
                            params[key] = value
                # Remove parameter section from command
                cmd = re.sub(r"\s*\[.*?\]", "", cmd)
        
        result["parameters"] = params

        if cmd.startswith("open "):
            app = cmd.removeprefix("open ").strip()
            if app in SUPPORTED_APPS:
                result["action"] = "open_app"
                result["response"] = f"Opening {app.capitalize()} on your Android device."
                print(f"[ANDROID OPEN] Opening app: {app} ({SUPPORTED_APPS[app]})")
            else:
                result["action"] = "open_app_unknown"
                result["response"] = f"App '{app}' not in supported list. Trying to open anyway."
                print(f"[ANDROID OPEN] App '{app}' not supported, attempting to open.")

        elif cmd.startswith("close "):
            app = cmd.removeprefix("close ").strip()
            result["action"] = "close_app"
            result["response"] = f"Closing {app.capitalize()} on your Android device."
            print(f"[ANDROID CLOSE] Closing app: {app}")

        elif cmd.startswith("start "):
            app = cmd.removeprefix("start ").strip()
            result["action"] = "start_app"
            result["response"] = f"Starting {app.capitalize()} on your Android device."
            print(f"[ANDROID START] Starting app: {app}")

        elif cmd.startswith("delete "):
            app = cmd.removeprefix("delete ").strip()
            result["action"] = "delete_app"
            result["response"] = f"Uninstalling {app.capitalize()} from your Android device."
            print(f"[ANDROID DELETE] Uninstalling app: {app}")

        elif cmd.startswith("lock "):
            app = cmd.removeprefix("lock ").strip()
            result["action"] = "lock_app"
            result["response"] = f"Locking {app.capitalize()} on your Android device."
            print(f"[ANDROID LOCK] Locking app: {app}")

        elif cmd.startswith("unlock "):
            app = cmd.removeprefix("unlock ").strip()
            result["action"] = "unlock_app"
            result["response"] = f"Unlocking {app.capitalize()} on your Android device."
            print(f"[ANDROID UNLOCK] Unlocking app: {app}")

        elif cmd.startswith("play "):
            query = cmd.removeprefix("play ").strip()
            result["action"] = "play_media"
            result["response"] = f"Playing: {query} on your Android device."
            print(f"[ANDROID PLAY] Playing: {query}")

        elif cmd.startswith("device "):
            device_cmd = cmd.removeprefix("device ").strip()
            result.update(handle_device_command(device_cmd, params))

        elif cmd.startswith("mobile "):
            mobile_cmd = cmd.removeprefix("mobile ").strip()
            result.update(handle_mobile_command(mobile_cmd, params))

        elif cmd.startswith("smart "):
            smart_cmd = cmd.removeprefix("smart ").strip()
            result.update(handle_smart_command(smart_cmd, params))

        else:
            result["action"] = "unknown"
            result["response"] = f"Command not handled: {cmd}"
            print(f"[ANDROID] Command not handled: {cmd}")

        results.append(result)

    return results

def handle_device_command(cmd, params):
    """Handle device-specific commands with parameters."""
    result = {"action": "device_command", "response": ""}
    
    if "volume" in cmd:
        action = params.get("action", "up")
        value = params.get("value", 10)
        
        if action == "up":
            result["response"] = f"Volume increased by {value}% on Android device."
            print(f"[ANDROID VOLUME] Up by {value}%")
        elif action == "down":
            result["response"] = f"Volume decreased by {value}% on Android device."
            print(f"[ANDROID VOLUME] Down by {value}%")
        elif action == "set":
            result["response"] = f"Volume set to {value}% on Android device."
            print(f"[ANDROID VOLUME] Set to {value}%")
        elif action in ["mute", "unmute"]:
            result["response"] = f"Volume {action}d on Android device."
            print(f"[ANDROID VOLUME] {action.capitalize()}")
    
    elif "brightness" in cmd:
        value = params.get("value", 50)
        result["response"] = f"Brightness set to {value}% on Android device."
        print(f"[ANDROID BRIGHTNESS] Set to {value}%")
    
    elif "battery" in cmd:
        result["response"] = "Checking battery percentage on Android device."
        print(f"[ANDROID BATTERY] Checking battery level")
    
    elif "flashlight" in cmd:
        action = params.get("action", "on")
        result["response"] = f"Flashlight turned {action} on Android device."
        print(f"[ANDROID FLASHLIGHT] Turned {action}")
    
    elif "screen" in cmd:
        action = params.get("action", "on")
        result["response"] = f"Screen turned {action} on Android device."
        print(f"[ANDROID SCREEN] Turned {action}")
    
    elif "home" in cmd:
        result["response"] = "Returning to home screen on Android device."
        print(f"[ANDROID HOME] Going to home screen")
    
    elif "reminder" in cmd or "alarm" in cmd:
        result["response"] = "Setting reminder/alarm on Android device."
        print(f"[ANDROID REMINDER] Setting reminder/alarm")
    
    elif "water" in cmd:
        result["response"] = "Activating water ejection on Android device."
        print(f"[ANDROID WATER] Activating water ejection")
    
    elif "silent" in cmd:
        action = params.get("action", "on")
        result["response"] = f"Silent mode turned {action} on Android device."
        print(f"[ANDROID SILENT] Turned {action}")
    
    elif "wi-fi" in cmd:
        action = params.get("action", "on")
        result["response"] = f"Wi-Fi turned {action} on Android device."
        print(f"[ANDROID WIFI] Turned {action}")
    
    elif "bluetooth" in cmd:
        action = params.get("action", "on")
        result["response"] = f"Bluetooth turned {action} on Android device."
        print(f"[ANDROID BLUETOOTH] Turned {action}")
    
    elif "mobile data" in cmd:
        action = params.get("action", "on")
        result["response"] = f"Mobile data turned {action} on Android device."
        print(f"[ANDROID MOBILE DATA] Turned {action}")
    
    elif "scroll" in cmd:
        direction = params.get("action", "up")
        result["response"] = f"Scrolling {direction} on Android device."
        print(f"[ANDROID SCROLL] {direction}")
    
    elif "screenshot" in cmd:
        result["response"] = "Taking screenshot on Android device."
        print(f"[ANDROID SCREENSHOT] Taking screenshot")
    
    elif "photo" in cmd:
        result["response"] = "Capturing photo on Android device."
        print(f"[ANDROID PHOTO] Capturing photo")
    
    elif "video" in cmd:
        result["response"] = "Recording video on Android device."
        print(f"[ANDROID VIDEO] Recording video")
    
    else:
        result["response"] = f"Device command '{cmd}' executed on Android device."
        print(f"[ANDROID DEVICE] {cmd}")
    
    return result

def handle_mobile_command(cmd, params):
    """Handle mobile-specific commands."""
    result = {"action": "mobile_command", "response": ""}
    
    if cmd.startswith("call "):
        contact = cmd.replace("call ", "").strip()
        result["response"] = f"Calling {contact} on Android device."
        print(f"[ANDROID CALL] Calling {contact}")
    
    elif cmd.startswith("send sms "):
        result["response"] = "Sending SMS on Android device."
        print(f"[ANDROID SMS] Sending SMS")
    
    elif "vibrate" in cmd:
        duration = params.get("duration", 300)
        result["response"] = f"Phone vibrating for {duration}ms."
        print(f"[ANDROID VIBRATE] {duration}ms")
    
    else:
        result["response"] = f"Mobile command '{cmd}' executed on Android device."
        print(f"[ANDROID MOBILE] {cmd}")
    
    return result

def handle_smart_command(cmd, params):
    """Handle smart/AI commands."""
    result = {"action": "smart_command", "response": ""}
    
    if "news" in cmd:
        result["response"] = "Fetching today's news on Android device."
        print(f"[ANDROID SMART] Fetching news")
    
    elif "weather" in cmd:
        result["response"] = "Getting weather report on Android device."
        print(f"[ANDROID SMART] Getting weather")
    
    elif "location" in cmd:
        result["response"] = "Getting current location on Android device."
        print(f"[ANDROID SMART] Getting location")
    
    elif "translate" in cmd:
        result["response"] = "Activating translation mode on Android device."
        print(f"[ANDROID SMART] Translation mode")
    
    elif "trouble" in cmd:
        result["response"] = "Emergency mode activated on Android device."
        print(f"[ANDROID SMART] Emergency mode")
    
    elif "search" in cmd:
        result["response"] = "Performing web search on Android device."
        print(f"[ANDROID SMART] Web search")
    
    elif "notification" in cmd:
        result["response"] = "Reading latest notification on Android device."
        print(f"[ANDROID SMART] Reading notification")
    
    else:
        result["response"] = f"Smart command '{cmd}' processed on Android device."
        print(f"[ANDROID SMART] {cmd}")
    
    return result

def human_friendly_responses(device_tasks: dict) -> str:
    """Generate human-friendly responses for device tasks."""
    responses = []
    
    if "android" in device_tasks:
        android_cmds = []
        for cmd in device_tasks['android']:
            if isinstance(cmd, dict):
                android_cmds.append(cmd.get('response', cmd.get('command', 'Unknown command')))
            else:
                android_cmds.append(cmd)
        
        if android_cmds:
            responses.append(f"On your Android device: {', '.join(android_cmds)}.")

    if "pc" in device_tasks:
        pc_cmds = []
        for cmd in device_tasks['pc']:
            if isinstance(cmd, dict):
                pc_cmds.append(cmd.get('response', cmd.get('command', 'Unknown command')))
            else:
                pc_cmds.append(cmd)
        
        if pc_cmds:
            responses.append(f"On your computer: {', '.join(pc_cmds)}.")

    if not responses:
        responses.append("No valid tasks were found for your devices.")

    return " ".join(responses)

def get_supported_apps():
    """Get list of supported apps."""
    return list(SUPPORTED_APPS.keys())

def is_app_supported(app_name: str) -> bool:
    """Check if an app is supported."""
    return app_name.lower() in SUPPORTED_APPS

def get_app_package(app_name: str) -> str:
    """Get package name for a supported app."""
    return SUPPORTED_APPS.get(app_name.lower(), "")
