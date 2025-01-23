# By: Arsh Singh for FRC Team 2869

import board
import busio
import json
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

# Constants
NAMES_FILE_PATH = "client/names.json"

# I2C connection setup
i2c = busio.I2C(board.SCL, board.SDA)
reset_pin = DigitalInOut(board.D6)
req_pin = DigitalInOut(board.D12)

# Initialize PN532
def initialize_pn532():
    pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
    ic, ver, rev, support = pn532.firmware_version
    print(f"Found PN532 with firmware version: {ver}.{rev}")
    pn532.SAM_configuration() # Configure PN532 to communicate with MiFare cards
    return pn532

pn532 = initialize_pn532()

# Load names from JSON file
def load_names(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Names file not found. Creating a new one.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON file. Starting with an empty list.")
        return []

def save_names(file_path, names):
    with open(file_path, "w") as file:
        json.dump(names, file, indent=4)

names_list = load_names(NAMES_FILE_PATH)

# Helper function to validate name input
def get_name_input():
    while True:
        name = input("Enter name in the form first_last: ").lower()
        if name.count("_") == 1 and name.replace("_", "").isalpha():
            return name
        print("Invalid input! Please follow the format 'first_last'.")

# Main loop
print("Waiting for RFID/NFC card...")
while True:
    try:
        # Check for an NFC card
        uid = pn532.read_passive_target(timeout=0.5)

        if uid is None:
            continue

        uid_str = "".join([hex(i) for i in uid])

        # Check if UID is already in the names list
        for entry in names_list:
            if uid_str == entry["id"]:
                print(f"Card belongs to: {entry['name']}")
                break
        else:
            print("Found new card with UID:", uid_str)
            name = get_name_input()

            if name == "stop":
                print("Exiting program.")
                break

            # Add new entry to the list
            new_entry = {"name": name, "id": uid_str}
            names_list.append(new_entry)

            # Save updated names list
            save_names(NAMES_FILE_PATH, names_list)
            print(f"Added {name} with UID {uid_str} to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")