# ========== IMPORTS ==========
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# ========== ENV & INIT ==========
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
useragent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')
client = Groq(api_key=GroqAPIKey)

SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like Letter."
}]
messages = []

# ========== EXECUTORS ==========

def GoogleSearch(topic):
    search(topic)
    return True

def OpenNotepad(file_path):
    subprocess.Popen(['notepad.exe', file_path])

def ContentWriterAI(prompt):
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=SystemChatBot + messages,
        max_tokens=2848,
        temperature=0.7,
        top_p=1,
        stream=True
    )
    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content
    messages.append({"role": "assistant", "content": answer})
    return answer.strip().replace("</s>", "")

def Content(topic):
    prompt = topic.replace("content ", "")
    ai_content = ContentWriterAI(prompt)
    file_path = rf"Data\{prompt.lower().replace(' ', '')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ai_content)
    OpenNotepad(file_path)
    return True

def YoutubeSearch(topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app, sess):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

def CloseApp(app):
    try:
        if "chrome" not in app.lower():
            close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
    if command in actions:
        actions[command]()
        return True
    return False

# ========== COMMAND TRANSLATOR ==========

def TranslateCommand(command: str) -> dict:
    """
    Translates input into a structured response dict:
    {
        'response': str,            # TTS response
        'device_action': {
            'target': 'pc' or 'android',
            'command': 'open whatsapp'
        }
    }
    """
    cmd = command.lower().strip()
    sess = requests.Session()

    if cmd.startswith("open "):
        app = cmd.removeprefix("open ").strip()
        if app in ["whatsapp", "youtube", "gmail", "chrome"]:
            return {
                "response": f"Opening {app.capitalize()}",
                "device_action": {
                    "target": "android",
                    "command": f"open {app}"
                }
            }
        else:
            OpenApp(app, sess)
            return {
                "response": f"Opening {app.capitalize()} on PC",
                "device_action": {
                    "target": "pc",
                    "command": f"open {app}"
                }
            }

    elif cmd.startswith("close "):
        CloseApp(cmd.removeprefix("close ").strip())
        return {
            "response": "Closing the app on PC.",
            "device_action": {
                "target": "pc",
                "command": cmd
            }
        }

    elif cmd.startswith("play "):
        PlayYoutube(cmd.removeprefix("play ").strip())
        return {
            "response": "Playing on YouTube.",
            "device_action": {
                "target": "pc",
                "command": cmd
            }
        }

    elif cmd.startswith("google search "):
        GoogleSearch(cmd.removeprefix("google search ").strip())
        return {
            "response": "Searching Google...",
            "device_action": {
                "target": "pc",
                "command": cmd
            }
        }

    elif cmd.startswith("youtube search "):
        YoutubeSearch(cmd.removeprefix("youtube search ").strip())
        return {
            "response": "Searching on YouTube...",
            "device_action": {
                "target": "pc",
                "command": cmd
            }
        }

    elif cmd.startswith("system "):
        System(cmd.removeprefix("system ").strip())
        return {
            "response": "System command executed.",
            "device_action": {
                "target": "pc",
                "command": cmd
            }
        }

    elif cmd.startswith("content "):
        Content(cmd)
        return {
            "response": "Generated content and saved to file.",
            "device_action": {
                "target": "pc",
                "command": cmd
            }
        }

    else:
        return {
            "response": f"Sorry, I don't recognize this command: {cmd}",
            "device_action": None
        }
