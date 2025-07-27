# ======================== Model_Simple.py ========================
# Simplified version of enhanced Model.py for testing without external dependencies

import re
import random

# Simplified command patterns for parameter extraction
COMMAND_PATTERNS = {
    "volume": {
        "patterns": [
            r"volume\s+(up|down|mute|unmute)(?:\s+(\d+)%)?",
            r"(?:set\s+)?volume\s+(?:to\s+)?(\d+)%",
            r"(?:increase|decrease)\s+volume\s+(?:by\s+)?(\d+)%",
            r"volume\s+(?:up|down)\s+(\d+)%"
        ],
        "default_values": {"up": 10, "down": 10}
    },
    "brightness": {
        "patterns": [
            r"brightness\s+(?:to\s+)?(\d+)%",
            r"set\s+brightness\s+(?:to\s+)?(\d+)%",
            r"(?:increase|decrease)\s+brightness\s+(?:by\s+)?(\d+)%"
        ]
    },
    "app_commands": {
        "patterns": [
            r"open\s+([a-zA-Z0-9\s]+)",
            r"start\s+([a-zA-Z0-9\s]+)",
            r"close\s+([a-zA-Z0-9\s]+)",
            r"delete\s+([a-zA-Z0-9\s]+)",
            r"lock\s+([a-zA-Z0-9\s]+)",
            r"unlock\s+([a-zA-Z0-9\s]+)"
        ]
    },
    "device_commands": {
        "patterns": [
            r"battery\s+percentage",
            r"turn\s+(on|off)\s+flashlight",
            r"turn\s+(on|off)\s+screen",
            r"back\s+to\s+home",
            r"set\s+reminder",
            r"set\s+alarm",
            r"remove\s+water",
            r"turn\s+(on|off)\s+silent",
            r"turn\s+(on|off)\s+wi-fi",
            r"connect\s+to\s+wi-fi",
            r"disconnect\s+wi-fi",
            r"turn\s+(on|off)\s+bluetooth",
            r"turn\s+(on|off)\s+mobile\s+data",
            r"scroll\s+(up|down|left|right)",
            r"take\s+screenshot",
            r"capture\s+photo",
            r"record\s+video"
        ]
    },
    "pc_commands": {
        "patterns": [
            r"open\s+([a-zA-Z0-9\s]+)\s+in\s+pc",
            r"back\s+to\s+desktop",
            r"shutdown\s+pc",
            r"restart\s+pc",
            r"lock\s+pc",
            r"volume\s+(up|down|mute|unmute)\s+in\s+pc",
            r"minimize\s+all",
            r"maximize\s+window",
            r"close\s+this\s+window",
            r"close\s+this\s+page",
            r"copy",
            r"paste",
            r"move\s+(upward|downward)",
            r"turn\s+on\s+sleeping\s+mode\s+on\s+pc",
            r"capture\s+photo\s+in\s+laptop",
            r"record\s+in\s+laptop",
            r"stop\s+recording",
            r"click\s+on",
            r"type",
            r"send\s+file\s+to\s+pc"
        ]
    }
}

def extract_parameters(command, category):
    """Extract parameters from commands using regex patterns."""
    command_lower = command.lower()
    patterns = COMMAND_PATTERNS.get(category, {}).get("patterns", [])
    
    for pattern in patterns:
        match = re.search(pattern, command_lower)
        if match:
            groups = match.groups()
            if category == "volume":
                if len(groups) == 2 and groups[1]:  # volume up/down with percentage
                    return {"action": groups[0], "value": int(groups[1])}
                elif len(groups) == 1 and groups[0].isdigit():  # set volume to X%
                    return {"action": "set", "value": int(groups[0])}
                elif len(groups) == 1:  # volume up/down without percentage
                    default_values = COMMAND_PATTERNS["volume"]["default_values"]
                    return {"action": groups[0], "value": default_values.get(groups[0], 10)}
            elif category == "brightness":
                return {"action": "set", "value": int(groups[0])}
            elif category == "app_commands":
                return {"app": groups[0].strip()}
            elif category == "device_commands":
                if len(groups) == 1:
                    return {"action": groups[0]}
            elif category == "pc_commands":
                if len(groups) == 1:
                    return {"app": groups[0].strip()}
    
    return {}

def extract_command_parameters(command):
    """Extract parameters from a command string."""
    command_lower = command.lower()
    
    # Check each category for parameter extraction
    for category, config in COMMAND_PATTERNS.items():
        params = extract_parameters(command, category)
        if params:
            return category, params
    
    return None, {}

def analyze_intent_simple(text):
    """Simple intent analysis without external dependencies."""
    text_lower = text.lower()
    
    # Extract numbers
    numbers = re.findall(r'\d+', text_lower)
    
    # Extract actions (simple keyword matching)
    actions = []
    action_keywords = ['open', 'close', 'start', 'stop', 'turn', 'set', 'play', 'call', 'send', 'take', 'capture', 'record']
    for keyword in action_keywords:
        if keyword in text_lower:
            actions.append(keyword)
    
    # Extract objects (simple keyword matching)
    objects = []
    object_keywords = ['volume', 'brightness', 'whatsapp', 'spotify', 'chrome', 'notepad', 'calculator', 'flashlight', 'screenshot', 'photo', 'video']
    for keyword in object_keywords:
        if keyword in text_lower:
            objects.append(keyword)
    
    return {
        "numbers": numbers,
        "actions": actions,
        "objects": objects
    }

