# KeyLogger Project

## Overview
This project will be an fully functional system based on these 3 parts:
- KeyLogger Agent: A pythonic program that uses ׳pynput׳ and runs on the target computer and in charge of gatering keyboard keystrokes, encrypting keystrokes and sending them to the server.
- Backend Side: Flask server that gets, decrypts and saves the data.
- Frontend (UI): A webpage that shows the data gathered in a nice way.

### Legal Issues
This project is designated for educational purposes. Do not use this project for illegal or unethical uses. The work is executed on local enviroment only and with computer owners permission. 

## Section #1

## General Content
0. Design - For collaborators
- You need to plan the teamwork on the project.

### Required Result:
    - A flowchart of the responsibilities. for example:
        - KeyLoggerService: Data gathering and sending upon request
        - KeyLoggerManager: Looping, and reading keystrokes every n seconds, binding them to the Buffer that transfer the data to FileWriter and optionaly also to NetworkWriter.
        - FileWriter: Gets a string of text and writes to file witha timestamp, having through a encryption via Encryptor.
        - NetworkWriter: Gets data and tranfer is to the server via IWriter class.
        - Encryptor: In charge of doing XOR or other encryption.

## Step 1: Implementing KeyLoggerService:
First of all:
There will be 3 files for the keylogger, one for each os type. 
the app.py in the backend side will ask the user on the frontend side (using buttons) which OS to use.


At this point, we will align and implement the KeyLoggerService in a uniform interface. The goal is to create a class that listens to keyboard keystrokes and temporarily stores them in memory (Buffer) for later use.

- Implementation Requirements:
    1. We will set a IKeyLogger class with the following functions:
        - start_logging(): Starting the Listener
        - stop_logging(): Stopping the Listener
        - get_logged_keys() -> list[str]: Returning a string of all keystrokes gathered.
    2. We will implement a KeyLoggerService class that will implement the IKeyLogger class.
    3. We will use pynput library for listening to keyboard keystrokes.

At this point, the goal is to "clean up the noise" and provide a consistent starting point so that later on, capabilities such as encryption, writing to a file, and sending to a server can be added. Using a defined interface allows for clean, maintainable, and modular code, so that the KeyLoggerService implementation can be easily replaced or upgraded.

Helper class:

from abc import ABC, abstractmethod 
from typing import List 
 
class IKeyLogger(ABC): 
    @abstractmethod 
    def start_logging(self) -> None: 
        pass 
     
    @abstractmethod 
    def stop_logging(self) -> None: 
        pass 
     
    @abstractmethod 
    def get_logged_keys(self) -> List[str]: 
        pass 

### Required Result: 
- A working KeyLoggerService that listens to keystrokes and stores them in memory. 
- The implementation will be carried out according to a uniform interface (IKeyLogger), so that in the future the code can be easily expanded.

## Step 2: FileWriter Implementaion
Task: Implementing a class named FileWriter that is responsible for writing to the file.

FileWriter is handling only the writing to file process, and the KeyLoggerManager class will work on the data before sending it.

### Required Result:
- FileWriter that gets a string of text and writes it to the file.

Example:
from abc import ABC, abstractmethod 
class IWriter(ABC): 
    @abstractmethod 
    def send_data(self, data: str, machine_name: str) -> None: 
        pass 

## Step 3: Writing XOR Encryption
Task: 
1. Write an Encryptor class that executes a basic XOR encryption on the data stored.
2. Save a simple key for the XOR operation.

Encryption is a vital part in the project - the sensitive data should'nt be saved openly in a file. XOR is a simple method that uses basics consepts of encryption.

### Required Result:
The file will be saved encrypted - so that when a user try to read the file directly, the text will look gibberish. Only those who have the decryption function and key can read the data.

## Step 4: KeyLoggerManager Implementation
Task:
Implement a KeyLoggerManager class that will receive the KeyLoggerService and the FileWriter, and manage the central Buffer.

Will do, on a periodic time:
- Gathering keystrokes from KeyLoggerService
- Binding data to the Buffer
- When the program is stopped:
    - Adds a timestamp to the data
    - Encrypting data with Encryptor
    - Transfering encrypted string to FileWriter

Centralizes the logic of data collection, processing, and transmission.
Allows flexibility in changes – for example, changing the update frequency, changing the encryption method, adding Buffer management

### Required Result:
KeyLoggerManager which initiates the collection, bundles the data, adds a timestamp, and performs encryption before sending the data to the writer class (and, if configured, to the sender class to the network).

### A secret agent decrypts the file
Task:
1. Write a script that gets the path for the encrypted file and the xor key from the user in the CLI.
2. The script will load the file, will process decryption, and will print the decrypted data to the screen.

### Required Result:
A Python file that allows you to recover the visible information from the file that the keylogger created.

## Step 5: Retina writing
Task:
Implement a NetworkWriter according to the IWriter, that will use the requests library to send data to the server.

### Required Result:
A class that implements this method:
send_data(data: str, machine_name: str) -> None


Advice:
Think on handling Execptions and Logs in every segment.

## Requirements:
Code will be compatible for all major OS, like Windows, MacOS and Linux.


