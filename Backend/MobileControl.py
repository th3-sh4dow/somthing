import requests

MOBILE_IP = "http://192.168.1.100:5000"  # 🔁 Replace with your phone IP

def speak_on_phone(msg):
    return requests.post(f"{MOBILE_IP}/say", json={"message": msg}).json()

def vibrate_phone(duration=300):
    return requests.post(f"{MOBILE_IP}/vibrate", json={"duration": duration}).json()

def get_battery_status():
    return requests.get(f"{MOBILE_IP}/battery").json()

def call_number(number):
    return requests.post(f"{MOBILE_IP}/call", json={"number": number}).json()

def send_sms(number, msg):
    return requests.post(f"{MOBILE_IP}/sms", json={"number": number, "message": msg}).json()

def toggle_flashlight(state="on"):
    return requests.post(f"{MOBILE_IP}/torch", json={"state": state}).json()
