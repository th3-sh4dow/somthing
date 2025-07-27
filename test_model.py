# ================== Advanced Central AI Server Processing Engine ==================
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Chatbot import ChatBot
from Backend.PC_Automation import TranslateCommand as PCTranslateCommand
from Backend.Andriod_Automation import TranslateAndroidCommand, human_friendly_responses
from dotenv import dotenv_values
import spacy
from fuzzywuzzy import process
import re
from googletrans import Translator
import asyncio
import aiohttp
from groq import Groq
from googleapiclient.discovery import build

# Load Environment Variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
YouTubeAPIKey = env_vars.get("YouTubeAPIKey")

# Initialize Groq for code generation
groq_client = Groq(api_key=GroqAPIKey)

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YouTubeAPIKey) if YouTubeAPIKey else None

# Load NLP models
nlp_en = spacy.load("en_core_web_sm")
nlp_multi = spacy.load("xx_ent_wiki_sm")
translator = Translator()

# Supported Automation Tasks
AutomationTypes = ["open", "close", "play", "system", "content", "google search", "youtube search", "code"]

# Music app aliases
MUSIC_APPS = {
    "youtube": ["youtube", "yutube", "youtub", "yt"],
    "spotify": ["spotify", "spotfy", "spsficsfic", "spoti", "spotfiy"]
}

# ----------------------- Utility Functions ------------------------ #

async def translate_to_english(query):
    try:
        detected = await asyncio.to_thread(translator.detect, query)
        if detected.lang != "en":
            translated = await asyncio.to_thread(translator.translate, query, dest="en")
            return translated.text
        return query
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        return query


def clean_query(query, music_app=None):
    """Clean query by removing fillers and app names."""
    query = query.lower()
    fillers = ["a", "the", "song", "gaana", "play", "chala", "khol", "sakti", "sakti hai", "sakti ho", "karo", "likho", "program"]
    for filler in fillers:
        query = re.sub(rf"\b{filler}\b", "", query)
    if music_app:
        for alias in MUSIC_APPS.get(music_app, []):
            query = query.replace(alias, "")
    query = re.sub(r"[^a-zA-Z0-9 ]", "", query)
    return query.strip()

def detect_music_app(query):
    """Detect music app with fuzzy matching."""
    query_lower = query.lower()
    for app, aliases in MUSIC_APPS.items():
        for alias in aliases:
            if alias in query_lower:
                return app
    return "youtube"  # Default to YouTube

async def generate_code(description):
    """Generate code using Grok."""
    prompt = f"Write a Python program to {description}. Provide only the code in a code block:\n```python\n```"
    completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=False
    )
    code = completion.choices[0].message.content.strip()
    # Extract code block
    code_match = re.search(r"```python\n([\s\S]*?)\n```", code)
    return code_match.group(1) if code_match else code


async def get_youtube_video_id(query):
    """Get the first YouTube video ID for a query."""
    if not youtube:
        print("[ERROR] YouTube API key missing")
        return None, query
    try:
        request = youtube.search().list(
            part="id,snippet",
            q=query,
            type="video",
            maxResults=1
        )
        response = await asyncio.to_thread(request.execute)
        if response.get("items"):
            video_id = response["items"][0]["id"]["videoId"]
            video_title = response["items"][0]["snippet"]["title"]
            print(f"[INFO] Found YouTube video: {video_title} (ID: {video_id})")
            return video_id, video_title
        print(f"[WARNING] No YouTube videos found for query: {query}")
        return None, query
    except Exception as e:
        print(f"[ERROR] YouTube API failed: {e}")
        return None, query

# ------------------- Main Core Decision + Dispatcher ------------------- #

async def MainExecution(Query, device_id=None):
    print(f"[INFO] Incoming Query → {Query} from {device_id}")

    # Translate Hindi to English
    query_translated = await translate_to_english(Query)
    print(f"[DEBUG] Translated Query → {query_translated}")

    # Get intent from FirstLayerDMM
    decisions = FirstLayerDMM(query_translated)
    print(f"[DEBUG] Decision Tree → {decisions}")

    device_tasks = {"android": [], "pc": []}
    final_answers = []

    music_app = detect_music_app(query_translated)

    for decision in decisions:
        decision_lower = decision.lower().strip()

        if decision_lower.startswith("general"):
            answer = ChatBot(await translate_to_english(decision.replace("general", "").strip()))
            final_answers.append(f"[General] {answer}")

        elif decision_lower.startswith("realtime"):
            answer = RealtimeSearchEngine(await translate_to_english(decision.replace("realtime", "").strip()))
            final_answers.append(f"[Realtime] {answer}")

        elif decision_lower.startswith("play"):
            song_name = clean_query(decision.replace("play", "").strip(), music_app)
            if song_name:
                if music_app == "youtube":
                    video_id, video_title = await get_youtube_video_id(song_name)
                    cmd = f"play::video_id::{video_id}" if video_id else f"play::{song_name}"
                    tts_response = f"Playing {video_title} on YouTube." if video_id else f"Searching {song_name} on YouTube."
                else:
                    cmd = f"play::{song_name} on spotify"
                    tts_response = f"Playing {song_name} on Spotify."
                if device_id:
                    device_tasks["android"].append(cmd)
                    final_answers.append(tts_response)
                else:
                    device_tasks["pc"].append(cmd)
                    final_answers.append(f"Playing {song_name} on your computer.")

        elif decision_lower.startswith("open"):
            app_name = clean_query(decision.replace("open", "").strip())
            if app_name:
                device_tasks["android"].append(f"open::{app_name}")
                final_answers.append(f"Opening {app_name.capitalize()} on your phone.")

        elif decision_lower.startswith("code"):
            code_desc = clean_query(decision.replace("code", "").strip())
            if code_desc:
                code = await generate_code(code_desc)
                device_tasks["android"].append(f"code::{code_desc}::{code}")
                final_answers.append(f"Generated code for {code_desc} and sent to your device.")

        elif any(decision_lower.startswith(t) for t in AutomationTypes):
            device_tasks["android"].append(decision)

    # Execution Phase (async)
    if device_tasks["android"] and device_id:
        TranslateAndroidCommand(device_tasks["android"])

    if device_tasks["pc"]:
        PCTranslateCommand(device_tasks["pc"])

    # Human-like reply
    final_output = "\n".join(final_answers) or human_friendly_responses(device_tasks) or "Done."

    # Generate device_action
# Generate device_action
    # Generate device_action
    flatten_android_commands = []
    for cmd in device_tasks["android"]:
        if cmd.lower().strip().startswith("play::") or cmd.lower().strip().startswith("open::"):
            flatten_android_commands.append(cmd.strip())  # ✅ as-is, no lowercase
        else:
            cmd_lower = cmd.lower().strip()
            for prefix in ["close ", "google search ", "youtube search ", "content ", "code "]:
                if cmd_lower.startswith(prefix):
                    keyword = prefix.strip().replace(" ", "_") if " " in prefix.strip() else prefix.strip()
                    data = cmd_lower.removeprefix(prefix).strip()
                    flatten_android_commands.append(f"{keyword}::{data}")
                    break
                
    # ✅ Yeh loop khatam hone ke baad hi return karo
    return final_output, {
        "tts_text": final_output,
        "device_command": ";".join(flatten_android_commands) if flatten_android_commands else ""
    }

# ------------------ END MODULE ------------------ #

if __name__ == "__main__":
    import asyncio
    while True:
        user_query = input(f"{Username} → ").strip()
        if user_query.lower() == "exit":
            print("[Exiting]")
            break
        response, device_action = asyncio.run(MainExecution(user_query))
        print(f"{Assistantname} → {response}")