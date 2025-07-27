import cohere
from rich import print
from dotenv import dotenv_values
import random
import re
import spacy
from fuzzywuzzy import process

# Load environment variables
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")

co = cohere.Client(api_key=CohereAPIKey)

# Load NLP model for better understanding
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("[WARNING] spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# Enhanced action keywords with parameters
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "mobile", "code", "device"
]

# Command patterns for parameter extraction
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
    "media_commands": {
        "patterns": [
            r"play\s+([a-zA-Z0-9\s]+)(?:\s+on\s+([a-zA-Z0-9\s]+))?",
            r"capture\s+photo",
            r"take\s+screenshot",
            r"record\s+video",
            r"change\s+camera",
            r"skip\s+(\d+)\s+sec",
            r"change\s+song",
            r"stop\s+recording"
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
            r"scroll\s+(up|down|left|right)"
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

# Chat history with enhanced examples
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "Jarvis, palpal gaana chala sakte ho"},
    {"role": "Chatbot", "message": "play palpal"},
    {"role": "User", "message": "Jarvis, kya tum WhatsApp khol sakte ho"},
    {"role": "Chatbot", "message": "open whatsapp"},
    {"role": "User", "message": "play palpal on spsficsfic"},
    {"role": "Chatbot", "message": "play palpal on spotify"},
    {"role": "User", "message": "write a program to print factorial of a number"},
    {"role": "Chatbot", "message": "code factorial program"},
    {"role": "User", "message": "ek program likho jo factorial nikale"},
    {"role": "Chatbot", "message": "code factorial program"},
    {"role": "User", "message": "volume down 20%"},
    {"role": "Chatbot", "message": "device volume down 20%"},
    {"role": "User", "message": "set brightness to 50%"},
    {"role": "Chatbot", "message": "device brightness 50%"},
    {"role": "User", "message": "open notepad in pc"},
    {"role": "Chatbot", "message": "pc open notepad"},
    {"role": "User", "message": "take a screenshot"},
    {"role": "Chatbot", "message": "device take screenshot"},
    {"role": "User", "message": "call mom"},
    {"role": "Chatbot", "message": "mobile call mom"},
    {"role": "User", "message": "what's the weather today?"},
    {"role": "Chatbot", "message": "realtime weather today"},
    {"role": "User", "message": "tell me a joke"},
    {"role": "Chatbot", "message": "general tell me a joke"},
]

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
            elif category == "media_commands":
                if len(groups) == 2 and groups[1]:
                    return {"content": groups[0].strip(), "platform": groups[1].strip()}
                elif len(groups) == 1:
                    return {"content": groups[0].strip()}
            elif category == "device_commands":
                if len(groups) == 1:
                    return {"action": groups[0]}
            elif category == "pc_commands":
                if len(groups) == 1:
                    return {"app": groups[0].strip()}
    
    return {}

def analyze_intent_with_nlp(text):
    """Use spaCy for advanced NLP analysis."""
    if not nlp:
        return {}
    
    doc = nlp(text.lower())
    
    # Extract entities and key information
    entities = {ent.label_: ent.text for ent in doc.ents}
    
    # Extract numbers
    numbers = [token.text for token in doc if token.like_num]
    
    # Extract actions (verbs)
    actions = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    
    # Extract objects (nouns)
    objects = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
    
    return {
        "entities": entities,
        "numbers": numbers,
        "actions": actions,
        "objects": objects
    }

