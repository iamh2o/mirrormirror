# mirrormirror
_[In Collaboration With ChatGPT4o](https://chatgpt.com/share/f1de3333-6d48-4c29-ac67-e0ca509536c4)_

For times you wish to to lock your MAC laptop if:
- Your face is not detected w/in a set period of time.
- Your bluetooth device looses contact with your laptop.
- Your laptop moves more than a set distance in some period of time.


## Pre-Requisites
- Intended For MAC Laptops ( tested on an Apple silicon M2 air MacOS 14.1.1 (23B81))
- Conda (all commands can be run with pip as well on the user level if desired and libraries installed with pip).

## Face Off
Locks a mac laptop if your face is not detected w/in a set period of time.
 
### Behavior
-  The script does not begin running when the UI boots up and does not begin running when the user ssh's into the machine. It does begin running when the user hits `Command+Shift+X`, and toggles off again when hit again. There is a small `FO` icon in the menu bar indicating the tool is running or not, and may also be clicked to turn on/off. The conda environment MIRRORMIRROR is properly used in automating the script and ongoing running of the script.
   -  You will need to have encoded your face first.
-  When triggered because the expected face of the allowed user is not detected, the script closes all open applications and locks the screen, requiring re-authentication to unlock (but not with face initially). When logged back in, the script begins again.  When triggered, there is a warning, and a 15 sec delay before the screen is locked and all open apps closed (this delay can not be preempted).  The only actions allowed when this warning appears are save actions in all open apps. 
  - Exception, the first failed detection, the user is given a warning which locks the screen for 15sec, and only allows 2 more attempts by hitting `command+shift+2` during the warning, After the second failed attempt,  all open applications and windows are closed and screen locked. The user must re-authenticate to log back in.
-  The script does not interfere with the normal operation of the computer, and does not cause any noticeable performance issues.


### Environment

#### Brew Stuff
One dependency is only available via brew.  So, first you'll need brew installed.  Then:

```bash
brew install blueutil
```

#### Conda Stuff (and by conda, I mean miniconda)
I use conda b/c it's quick and easy for me. You can also use venvs, pip install this all into your user python, or whatnot.

```bash
conda create -n MIRRORMIRROR -c conda-forge opencv ipython pytest && \
conda activate MIRRORMIRROR && \
pip install pystray
echo "happy birthday!"
```

### Scripts

#### Face Encoding
Run `[bin/face_encoding.py](bin/face_encoding.py)`

```python
import face_recognition
import cv2
import numpy as np
import pickle

# Open webcam
cap = cv2.VideoCapture(0)

print("Look at the camera to capture your face...")
ret, frame = cap.read()

# Convert frame from BGR (OpenCV format) to RGB (face_recognition format)
rgb_frame = frame[:, :, ::-1]

# Detect face locations and encode your face
face_locations = face_recognition.face_locations(rgb_frame)
face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

if face_encodings:
    # Save the face encoding to a file
    with open('your_face_encoding.pkl', 'wb') as f:
        pickle.dump(face_encodings[0], f)
    print("Face encoding saved successfully!")
else:
    print("No face detected, try again.")

cap.release()
```

#### Face Off Monitoring Tool
Rename the `bin/face_off.py` script to something you prefer, and edit the hotkeys to your liking:

```python
import cv2
import time
import os
import keyboard
import threading
import face_recognition
import pickle
from pystray import Icon, MenuItem as item, Menu
from PIL import Image

# Load your face encoding
with open('your_face_encoding.pkl', 'rb') as f:
    my_face_encoding = pickle.load(f)

timeout = 60  # Timeout before locking
face_not_detected_time = None
enabled = False  # Start disabled by default

# Placeholder for the pystray icon, updated later
icon = None

# Function to start face recognition
def start_face_recognition():
    global face_not_detected_time
    while enabled:
        cap = cv2.VideoCapture(0)  # Open the webcam
        ret, frame = cap.read()
        if not ret:
            cap.release()
            continue

        # Convert frame from BGR (OpenCV format) to RGB (face_recognition format)
        rgb_frame = frame[:, :, ::-1]

        # Detect face locations and encode faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_recognized = False
        for face_encoding in face_encodings:
            # Compare the detected face with your saved encoding
            matches = face_recognition.compare_faces([my_face_encoding], face_encoding, tolerance=0.65)
            if matches[0]:
                face_recognized = True
                break

        if face_recognized:
            face_not_detected_time = None
            print("Your face is detected.")
        else:
            if face_not_detected_time is None:
                face_not_detected_time = time.time()
            elif time.time() - face_not_detected_time >= timeout:
                print("Your face is not detected. Locking screen in 15 seconds.")
                time.sleep(15)  # Warning delay
                lock_screen()
                break

        cap.release()  # Release the camera after the check

        # Wait for 5 minutes before the next check (300 seconds)
        time.sleep(300)

def toggle_face_recognition():
    global enabled
    enabled = not enabled
    if enabled:
        print("Face recognition enabled.")
        threading.Thread(target=start_face_recognition).start()
    else:
        print("Face recognition disabled.")
    update_icon()

def lock_screen():
    os.system("osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")

# Update the menu bar icon when the state changes
def update_icon():
    if enabled:
        icon.icon = Image.open("enabled_icon.png")
        icon.title = "Face Off: Enabled"
    else:
        icon.icon = Image.open("disabled_icon.png")
        icon.title = "Face Off: Disabled"

# Function to quit the app
def quit_app(icon, item):
    icon.stop()

# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    menu = Menu(
        item('Toggle Face Recognition', toggle_face_recognition),
        item('Quit', quit_app)
    )
    icon = Icon("Face Off", Image.open("disabled_icon.png"), menu=menu)
    icon.run()

# Hotkey to toggle face recognition
keyboard.add_hotkey('cmd+shift+x', toggle_face_recognition)

# Run the menu bar icon in a separate thread
threading.Thread(target=setup_icon).start()

# Keep the script running indefinitely
keyboard.wait()


```


### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
Create `~/Library/LaunchAgents/com.$USER.faceoff.plist`, rename to match the above script.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.faceoff</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/conda/envs/MIRRORMIRROR/bin/python</string>
        <string>/path/to/face_off.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```



#### Load The LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.username.faceoff.plist # rename to match scipt name above
```



## You Can Leave
A tool to lock your MAC laptop if your bluetooth device looses contact with your laptop.

### Behavior
-  The tool does not begin at boot up or when the user logins in to the UI or by ssh.
-  The tool may be started/stopped by the user with the hotkey `Command + Shift + B`. There is a small `YCL` icon in the menu bar indicating the tool is running or not, and may also be clicked to turn on/off. When the tool is started, it reports the connected bluetooth devices, and allows the user to select the device to monitor, through a simple UI window option of paired devices. When toggling off, the expected bluetooth device is cleared, and when toggled back on the device will need to be specified again by the user.  When triggered, there is a warning, and a 15 sec delay before the screen is locked and all open apps closed (this delay can not be preempted), The only actions allowed when this warning appears are save actions in all open apps.
-  When triggered because the specified device has lost connection, the screen is locked, and all open apps closed, requiring the user to re-authenticate to log back in. When logging back in, the tool is not started automatically.
-  When triggered because the specified device hss lost connection, the user MAY NOT turbn off the tool. Nor may the user click the menu icon to turb off.
-  The tool does not interfere with the normal operation of the computer, and does not cause any noticeable performance issues.



### Environment
We will use the conda MIRROR environment created above.


### Tool Script
Rename the `bin/you_can_leave.py` script to something you prefer, and edit the hotkeys to your liking:

```python
import subprocess
import time
import os
import keyboard
import threading
from pystray import Icon, MenuItem as item, Menu
from PIL import Image

# Bluetooth device address (replace with your device's MAC address)
DEVICE_ADDRESS = "XX-XX-XX-XX-XX-XX"
bluetooth_lock_enabled = False  # Start disabled by default
icon = None  # Placeholder for the menu bar icon

# Function to check if Bluetooth device is connected
def check_bluetooth_connection():
    try:
        result = subprocess.run(["blueutil", "--connected", DEVICE_ADDRESS], stdout=subprocess.PIPE)
        return "0" in result.stdout.decode('utf-8')  # If the result is "0", the device is disconnected
    except Exception as e:
        print(f"Error checking Bluetooth connection: {e}")
        return False

# Function to lock the screen
def lock_screen():
    os.system("osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")

# Function to start the Bluetooth monitoring loop
def bluetooth_lock_loop():
    global bluetooth_lock_enabled
    while bluetooth_lock_enabled:
        if check_bluetooth_connection():
            print("Bluetooth device disconnected, locking screen...")
            lock_screen()
            break
        else:
            print("Bluetooth device connected.")
        time.sleep(60)

# Function to toggle the Bluetooth lock tool
def toggle_bluetooth_lock():
    global bluetooth_lock_enabled
    bluetooth_lock_enabled = not bluetooth_lock_enabled
    print("Bluetooth lock enabled" if bluetooth_lock_enabled else "Bluetooth lock disabled")

    if bluetooth_lock_enabled:
        threading.Thread(target=bluetooth_lock_loop).start()
    update_icon()

# Update the menu bar icon when the tool state changes
def update_icon():
    if bluetooth_lock_enabled:
        icon.icon = Image.open("enabled_icon.png")
        icon.title = "You Can Leave: Enabled"
    else:
        icon.icon = Image.open("disabled_icon.png")
        icon.title = "You Can Leave: Disabled"

# Function to quit the app
def quit_app(icon, item):
    icon.stop()

# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    menu = Menu(
        item('Toggle Bluetooth Lock', toggle_bluetooth_lock),
        item('Quit', quit_app)
    )
    icon = Icon("You Can Leave", Image.open("disabled_icon.png"), menu=menu)
    icon.run()

# Hotkey to toggle the Bluetooth lock (Command + Shift + B)
keyboard.add_hotkey('cmd+shift+b', toggle_bluetooth_lock)

# Run the menu bar icon in a separate thread
threading.Thread(target=setup_icon).start()

# Keep the script running indefinitely
keyboard.wait()

```

### Helpful Stuff

```bash
blueutil --paired
```

### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
Create` ~/Library/LaunchAgents/com.$USER.youcanleave.plist` (rename to match the above script):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.youcanleave</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/conda/envs/MIRRORMIRROR/bin/python</string>
        <string>/path/to/bluetooth_lock.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```


#### Load The LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.username.youcanleave.plist # rename to match scipt name above
```


## But Dont Go Far
A script to lock your MAC laptop if it moves more than a set distance in some period of time.


### Behavior
- The tool does not begin at boot up or when the user logins in to the UI or by ssh.
- The tool may be started/stopped by the user with the hotkey `Command + Shift + G`. There is a small `DGF` icon in the menu bar indicating the tool is running or not, and may also be clicked to turn on/off. When the tool is started, it reports the current address detected, and asks the user to specify how many miles as a float will trigger the tool to lock and close all windows, requiring a user to re-auth to log back in.  When toggling off, the specified address and distance tolock us cleared and will be reprompted when the user toggles this tool back on. When triggered, there is a warning, and a 15 sec delay before the screen is locked and all open apps closed (this delay can not be preempted). The only actions allowed when this warning appears are save actions in all open apps
- When triggered because the specified device has lost connection, the screen is locked, and all open apps closed, requiring the user to re-authenticate to log back in. When logging back in, the tool is not started automatically.
- When triggered because the specified device hss lost connection, the user MAY NOT turbn off the tool. Nor may the user click the menu icon to turb off.
- The tool does not interfere with the normal operation of the computer, and does not cause any noticeable performance issues.



### Environment
We will use the conda MIRROR environment created above.


### Tool Script
Rename the `bin/but_dont_go_far.py` script to something you prefer, and edit the hotkeys to your liking:

```python
import time
import os
import requests
import math
import keyboard
import threading
from pystray import Icon, MenuItem as item, Menu
from PIL import Image

# Distance monitoring state
distance_monitor_enabled = False  # Start disabled by default
icon = None  # Placeholder for the menu bar icon

# Initial location and distance threshold
current_location = None
distance_threshold = 0.0  # Set when the tool is activated

# Function to get the current location using an IP geolocation API
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/loc")
        return tuple(map(float, response.text.strip().split(',')))  # Latitude, Longitude
    except Exception as e:
        print(f"Error getting location: {e}")
        return None

# Function to calculate distance between two lat/long points (Haversine formula)
def calculate_distance(loc1, loc2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers

# Function to lock the screen
def lock_screen():
    os.system("osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")

# Function to start monitoring the distance
def distance_monitor_loop():
    global current_location
    while distance_monitor_enabled:
        new_location = get_current_location()
        if new_location:
            distance_moved = calculate_distance(current_location, new_location)
            print(f"Distance moved: {distance_moved} km")
            if distance_moved > distance_threshold:
                print(f"Exceeded distance threshold of {distance_threshold} km. Locking screen...")
                time.sleep(15)  # Warning delay
                lock_screen()
                break
        else:
            print("Unable to get new location.")
        time.sleep(2400)  # Check location every 2400 seconds

# Function to toggle distance monitoring
def toggle_distance_monitor():
    global distance_monitor_enabled, current_location, distance_threshold
    distance_monitor_enabled = not distance_monitor_enabled
    if distance_monitor_enabled:
        print("Distance monitor enabled.")
        current_location = get_current_location()
        if current_location:
            distance_threshold = float(input("Enter the distance threshold (in kilometers): "))
            threading.Thread(target=distance_monitor_loop).start()
        else:
            print("Failed to get current location. Disabling monitor.")
            distance_monitor_enabled = False
    else:
        print("Distance monitor disabled.")
    update_icon()

# Update the menu bar icon when the tool state changes
def update_icon():
    if distance_monitor_enabled:
        icon.icon = Image.open("enabled_icon.png")
        icon.title = "But Don't Go Far: Enabled"
    else:
        icon.icon = Image.open("disabled_icon.png")
        icon.title = "But Don't Go Far: Disabled"

# Function to quit the app
def quit_app(icon, item):
    icon.stop()

# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    menu = Menu(
        item('Toggle Distance Monitor', toggle_distance_monitor),
        item('Quit', quit_app)
    )
    icon = Icon("But Don't Go Far", Image.open("disabled_icon.png"), menu=menu)
    icon.run()

# Hotkey to toggle the distance monitor (Command + Shift + G)
keyboard.add_hotkey('cmd+shift+g', toggle_distance_monitor)

# Run the menu bar icon in a separate thread
threading.Thread(target=setup_icon).start()

# Keep the script running indefinitely
keyboard.wait()

```

### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
Create `~/Library/LaunchAgents/com.$USER.butdontgofar.plist` (rename to match the above script):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.butdontgofar</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/conda/envs/MIRRORMIRROR/bin/python</string>
        <string>/path/to/distance_lock.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

#### Load The LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.username.butdontgofar.plist # renme to match scipt name above
```


