# NFC Attendance Registration System

This project is a Python-based NFC card registration system designed for FRC Team 2869. It uses the Adafruit PN532 NFC module to read NFC cards and associate them with user-defined names. Registered data is stored in a JSON file for easy lookup and management.

## Features

- Utilizes the Adafruit PN532 NFC module to read MiFare cards.
- Associates NFC card UID with user-provided names.
- Saves registered data in a JSON file for persistence.
- Stores attendance data in CSV files each day as a backup, and also sends sign in data to a server.
- Provides a clean UI which displays the current time, a logo, and greets the user signing in.

Note: This project was intended for use on a Raspberry Pi 3B+ Model, with a separate Java server used to collect the data.

## Contributions

This project was developed by Arsh Singh for FRC Team 2869. Contributions and suggestions are welcome.

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute this project as needed.