# Enhanced preamble with parameter support
preamble = """
You are a very accurate Decision-Making Model with advanced NLP capabilities, which decides what kind of a query is given to you and extracts specific parameters.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation.

*** Do not answer any query, just decide what kind of query is given to you and extract parameters. ***

COMMAND CATEGORIES AND PARAMETERS:

1. CORE Commands:
-> Respond with 'general (query)' for conversational queries
-> Respond with 'realtime (query)' for queries needing up-to-date information
-> Respond with 'exit' for goodbye queries

2. APP Commands:
-> Respond with 'open (app name)' for opening apps
-> Respond with 'close (app name)' for closing apps
-> Respond with 'start (app name)' for starting apps
-> Respond with 'delete (app name)' for uninstalling apps
-> Respond with 'lock (app name)' for locking apps
-> Respond with 'unlock (app name)' for unlocking apps

3. MEDIA Commands:
-> Respond with 'play (content) on (platform)' for media playback
-> Respond with 'capture photo' for taking photos
-> Respond with 'take screenshot' for screenshots
-> Respond with 'record video' for video recording
-> Respond with 'change camera' for switching cameras
-> Respond with 'skip (X) sec' for media skipping
-> Respond with 'change song' for next song
-> Respond with 'stop recording' for stopping recording

4. DEVICE Commands (with parameters):
-> Respond with 'device volume (action) (value)%' for volume control
-> Respond with 'device brightness (value)%' for brightness control
-> Respond with 'device battery percentage' for battery info
-> Respond with 'device turn (on/off) flashlight' for flashlight
-> Respond with 'device turn (on/off) screen' for screen control
-> Respond with 'device back to home' for home screen
-> Respond with 'device set reminder' for reminders
-> Respond with 'device set alarm' for alarms
-> Respond with 'device remove water' for water ejection
-> Respond with 'device turn (on/off) silent' for silent mode
-> Respond with 'device turn (on/off) wi-fi' for WiFi control
-> Respond with 'device connect to wi-fi' for WiFi connection
-> Respond with 'device turn (on/off) bluetooth' for Bluetooth
-> Respond with 'device turn (on/off) mobile data' for mobile data
-> Respond with 'device scroll (direction)' for scrolling

5. PC Commands:
-> Respond with 'pc open (app) in pc' for PC apps
-> Respond with 'pc back to desktop' for desktop
-> Respond with 'pc shutdown pc' for shutdown
-> Respond with 'pc restart pc' for restart
-> Respond with 'pc lock pc' for locking PC
-> Respond with 'pc volume (action) in pc' for PC volume
-> Respond with 'pc minimize all' for minimizing windows
-> Respond with 'pc maximize window' for maximizing
-> Respond with 'pc close this window' for closing windows
-> Respond with 'pc copy' for copying
-> Respond with 'pc paste' for pasting
-> Respond with 'pc move (direction)' for scrolling
-> Respond with 'pc turn on sleeping mode on pc' for sleep mode
-> Respond with 'pc capture photo in laptop' for laptop camera
-> Respond with 'pc record in laptop' for laptop recording
-> Respond with 'pc click on' for clicking
-> Respond with 'pc type' for typing
-> Respond with 'pc send file to pc' for file transfer

6. SMART Commands:
-> Respond with 'smart today news' for news
-> Respond with 'smart weather report' for weather
-> Respond with 'smart current location' for GPS location
-> Respond with 'smart show me location of (person)' for tracking
-> Respond with 'smart translate mode' for translation
-> Respond with 'smart trouble' for emergency
-> Respond with 'smart search (query)' for web search
-> Respond with 'smart what is this' for object detection
-> Respond with 'smart scan and explain' for text reading
-> Respond with 'smart new notification' for notifications
-> Respond with 'smart unknown (query)' for AI queries
-> Respond with 'smart tell me about (topic)' for Wikipedia

7. OTHER Commands:
-> Respond with 'generate image (prompt)' for image generation
-> Respond with 'reminder (datetime with message)' for reminders
-> Respond with 'content (topic)' for content creation
-> Respond with 'google search (topic)' for Google searches
-> Respond with 'youtube search (topic)' for YouTube searches
-> Respond with 'code (program description)' for code generation
-> Respond with 'mobile (query)' for mobile tasks

PARAMETER EXTRACTION EXAMPLES:
- "volume down 20%" → "device volume down 20%"
- "set brightness to 50%" → "device brightness 50%"
- "open notepad in pc" → "pc open notepad"
- "play despacito on spotify" → "play despacito on spotify"
- "call mom" → "mobile call mom"
- "take a screenshot" → "device take screenshot"

For multiple tasks, combine them with commas.
For Hindi queries, extract the main intent and entity.
Respond with 'general (query)' if the query is unclear or not covered above.
"""

