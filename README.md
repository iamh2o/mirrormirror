# mirrormirror
_[In Collaboration With ChatGPT4o](https://chatgpt.com/share/f1de3333-6d48-4c29-ac67-e0ca509536c4)_

For times you wish to to lock your MAC laptop if:
- Your face is not detected w/in a set period of time.
- Your bluetooth device looses contact with your laptop.
- Your laptop moves more than a set distance in some period of time.


## Pre-Requisites
- Intended For MAC Laptops ( tested on an Apple silicon M2 air MacOS 14.1.1 (23B81)). 
- Brew installed python 3.12 & cmake 3.30.3.arm64 &  dlib-19.24.6 .
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
conda create -y -n MIRRORMIRROR -c conda-forge python==3.12.2 opencv ipython pytest face_recognition && \
conda activate MIRRORMIRROR && \
pip install pystray
echo "happy birthday!"
```

### Scripts
#### Activate MIRRORMIRROR

```bash
conda activate MIRRORMIRROR
```

#### Face Encoding
Run [`bin/face_encoding.py`](bin/face_encoding.py) to create an encoding of your face.



#### Face Off Monitoring Tool
EDIT [`bin/face_off.py`](bin/face_off.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.


### Automate Enabling Toggle Hotkey And Menu Bar Icon

#### Create LaunchAgent XML

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
#### Activate MIRRORMIRROR

```bash
conda activate MIRRORMIRROR
```


### Tool Script
Edit [`bin/you_can_leave.py`](bin/you_can_leave.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.

### Helpful Stuff

```bash
blueutil --paired
```

### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
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
Edit [`bin/but_dont_go_far.py`](bin/but_dont_go_far.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.

### Automate Enabling Toggle Hotkey And Menu Bar Icon
#### Create LaunchAgent XML
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


## Issues Observed
- The face recognition library had a problem with the conda dlib, which necessitated brew python update and cmake update, then repip installing dlib  dlib-19.24.6.