## Section #2: Backend Implementation
The server will be for 2 main uses:
- Getting the KeyLogger data and keeping them for later use.
- Allowing the option to get keystrokes data, so the user will be able to access them on the frontend side.

The backend must be in Python and is recommended to use Flask (but other option like Django are allowed).

## Step 0: Design
- Define the data architecture for the Backend.
- Think about how you would like to organize the information in the file system so that you can differentiate between each machine and another, and save text files containing the keystrokes in a hierarchical manner.

- Consider if you prefer to create new file for each POST or to bind few to a single file.

### Required Result:
here is a textual description:
- data/
  - machine1/
    - Log_2025-02-03_10-15-00.txt
    - Log_2025-02-03_10-20-00.txt
  - machine2/
    - Log_2025-02-03_11-00-00.txt

An example to folders structure:
KeyLogger Project/
  backend/
    ├── app.py
    ├── data/ 
  index.html
  static/
    ├── assets/
        ├── images/
    ├── css/
    ├── js/
  README.md


## Step 1: 
Task:

1. Make sure Flask is installed (or install it using pip install flask).
2. Create a new backend folder and navigate to it.
3. Inside the folder, create the following files:
  3.1. app.py (server main file)
  3.2. data/ (in which keylogger files will be stored)

### Required Result:
Project structure that includes data folder and an empty app.py file

## Step 2: Creating basic Flask server
Task:
1. Open app.py and insert the following code:

from flask import Flask, jsonify
app = Flask(__name__)
@app.route('/')
def home():
  return "KeyLogger Server is Running"
if __name__ == '__main__':
  app.run(debug=True) 

2. Run the server (python app.py) and make sure it works.
3. Go to address http://127.0.0.1:5000 and check if page loads successfully.

### Required Result:
An active Flask server that shows a message in the browser.

## Step 3: Creating API to get KeyLogger data
Task:
Create a listener via Flask that will listen to data from the tool.

### Required Result:
Data from the tool will be recieved by the server, will be decrypted and saved to the disk under data/ folder.

- POST to api/upload/ that gets data and save it in structure:
  - data/<machine>/log_<timestamp>.txt

Here is a starter code (rest of app.py):

from flask import request
import time

def generate_log_filename():
  return "log_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
@app.route('/api/upload', methods=['POST'])
def upload():
  data = request.get_json()
  if not data or "machine" not in data or "data" not in data:
    return jsonify({"error": "Invalid payload"}), 400
  machine = data["machine"]
  log_data = data["data"]

  machine_folder = os.path.join(DATA_FOLDER, machine)
  if not os.path.exists(machine_folder):
    os.makedirs(machine_folder)

  filename = generate_log_filename()
  file_path = os.path.join(machine_folder, filename)

  with open(file_path, "w", encoding="utf-8") as f:
    f.write(log_data)

  return jsonify({"status": "success", "file": file_path}), 200

## Step 4: Creating API to get computer list
Task:
Create an API on your server named get_target_machines_list(), allowing to get the computer list on which the tool ran so far.
The computer list will be extracted from folders names, no need for a database.

### Required Result:
A GET call to api/get_target_machines_list/ will return a JSON array with computers names.

## Step 5: Extracting specific machine keystrokes data
Task:
Create an API in the server named get_target_machine_key_strokes(target_machine) that allows to get keystrokes from a specific machine.

### Required Result:
A call to pi/get_keystrokes?machine=computer1/ will return a JSON with the computer data.


## Section #3: Frontend Implementation

### Overview
The frontend provides a clean, modern interface for the keylogger application with a dark/light theme system and responsive design.

### Technical Stack
- HTML5 for structure
- CSS3 for styling
- Vanilla JavaScript for functionality
- Font Awesome for icons
- JetBrains Mono font for typography

### Key Components

1. Header
   - Logo display
   - Application title
   - Navigation menu with smooth scrolling
   - Responsive design

2. Main Sections
   - OS Type Selection
     - Windows, Linux, and MacOS options
     - Interactive icon buttons
   
   - Connected Devices
     - Grid layout for device cards
     - Status indicators
     - Device information display
   
   - Logs
     - Real-time logging display
     - Start/Stop/Clear controls
     - Custom scrollbar styling
     - Monospace formatting
   
   - History
     - Date and time filtering
     - Scrollable log entries
     - Entry timestamps
     - Search functionality
   
   - About
     - Project description
     - Team member profiles
     - Social links integration
   
   - Contact
     - Contact information display
     - Form integration with Formspree
     - Responsive grid layout

### Styling Features

1. Theme System
   - Dark/light mode toggle
   - Custom CSS variables for colors
   - Smooth transitions
   - Persistent theme preference

2. Color Scheme
   - Primary colors:
     - Black (#000000)
     - Purple (#7B68EE)
     - Turquoise (#40E0D0)
   - Supporting colors for text and backgrounds

3. UI Components
   - Custom button styles
   - Interactive hover effects
   - Custom scrollbars
   - Responsive containers
   - Card-based layouts

### Responsive Design
- Mobile-first approach
- Flexible grid systems
- Breakpoint at 768px for layout changes
- Adaptive component sizing
- Touch-friendly interface elements

### Browser Compatibility
- Modern browser support
- Custom scrollbar fallbacks
- CSS variable fallbacks
- Cross-browser tested



# Key-Logger
