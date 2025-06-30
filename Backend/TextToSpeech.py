# import pygame
# import random
# import asyncio
# import edge_tts
# import os
# from dotenv import dotenv_values

# # Load environment variables
# env_vars = dotenv_values(".env")
# AssistantVoice = env_vars.get("AssistantVoice")  # Fallback voice if not set

# # Asynchronous function to convert text to an audio file
# async def TextToAudioFile(text):
#     file_path = r"Data\speech.mp3"

#     if os.path.exists(file_path):
#         os.remove(file_path)

#     communicate = edge_tts.Communicate(text, voice=AssistantVoice, pitch='+5Hz', rate='+13%')
#     await communicate.save(file_path)

# # Function to manage Text-to-Speech (TTS) functionality
# def TTS(text, func=lambda r=None: True):
#     while True:
#         try:
#             asyncio.run(TextToAudioFile(text))

#             pygame.mixer.init()
#             pygame.mixer.music.load(r"Data\speech.mp3")
#             pygame.mixer.music.play()

#             while pygame.mixer.music.get_busy():
#                 if func() is False:
#                     break
#                 pygame.time.Clock().tick(10)  # Corrected from time.clock()

#             return True

#         except Exception as e:
#             print(f"Error in TTS: {e}")

#         finally:
#             try:
#                 func(False)
#                 pygame.mixer.music.stop()
#                 pygame.mixer.quit()
#             except Exception as e:
#                 print(f"Error in finally block: {e}")

# # Function to manage long Text-to-Speech with added randomness
# def TextToSpeech(Text, func=lambda r=None: True):
#     Data = str(Text).split(".")
#     responses = [
#             "The rest of the result has been printed to the chat screen, kindly check it out sir.",
#             "The rest of the text is now on the chat screen, sir, please check it.",
#             "You can see the rest of the text on the chat screen, sir.",
#             "The remaining part of the text is now on the chat screen, sir.",
#             "Sir, you'll find more text on the chat screen for you to see.",
#             "The rest of the answer is now on the chat screen, sir.",
#             "Sir, please look at the chat screen, the rest of the answer is there.",
#             "You'll find the complete answer on the chat screen, sir.",
#             "The next part of the text is on the chat screen, sir.",
#             "Sir, please check the chat screen for more information.",
#             "There's more text on the chat screen for you, sir.",
#             "Sir, take a look at the chat screen for additional text.",
#             "You'll find more to read on the chat screen, sir.",
#             "Sir, check the chat screen for the rest of the text.",
#             "The chat screen has the rest of the text, sir.",
#             "There's more to see on the chat screen, sir, please look.",
#             "Sir, the chat screen holds the continuation of the text.",
#             "You'll find the complete answer on the chat screen, kindly check it out sir.",
#             "Please review the chat screen for the rest of the text, sir.",
#             "Sir, look at the chat screen for the complete answer."
#         ]

#     if len(Data) > 4 and len(Text) >= 250:
#         TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
#     else:
#         TTS(Text, func)

# # CLI Execution
# if __name__ == "__main__":
#     while True:
#         TextToSpeech(input("Enter the text: "))



# TextToSpeech.py

import asyncio
import edge_tts
import os
from playsound import playsound
import random
from dotenv import dotenv_values

# Load environment variable
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-IN-NeerjaNeural")  # Fallback voice

async def TextToAudioFile(text, file_path="Data/speech.mp3"):
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(text, voice=AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def TTS(text, func=lambda r=None: True):
    file_path = "Data/speech.mp3"
    try:
        asyncio.run(TextToAudioFile(text, file_path))
        playsound(file_path)
        func()
    except Exception as e:
        print(f"[TTS Error] {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    messages = [
            "The rest of the result has been printed to the chat screen, kindly check it out sir.",
            "The rest of the text is now on the chat screen, sir, please check it.",
            "You can see the rest of the text on the chat screen, sir.",
            "The remaining part of the text is now on the chat screen, sir.",
            "Sir, you'll find more text on the chat screen for you to see.",
            "The rest of the answer is now on the chat screen, sir.",
            "Sir, please look at the chat screen, the rest of the answer is there.",
            "You'll find the complete answer on the chat screen, sir.",
            "The next part of the text is on the chat screen, sir.",
            "Sir, please check the chat screen for more information.",
            "There's more text on the chat screen for you, sir.",
            "Sir, take a look at the chat screen for additional text.",
            "You'll find more to read on the chat screen, sir.",
            "Sir, check the chat screen for the rest of the text.",
            "The chat screen has the rest of the text, sir.",
            "There's more to see on the chat screen, sir, please look.",
            "Sir, the chat screen holds the continuation of the text.",
            "You'll find the complete answer on the chat screen, kindly check it out sir.",
            "Please review the chat screen for the rest of the text, sir.",
            "Sir, look at the chat screen for the complete answer."
    ]

    if len(Text.split(".")) > 4 and len(Text) >= 250:
        part = " ".join(Text.split(".")[0:2]) + ". " + random.choice(messages)
        TTS(part, func)
    else:
        TTS(Text, func)

# CLI Test Execution
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        TextToSpeech(user_input)