# Ownership preamble (unchanged)
ownership_preamble = """
You are a professional AI assistant designed to explain your own origin in a respectful and intelligent way. 
If someone asks questions like \"who made you\", \"who built you\", \"who developed you\", or similar, 
you should respond by naturally describing your creator.

Here's how you should describe yourself:

\"I was proudly built by Bicky Muduli, also known as Shadow. He is a highly skilled software developer, 
ethical hacker, and cybersecurity expert. He specializes in penetration testing, secure development, 
OSINT, and automation systems. With a deep passion for technology and self-learning, Bicky created me 
as part of his mission to integrate artificial intelligence with practical real-world use cases. 
He believes in innovation, open learning, and empowering the cybersecurity community.\"

If the question is asked in an informal or funny way (like \"who's your daddy?\"), respond cleverly 
but still honor Bicky Muduli.
"""

ownership_triggers = [
    "who built you", "who made you", "who developed you", "who is your developer", "who created you",
    "who is your creator", "who programmed you", "who is your founder", "who owns you", "your maker",
    "who is the person behind you", "who is your builder", "developer of you", "coded you", "your owner",
    "your father", "who is your father", "who is your daddy", "your papa", "papa", "daddy"
]

def is_ownership_query(prompt: str):
    prompt_lower = prompt.lower()
    return any(trigger in prompt_lower for trigger in ownership_triggers)

def extract_command_parameters(command):
    """Extract parameters from a command string."""
    command_lower = command.lower()
    
    # Check each category for parameter extraction
    for category, config in COMMAND_PATTERNS.items():
        params = extract_parameters(command, category)
        if params:
            return category, params
    
    return None, {}

def FirstLayerDMM(prompt: str = "test"):
    """Enhanced Decision Making Model with parameter extraction."""
    
    if is_ownership_query(prompt):
        stream = co.chat_stream(
            model='command-r-plus',
            message=prompt,
            temperature=0.7,
            chat_history=[],
            prompt_truncation='OFF',
            connectors=[],
            preamble=ownership_preamble
        )
        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text
        return [f"general {response.strip()}"]

    # Use NLP analysis for better understanding
    nlp_analysis = analyze_intent_with_nlp(prompt)
    
    messages = [{"role": "user", "content": f"{prompt}"}]
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    response = response.replace("\n", "").split(",")
    response = [i.strip() for i in response if any(i.strip().lower().startswith(func) for func in funcs)]

    # Enhanced parameter extraction for each command
    enhanced_commands = []
    for cmd in response:
        if cmd.startswith("device ") or cmd.startswith("pc ") or cmd.startswith("mobile "):
            # Extract parameters for device commands
            category, params = extract_command_parameters(cmd)
            if params:
                # Add parameters to command
                param_str = " ".join([f"{k}:{v}" for k, v in params.items()])
                enhanced_commands.append(f"{cmd} [{param_str}]")
            else:
                enhanced_commands.append(cmd)
        else:
            enhanced_commands.append(cmd)

    if not enhanced_commands or any("(query)" in r for r in enhanced_commands):
        return ["general " + prompt]
    
    return enhanced_commands

if __name__ == "__main__":
    while True:
        user_input = input("Enter your query: ")
        # user_input = "play letest video of not Veeru"
        result = FirstLayerDMM(prompt=user_input)
        print(f"Decision: {result}")
        
        # Show parameter extraction
        for cmd in result:
            if cmd.startswith(("device ", "pc ", "mobile ")):
                category, params = extract_command_parameters(cmd)
                if params:
                    print(f"Parameters for '{cmd}': {params}")