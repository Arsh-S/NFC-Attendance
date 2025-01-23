# By: Arsh Singh for FRC Team 2869

import os
import tkinter as tk
from tkinter.font import Font
from PIL import ImageTk, Image
from datetime import datetime
import pytz
import asyncio
import csv
import json
import requests
from py532lib.i2c import Pn532_i2c
from async_tkinter_loop import async_mainloop

# Constants
SERVER_IP = "YOUR_SERVER_IP"
TIMEZONE = pytz.timezone("US/Eastern")
JSON_FILE_PATH = "client/names.json"
LOGO_PATH = "client/RegalEagleLogo.png"
ATTENDANCE_DIR = "client/attendance/"

# Initialize PN532
pn532 = Pn532_i2c()
pn532.SAMconfigure()

# Load Names from JSON File
with open(JSON_FILE_PATH, "r") as file:
    namesList = json.load(file)

# Initialize Tkinter
root = tk.Tk()
root.title("NFC Attendance App")
root.attributes("-fullscreen", True)
root.geometry("1920x1080")

# Fonts
bigFont = Font(family="Calibri", size=100)
nameFont = Font(family="Calibri", size=150, weight="bold")
timeFont = Font(family="Calibri", size=75)

# UI Elements
logo = Image.open(LOGO_PATH).resize((200, 200), Image.LANCZOS)
logoTk = ImageTk.PhotoImage(logo)
logoLabel = tk.Label(image=logoTk)
logoLabel.image = logoTk
logoLabel.place(x=0, y=0)

textVar = tk.StringVar()
textLabel = tk.Label(root, textvariable=textVar, font=bigFont)
textLabel.pack(pady=50, padx=50)

nameVar = tk.StringVar()
nameLabel = tk.Label(root, textvariable=nameVar, font=nameFont)
nameLabel.place(relx=0.5, rely=0.5, anchor="center")

timeVar = tk.StringVar()
timeLabel = tk.Label(root, textvariable=timeVar, font=timeFont)
timeLabel.place(relx=1, rely=1, anchor="se")

nameVar.set("Tap to sign in...")
textVar.set("")

# Helpers
def resetName():
    nameLabel.config(font=nameFont)
    nameVar.set("Tap to sign in...")
    textVar.set("")

def setName(name, localtime):
    formatted_name = " ".join(part.capitalize() for part in name.split("_"))
    nameLabel.config(font=Font(family="Calibri", size=1500 // (1 + len(formatted_name)), weight="bold"))
    textVar.set(welcomeOrGoodbye(name, localtime))
    nameVar.set(formatted_name)
    root.after(3000, resetName)

def welcomeOrGoodbye(name, localtime):
    loginDate = datetime.fromtimestamp(int(localtime)).astimezone(TIMEZONE).date()
    file_path = os.path.join(ATTENDANCE_DIR, f"{loginDate}.csv")
    
    if not os.path.exists(file_path):
        return "Welcome!"
    
    with open(file_path, "r") as csvFile:
        return "Goodbye!" if csvFile.read().count(name) > 1 else "Welcome!"

def CsvAddLogin(loginName, loginTime):
    parsedDatetime = datetime.fromtimestamp(int(loginTime)).astimezone(TIMEZONE)
    loginDate = parsedDatetime.date()
    loginTime = parsedDatetime.strftime("%X")

    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    file_path = os.path.join(ATTENDANCE_DIR, f"{loginDate}.csv")
    
    with open(file_path, "a+", newline="") as csvFile:
        csv.writer(csvFile).writerow([loginName, loginTime])

def send_data_to_server(url, name):
    try:
        response = requests.get(f"{url}{name}/")
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        print("Error sending data:", e)
        return None

# Async Functions
async def updateTime():
    while True:
        timeVar.set(datetime.now().astimezone(TIMEZONE).strftime("%-I:%M:%S %p"))
        await asyncio.sleep(1)

async def scan():
    while True:
        try:
            card_data = pn532.read_mifare().get_data()
            if not card_data:
                continue

            card_data_hex = "".join([hex(x) for x in card_data])
            print("Found card with data:", card_data_hex)

            if card_data_hex in namesList:
                localTime = datetime.now(TIMEZONE).strftime("%s")
                CsvAddLogin(card_data_hex, localTime)
                setName(card_data_hex, localTime)
                await asyncio.sleep(3)  # Delay before next scan
            else:
                setText("Unrecognized NFC Tag!")
                await asyncio.sleep(3)
        except Exception as e:
            print("Error during scan:", e)

def start_system():
    asyncio.create_task(scan())
    asyncio.create_task(updateTime())

# Main Loop
if __name__ == "__main__":
    root.after(500, start_system)
    async_mainloop(root)