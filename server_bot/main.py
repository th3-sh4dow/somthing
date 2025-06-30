from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Chatbot import ChatBot
from dotenv import dotenv_values
from asyncio import run 
import subprocess
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def MainExecution(query):
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    print(f"[Query] {query}")
    Decision = FirstLayerDMM(query)
    print(f"[Decision Layer] → {Decision}")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Merged_query = " and ".join([
        "".join(i.split(":")[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
    ])

    for q in Decision:
        if "generate" in q:
            ImageGenerationQuery = q
            ImageExecution = True

    for q in Decision:
        if not TaskExecution and any(q.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    if ImageExecution:
        try:
            with open(r"Frontend/Files/ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")
            p1 = subprocess.Popen(['python', r'Backend/ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"[ERROR] Starting image generation: {e}")

    if G or R:
        QueryMod = Merged_query
        Answer = RealtimeSearchEngine(QueryMod)
        print(f"[Answer] {Answer}")
        return Answer
    else:
        for q in Decision:
            if "general" in q:
                QueryFinal = q.replace("general", "")
                Answer = ChatBot(QueryFinal)
                print(f"[General Answer] {Answer}")
                return Answer
            elif "realtime" in q:
                QueryFinal = q.replace("realtime", "")
                Answer = RealtimeSearchEngine(QueryFinal)
                print(f"[Realtime Answer] {Answer}")
                return Answer
            elif "exit" in q:
                print("[Exiting]")
                os._exit(1)
