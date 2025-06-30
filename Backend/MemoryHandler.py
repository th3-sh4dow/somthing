import json
import os
from datetime import datetime

MEMORY_FILE = "Data/memory.json"

def init_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)

def save_task(task, pending=None):
    data = {
        "last_task": task,
        "last_session_time": str(datetime.now()),
        "pending_tasks": pending if pending else []
    }
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

def load_memory():
    file_path = "Data/Status.data"

    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        # File doesn't exist or is empty
        return []

    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # Handle corrupted JSON gracefully

def add_pending_task(task):
    memory = load_memory()
    memory.setdefault("pending_tasks", []).append(task)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)
