# mirrormirror
_[In Collaboration With ChatGPT4o](https://chatgpt.com/share/f1de3333-6d48-4c29-ac67-e0ca509536c4)_

> These are three tools for times you wish to immediately automatically lock your MAC laptop if:
- Your face is not detected w/in a set period of time. <img src="icons/fo_enabled.png" alt="faceoff" style="width:30px; vertical-align:middle;">
- A specified bluetooth device loses contact with your laptop. <img src="icons/bt_enabled.png" alt="bluetooth_lock" style="width:30px; vertical-align:middle;">
- Your laptop moves more than a set distance in some period of time. <img src="icons/gf_enabled.png" alt="geo_fence" style="width:30px; vertical-align:middle;">


> Note!
- These default to running the lockscreen condition test every 5s. 
- Once enabled, these are designed to require the lockscreen condition to be triggered, and a re-authentication to then disable and quit the tool(s). 
- If you find this annoying, you probably do not need this tool. 
- Yahtzee!
  

## Pre-Requisites
- Intended For MAC Laptops ( tested on an Apple silicon M2 air MacOS 14.1.1 (23B81)). 
- Brew installed python 3.12 & cmake 3.30.3.arm64 &  dlib-19.24.6 .
- When you first run the scripts, you will be asked by MacOS to monitor inputs (prob from the terminal app you are using), you also will need to allow the same in Privay&Security->Accessibility and allow this app.

## Face Off
Locks a mac laptop if your face is not detected w/in a set period of time.  You might need to 
 
### Behavior
-  The script does not begin running when the UI boots up and does not begin running when the user ssh's into the machine. It does begin running when the user runs the script or configures to auto-load. When running, there is a small smiley face icon in the menu bar indicating the tool is running or suspended, and will dissappear when the tool quits. 
   -  You will need to have encoded your face first.
-  When triggered because the expected face of the allowed user is not detected, the script locks the screen, requiring re-authentication to unlock (but not with face). When logged back in, the script will be in a toggled off state and only begins if toggled on.  Once turned on and scanning, the only way to disable the feature is to sudo kill the running process, or to allow the lockscreen to be triggered, re-authenticate, and with the tool in a toggled off state, you may quit it.  **It is a design feature that this tool may not be disabled w/out going through a password re-authentication**.
- If you wish to make this more fussy, please do so! But, I believe for the use case, simple and reactive is best for me.



### Environment Setup

#### Brew Stuff
One dependency is only available via brew.  So, first you'll need brew installed.  Then:

```bash
brew install blueutil ffmpeg cmake
```

#### Python venv
_I would usually use conda, but for some reason, it was a huge pain to get MacOS to recognize conda python as allowed to use loc services... so I used venv._

```bash
python3.12 -m venv mirrormirror
source mirrormirror/bin/activate

pip install pystray pynput requests pyobjc-framework-CoreLocation pyobjc-core py2app opencv-python  ipython pytest face_recognition 

echo "happy birthday!"
```

<hr>
<hr> 
<hr>

### The Three Tools
#### First, Activate `mirrormirror` venv

```bash
source mirrormirror/bin/activate
```

<hr>
<hr>

#### FaceOff

![faceoff](icons/fo_enabled.png)

- When running these, you might need to tell your cell phone to disconnect if it tries to be the webcam.  Manually edit `cv2.VideoCapture(0) ` to be 0 or 1 if needed & automate this part if inspired to do so.
 
##### Face Encoding
Run [`bin/face_encoding.py`](bin/face_encoding.py) to create an encoding of your face.



##### Face Off Monitoring Tool
EDIT [`bin/face_off.py`](bin/face_off.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.

> Run the script and allow it to fail so that you can grant permission for it to lock the screen on your behalf.


### Automate Enabling Toggle Hotkey And Menu Bar Icon

#### Create LaunchAgent XML
_launchagent steps not yet tested_
Create `~/Library/LaunchAgents/com.$USER.faceoff.plist`, rename to match the above script. Use this template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.faceoff</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/mirrormirror/bin/python</string>
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

<hr>



## You Can Leave

![blueooth_lock](icons/bt_enabled.png)

A tool to lock your MAC laptop if your bluetooth device looses contact with your laptop.

### Behavior
- The tool does not begin at boot up or when the user logins in to the UI or by ssh. The script must be started manually, or may be automated to start when the UI is logged into.
-  The tool, once running, needs to be specifically enabled to begin its work. 
-  There is a small icon in the menu bar indicating the tool is running and if it is enabled or not. 
- When the tool is started, the menu displays the detected bluetooth devices. Select a device to monitor before you may enable monitoring for lock condition. When the device is not detected, the lockscreen is brough up and requires re-auth to unlock(assuming this is how your lockscreen is configured). When you re-auth, the tool will still be running, but now disabled. You may now quit it, or select a new device to monitor + enable monitoring.


### Environment
#### Activate MIRRORMIRROR venv

```bash
source mirrormirror/bin/activate
```


### Tool Script
Edit [`bin/you_can_leave.py`](bin/you_can_leave.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.

### Helpful Stuff

```bash
blueutil --paired
```

### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
_launchagent steps not yet tested_
Create` ~/Library/LaunchAgents/com.$USER.youcanleave.plist` (rename to match the above script), use this template::

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.youcanleave</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/mirrormirror/bin/python</string>
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

<hr>

## But Dont Go Far
<<<<<<< HEAD
_not quite tested for location violation triggering_
A script to lock your MAC laptop if it moves more than a set distance from the starting location the tool detected in some period of time.
=======

![gf](icons/gf_enabled.png)

A script to lock your MAC laptop if it moves more than a set distance in some period of time.
>>>>>>> 1c66f4be310ed36f1cea8d92513a9c6ffc11aa8a


### Behavior
- The tool does not begin at boot up or when the user logins in to the UI or by ssh. The script must be started manually, or may be automated to start when the UI is logged into. The first argument to the tool is a float representing the distance in meters that will trigger the lockscreen. The lat/long of the current laptop location is detected, and every time interval a new lat/long is detected, the distance from the starting location is calculated. If the distance exceeds the threshold, the lockscreen is triggered.
-  The tool, once running, needs to be specifically enabled to begin its work. 
-  There is a small icon in the menu bar indicating the tool is running and if it is enabled or not. Once enabled, the tool may only be disabled by triggering the lockscreen condition and re-authenticating, then quitting the tool (or re-enabling it).

### Environment
#### Activate MIRRORMIRROR venv

```bash
source mirrormirror/bin/activate
```


### Tool Script
Edit [`bin/but_dont_go_far.py`](bin/but_dont_go_far.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.

### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
_launchagent steps not yet tested_
Create `~/Library/LaunchAgents/com.$USER.butdontgofar.plist` (rename to match the above script), use this template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.butdontgofar</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/mirrormirror/bin/python</string>
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


## Issues Observed
<<<<<<< HEAD
- The face recognition library had a problem with the venvdlib, which necessitated brew python update and cmake update, then re-pip installing dlib  dlib-19.24.6.
=======
- The face recognition library had a problem with the conda dlib, which necessitated brew python update and cmake update, then repip installing dlib  dlib-19.24.6.
>>>>>>> 1c66f4be310ed36f1cea8d92513a9c6ffc11aa8a