def FirstLayerDMM_Simple(prompt: str = "test"):
    """Simplified Decision Making Model with parameter extraction."""
    
    prompt_lower = prompt.lower()
    
    # Simple rule-based decision making
    decisions = []
    
    # Volume commands
    if any(word in prompt_lower for word in ["volume", "vol"]):
        if "down" in prompt_lower or "decrease" in prompt_lower:
            # Extract percentage
            numbers = re.findall(r'\d+', prompt_lower)
            value = int(numbers[0]) if numbers else 10
            decisions.append(f"device volume down {value}% [action:down value:{value}]")
        elif "up" in prompt_lower or "increase" in prompt_lower:
            numbers = re.findall(r'\d+', prompt_lower)
            value = int(numbers[0]) if numbers else 10
            decisions.append(f"device volume up {value}% [action:up value:{value}]")
        elif "set" in prompt_lower or "to" in prompt_lower:
            numbers = re.findall(r'\d+', prompt_lower)
            value = int(numbers[0]) if numbers else 50
            decisions.append(f"device brightness {value}% [action:set value:{value}]")
        else:
            decisions.append("device volume [action:check]")
    
    # Brightness commands
    elif "brightness" in prompt_lower:
        numbers = re.findall(r'\d+', prompt_lower)
        value = int(numbers[0]) if numbers else 50
        decisions.append(f"device brightness {value}% [action:set value:{value}]")
    
    # App commands
    elif any(word in prompt_lower for word in ["open", "start", "kholo", "khol"]):
        apps = ["whatsapp", "spotify", "chrome", "youtube", "gmail", "telegram", "instagram"]
        for app in apps:
            if app in prompt_lower:
                decisions.append(f"open {app}")
                break
        else:
            # Generic app open
            decisions.append("open app")
    
    # Device commands
    elif "screenshot" in prompt_lower or "khicho" in prompt_lower:
        decisions.append("device take screenshot")
    elif "photo" in prompt_lower:
        decisions.append("device capture photo")
    elif "flashlight" in prompt_lower:
        if "on" in prompt_lower:
            decisions.append("device turn on flashlight [action:on]")
        else:
            decisions.append("device turn off flashlight [action:off]")
    elif "battery" in prompt_lower:
        decisions.append("device battery percentage")
    
    # PC commands
    elif "pc" in prompt_lower or "computer" in prompt_lower:
        if "notepad" in prompt_lower:
            decisions.append("pc open notepad")
        elif "calculator" in prompt_lower:
            decisions.append("pc open calculator")
        elif "shutdown" in prompt_lower:
            decisions.append("pc shutdown pc")
        elif "volume" in prompt_lower:
            if "up" in prompt_lower:
                decisions.append("pc volume up in pc")
            elif "down" in prompt_lower:
                decisions.append("pc volume down in pc")
    
    # Media commands
    elif "play" in prompt_lower or "chala" in prompt_lower:
        if "spotify" in prompt_lower:
            decisions.append("play music on spotify")
        elif "youtube" in prompt_lower:
            decisions.append("play music on youtube")
        else:
            decisions.append("play music")
    
    # Communication commands
    elif "call" in prompt_lower:
        decisions.append("mobile call contact")
    elif "sms" in prompt_lower or "message" in prompt_lower:
        decisions.append("mobile send sms")
    
    # Smart commands
    elif any(word in prompt_lower for word in ["weather", "news", "location", "search"]):
        if "weather" in prompt_lower:
            decisions.append("smart weather report")
        elif "news" in prompt_lower:
            decisions.append("smart today news")
        elif "location" in prompt_lower:
            decisions.append("smart current location")
        elif "search" in prompt_lower:
            decisions.append("smart search query")
    
    # General queries
    elif any(word in prompt_lower for word in ["how", "what", "when", "where", "why", "who"]):
        decisions.append(f"general {prompt}")
    
    # Realtime queries
    elif any(word in prompt_lower for word in ["today", "current", "latest", "now"]):
        decisions.append(f"realtime {prompt}")
    
    # Default to general if no specific intent found
    if not decisions:
        decisions.append(f"general {prompt}")
    
    return decisions

if __name__ == "__main__":
    print("🧪 Testing Simplified Enhanced Model")
    print("=" * 50)
    
    test_queries = [
        "volume down 20%",
        "set brightness to 50%",
        "open whatsapp",
        "take screenshot",
        "turn on flashlight",
        "open notepad in pc",
        "play music on spotify",
        "what's the weather today?",
        "volume kam karo 25%",
        "whatsapp kholo"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        decisions = FirstLayerDMM_Simple(query)
        print(f"📋 Decisions: {decisions}")
        
        # Extract parameters
        for decision in decisions:
            if "[" in decision and "]" in decision:
                category, params = extract_command_parameters(decision)
                if params:
                    print(f"⚙️  Parameters: {params}")
        
        print("-" * 40) 