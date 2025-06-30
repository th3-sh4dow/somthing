from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Chatbot import ChatBot
from dotenv import dotenv_values
from asyncio import run 
import subprocess
import json
import os
import cohere
from Backend.PC_Automation import TranslateCommand
from Backend.Andriod_Automation import TranslateAndroidCommand as AndroidTranslateCommand

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
            

    return new_query.capitalize()


def MainExecution(Query, device_id=None):
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join([
        "".join(i.split(":")[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
    ])

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    # Only pass automation tasks to correct handler
    AutomationTasks = [q for q in Decision if any(q.startswith(func) for func in Functions)]
    device_action = None
    if AutomationTasks:
        # Example: If the command is for Android, don't execute on server, just return action
        for task in AutomationTasks:
            if "whatsapp" in task.lower():
                device_action = {
                    "target": "android",
                    "command": task
                }
                break
        # If not android, execute on the correct platform
        if not device_action:
            if device_id:
                print("[DEBUG] Running AndroidTranslateCommand()")
                AndroidTranslateCommand(AutomationTasks)
            else:
                print("[DEBUG] Running PC TranslateCommand()")
                TranslateCommand(AutomationTasks)

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    # Process all decisions and collect answers
    answers = []
    for Queries in Decision:
        if "general" in Queries:
            QueryFinal = Queries.replace("general", "").strip()
            Answer = ChatBot(QueryModifier(QueryFinal))
            answers.append(f"[General Answer] {Answer}")

        elif "realtime" in Queries:
            QueryFinal = Queries.replace("realtime", "").strip()
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            answers.append(f"[Realtime Answer] {Answer}")

        elif any(Queries.startswith(func) for func in Functions):
            # Already handled above
            continue

        elif "exit" in Queries:
            Answer = ChatBot(QueryModifier("Okay, Bye!"))
            print(Answer)
            os.exit(1)

    final_output = "\n\n".join(answers)
    if final_output:
        print(f"\n{Assistantname} →\n{final_output}")
    # Return both the response and device_action metadata
    return final_output, device_action

# if __name__ == "__main__":
#     while True:
#         user_query = input(f"{Username} → ").strip()
#         if user_query.lower() == "exit":
#             print("[Exiting]")
#             break
#         response = MainExecution(user_query)
#         print(f"{Assistantname} → {response}")
