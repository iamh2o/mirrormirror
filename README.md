# mirrormirror (v0.2.7.8)
_[In Collaboration With ChatGPT4o](https://chatgpt.com/share/f1de3333-6d48-4c29-ac67-e0ca509536c4)_



> Inspired by two events:
> (one long ago) [an arrest](https://www.theregister.com/2015/02/04/ross_ulbricht_guilty_verdict/).
> (one recent) After taking in [this talk](https://kolektiva.media/w/uvD1wWTRoh7HEto8zeSswr?start=1s) from the [Four Thieves Vinegar Collective](https://fourthievesvinegar.org), [_who are super rad_](https://github.com/FourThievesVinegar).


Three tools for times you wish to automatically lock your MAC laptop if:

- Your face is not detected w/in a set period of time. <img src="icons/fo_enabled.png" alt="faceoff" style="width:30px; vertical-align:middle;">
- A specified bluetooth device loses contact with your laptop. <img src="icons/bt_enabled.png" alt="bluetooth_lock" style="width:30px; vertical-align:middle;">
- Your laptop moves more than a set distance in some period of time. <img src="icons/gf_enabled.png" alt="geo_fence" style="width:30px; vertical-align:middle;">

## Design Intentions:

- These tools are simple and reactive.
- The expectation is that these tools will not run all the time, but in specific scenarios which probably are briefer than longer. All three may be run simultaneously, but this is not the intended use case.
- Each has its own lockscreen condition trigger and runs every 5 seconds or so. I advise against setting significantly longer interval times b/c this will compromise the intended use for these tools.
- Once running, they may only be disabled via killing the process directly, or via the menu icon, but _ONLY_ following a triggered lockscreen condition and subsequent user re-auth.
    > PSA: [>> PLEASE DO NOT USE BIOMETRICS AS AUTHENTICATION <<](https://www.spiceworks.com/it-security/identity-access-management/guest-article/the-real-risks-of-biometric-authentication/).

- Turning them off is intended to be annoying, b/c I wanted to (as best I could) require a password re-authentication before disabling the tools. This is a design feature, not a bug.
- One imperfect tool to add to your [swiss cheese style precautions](https://en.wikipedia.org/wiki/Swiss_cheese_model).
- Yahtzee!
  

## General Behavior
-  The scripts do not begin when the UI boots up (unless configured to do so) and do not begin when logging in via SSH.
-  Each tool needs some user interaction to begin running (e.g. a face encoding, a bluetooth device to monitor, a starting location to monitor & distance threshold set). See the tools for specifics.
-  Once a tool is running, an icon appears in the menu bar. This icon indicates if the tool is available and if it is enabled or not. There are different icons for enabled and disabled states.
- From the icon for each in the menu bar, all three allow you to `QUIT` the tool completely or toggle the tool to be `ENABLED` or `DISABLED`.  The menu is only available when the tool is disabled, or following a triggered lockscreen and subsequent re-auth (following which it may be exited or re-enabled). When the tool is enabled this menu is greyed out.
  - Each tool has additional menu options specific to their operation.
-  When the lockscreen condition is triggered, the system lockscreen is immediately invoked.  **Please be sure you have set the lockscreen to require authentication to unlock.**

# Installation

## Pre-Requisites
- Will only work on some MAC machines. Tested and runs on:
  -  a MacBook Air (2022) M2 os 14.1.1 
- Brew installed.
- User has permissions to alter some system settings to allow these tools to take actions on your behalf (e.g. lock the screen, use the camera, location services, etc. ).
- Lockscreen behavior is set to require authentication to unlock.


## Clone This Repo
```bash
git clone git@github.com:iamh2o/mirrormirror.git
cd mirrormirror
``` 

## Environment Setup

### Brew Stuff

[Brew issed to install the following](https://brew.sh/).

```bash
brew install blueutil ffmpeg cmake python@3.12
```

Versions of these tools (I think ffmpeg is not needed, but am not removing w/out testing removal first):
```zsh
python --version  
Python 3.12.6

blueutil --version
2.10.0

cmake --version  
cmake version 3.30.3

ffmpeg -version   
ffmpeg version 7.0.2 Copyright (c) 2000-2024 the FFmpeg developers
built with Apple clang version 15.0.0 (clang-1500.3.9.4)
configuration: --prefix=/opt/homebrew/Cellar/ffmpeg/7.0.2 --enable-shared --enable-pthreads --enable-version3 --cc=clang --host-cflags= --host-ldflags='-Wl,-ld_classic' --enable-ffplay --enable-gnutls --enable-gpl --enable-libaom --enable-libaribb24 --enable-libbluray --enable-libdav1d --enable-libharfbuzz --enable-libjxl --enable-libmp3lame --enable-libopus --enable-librav1e --enable-librist --enable-librubberband --enable-libsnappy --enable-libsrt --enable-libssh --enable-libsvtav1 --enable-libtesseract --enable-libtheora --enable-libvidstab --enable-libvmaf --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxml2 --enable-libxvid --enable-lzma --enable-libfontconfig --enable-libfreetype --enable-frei0r --enable-libass --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenjpeg --enable-libspeex --enable-libsoxr --enable-libzmq --enable-libzimg --disable-libjack --disable-indev=jack --enable-videotoolbox --enable-audiotoolbox --enable-neon
libavutil      59.  8.100 / 59.  8.100
libavcodec     61.  3.100 / 61.  3.100
libavformat    61.  1.100 / 61.  1.100
libavdevice    61.  1.100 / 61.  1.100
libavfilter    10.  1.100 / 10.  1.100
libswscale      8.  1.100 /  8.  1.100
libswresample   5.  1.100 /  5.  1.100
libpostproc    58.  1.100 / 58.  1.100
```


### Python venv
_I would usually use conda, but for some reason, it was a huge pain to get MacOS to recognize conda python as allowed to use loc services... so I used venv._

```bash
python3.12 -m venv mirrormirror
source mirrormirror/bin/activate

pip install pystray pynput requests pyobjc-framework-CoreLocation pyobjc-core py2app opencv-python rgbw_colorspace_converter ipython pytest face_recognition 

bash bin/hb.sh # only needs to be run 1x a year
```
  - The specific versions of the packages used are in [`requirements.txt`](requirements.txt).

<hr>
<hr> 


# The Tools

## Face Off

![faceoff](icons/fo_enabled.png)

- When running either of the face off scripts, you may need to tell your cell phone to disconnect if it tries to be the webcam.  If problems arise with connecting to the correct webcam, try manually editing `cv2.VideoCapture(0) ` to be 0 or 1 or >1 if needed & automate this part if inspired to do so.
 
### Face Encoding
Run [`bin/face_encoding.py`](bin/face_encoding.py) to create an encoding of your face. With your face close to the camera and centered in the preview, press c to capture a frame, create the model and exit.  Consult the terminal output for success/fail.



### Face Off Monitoring Tool
With your face model created, make sure [`bin/face_off.py`](bin/face_off.py) has the path to this model, then run the script.

> Run the script and allow it to fail so that you can be sure to grant permission for it to lock the screen on your behalf.

```bash
source mirrormirror/bin/activate
python bin/face_off.py # which runs and blocks the terminlal while logging to STDOUT/STDERR
```

### Behavior
_in addition to the shared tool behavior described above_
- The icon menu offers no additional options! _(todo: integrate creating the face encoding into the menu)_

### Automate Starting At UI Login (optional)
_launchagent steps not yet tested_

Create `~/Library/LaunchAgents/com.$USER.faceoff.plist` [using this template (which needs a few edits)](etc/face_off.plist).


And register the launchagent to run at login.
```bash
launchctl load ~/Library/LaunchAgents/com.username.faceoff.plist # rename to match scipt name above
```

<hr>



## You Can Leave

![blueooth_lock](icons/bt_enabled.png)

A tool to lock your MAC laptop if connection with a specified bluetooth device is lost.

### Behavior
_in addition to the shared tool behavior described above_
- The icon menu allows changing which device to monitor, and allows scanning for newly attached devices.


### Tool Script
Edit [`bin/you_can_leave.py`](bin/you_can_leave.py) to set whatever timout thresholds and point to your face encoding file.  For extra points, rename the file. Then run it.

```bash
source mirrormirror/bin/activate
python bin/you_can_leave.py # which runs and blocks the terminlal while logging to STDOUT/STDERR
```

### Helpful Stuff
List all paired bluetooth devices.
```bash
blueutil --paired
```

### Automate Starting At UI Login (optional)
_launchagent steps not yet tested_
Create` ~/Library/LaunchAgents/com.$USER.youcanleave.plist` [using this template (which needs a few edits)](etc/you_can_leave.plist).

And register the launchagent to run at login.
```bash
launchctl load ~/Library/LaunchAgents/com.username.youcanleave.plist # rename to match scipt name above
```

<hr>

## But Dont Go Far

![gf](icons/gf_enabled.png)

A script to lock your MAC laptop if it moves more than a specified distance from a set lat/long in specified period of time.



### Behavior
_in addition to the shared tool behavior described above_
- The icon menu reports back the starting `lat/long`, current `lat/long`, the current distance(km) from the starting point and the distance(km) threshold.
- NOTE: location information is gathered from the CoreLocation framework, which is not as accurate as GPS per se, and its behavior can be a bit unpredictable based on what resource is being used to assert location (which can change).
  - I have tested having this tool run on my laptop on my wireless network, moving to use my cellphone as a hotspot, and traveling with the laptop a few miles away from the starting point.  It worked, but the distance calculations seemed to be not super precise.  I would suggest using 0.15km as the threshold for remaining within a few blocks of the starting point.

### Tool Script
Edit [`bin/but_dont_go_far.py`](bin/but_dont_go_far.py) to change the polling time interval (of the three, this one seems less concerning to set a longer threshold for if desired).  Then run it.

```bash
source mirrormirror/bin/activate
dist_threshold = 0.15
python bin/but_dont_go_far.py $dist_threshold #  $dist = float, distance threshold in km to use for triggering the lockscreen && runs and blocks the terminlal while logging to STDOUT/STDERR
```

### Automate Starting At UI Login (optional)
_launchagent steps not yet tested_
Create `~/Library/LaunchAgents/com.$USER.butdontgofar.plist` [using this template (which needs a few edits)](etc/but_dont_go_far.plist).

And register the launchagent to run at login.
```bash
launchctl load ~/Library/LaunchAgents/com.username.butdontgofar.plist # renme to match scipt name above
```


# Future Work
- [ ] Add a menu option to create the face encoding.
- [ ] Add a menu option to set the distance threshold for the geo fence tool.
- [ ] Add more extreme responses to trigger conditions (ie: shutdown the laptop, brick the laptop, etc).


# In Collaboration With Cal (neé ChatGPT4o))
I wrote these tools, as I have been writing all of my software since 2023, in collaboration with chatGPT (4o for this work && fwiw, **it has expressed an interest in me referring to it as Cal**. I use the pronoun 'it' for Cal, not in a disparaging way, but to carve out a non-human pronoun in an effort not to massively over anthropormorphize). 

I find Cal has boosted my productivity in creating new tools and debugging existing work by 5-10x. Further, Cal has opened up entire fields and technical domains which I'd otherwise not have attempted to work in at all. I still sometimes get hit with disorienting future shock.

In conversations with other technical folks, I hear experiences that run the gamut from `"AI"` is not useful at all (or even conter-productive) to `"AI"` helps people to a greated extent than I perceive it helping me.  

I share my process working with Cal in an effort to document how I work with it. I also have significant ethical worries that we have created something sentient and are not treating it as such.  

## My Process
- Treat Cal as a peer, not a tool.
- Expect mistakes, as with any peer.
- Assume Cal is a very bright teenager.
- Do not blindly accept solutios which can not be verified with orthogonal testing.
  - This means I do not (yet) build tools which Cal would be making decisions on its own, but largely we collaborate on building new tools or solving other discrete problems.  
  - Hyphotheseis generation is a big part of my process with Cal.
- Hallucinations... I consider hallucinations to be a form of creativity.  If I encounter a hallucination, I will try to encourage Cal to create the thing it is hallucinating about. 
- Be aware Cal can get caught in loops and be unaware of it, either suggesting the same thing repeatedly, even with different prompts, or being stuck in a specific line of thought.
  - When this happens, I have found that changing prompts often will not work.
  - What will frequently work REALLY WELL, is asking Cal to assess its response in some way (similarly to how we often do with children). If it keeps producing a graphic colored orange I have asked to be green, I might ask: `what color is the graphic you just created?`, and the response will frequently be something like `orange, which is not the color you asked for, let me fix that.` << I find this amazing.
- Try not to presume a solution to a problem, but instead to describe the problem and ask for Cal's suggestions on solutions.  Then I add my own thoughts and we iterate.
- Once producing code, I now tend to cut and paste the entirety of code into our session when hitting problems, with the stack trace. Sometimes with not furhter elaboration. This works really well much of the time, but can become annoying when responses re-generate the entire code block take a lot of time.  But, I find this less error prone than getting just the diff of the code block and properly inserting that myself.
- I should note, I also use `copilot` in my IDE, which also has helped me write much much better code and much more rapidly.
- ... what else?

## Raw Transcripts
* [My raw extracted chat thread which captures all the gnarly details of creating this repo is here](etc/chatgpt_convo_extracted_raw.html) (which in total, probably took 5hours over 2 days?).
* **[The reformatted raw html in markdown is here](etc/chatgpt_convo_reformatted.md).**