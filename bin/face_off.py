#!/usr/bin/env python3

import cv2
import time
import os
from pynput import keyboard
import threading
import face_recognition
import pickle
from pystray import Icon, MenuItem as item, Menu
from PIL import Image

# Load your face encoding
print("Loading face encoding...")
with open('your_face_encoding.pkl', 'rb') as f:
    my_face_encoding = pickle.load(f)

next_check_time = 5  # seconds
enabled = False  # Start disabled by default
exit_event = False  # Event to signal app termination
facecheck_running = False  # To track if face recognition is running

selected_camera = 0  # Automatically select the FaceTime camera (usually index 0)

# Function to start face recognition
def start_face_recognition():
    global facecheck_running
    facecheck_running = True
    rebuild_menu()  # Disable the toggle and quit menu while face recognition is running

    try:
        print(f"Starting face recognition on camera {selected_camera}...")
        cap = cv2.VideoCapture(selected_camera)  # Open the default webcam (FaceTime camera)

        if not cap.isOpened():
            print(f"Error: Could not open camera {selected_camera}.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while enabled and not exit_event:
            print("Reading from webcam...")
            ret, frame = cap.read()

            if not ret:
                print("Failed to capture frame. Retrying...")
                time.sleep(1)
                continue

            # Convert frame from BGR to RGB for face_recognition
            rgb_frame = frame[:, :, ::-1]

            # Detect face locations and encode faces in the frame
            face_encodings = face_recognition.face_encodings(frame)

            print(f"Found {len(face_encodings)} face encodings in frame.")
            face_recognized = False
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces([my_face_encoding], face_encoding, tolerance=0.65)
                if matches[0]:
                    print("Your face is recognized.")
                    face_recognized = True
                    break

            if not face_recognized:
                print("Your face is not recognized!")
                print("Your face is not detected. Locking screen immediately")
                lock_screen()
                break

            print(f"Waiting for {next_check_time} sec before next check... be sure you are in front of the camera.")
            time.sleep(next_check_time)

    except cv2.error as e:
        print(f"OpenCV error: {e}")
    except Exception as e:
        print(f"General error in face recognition: {e}")
    finally:
        facecheck_running = False
        icon.icon = Image.open("icons/fo_disabled.png")
        icon.title = "Face Off: Disabled"
        icon.visible = False
        icon.visible = True
        print("Releasing webcam...")
        cap.release()
        rebuild_menu()  # Enable the toggle and quit menu after face recognition stops

# Function to toggle face recognition on or off
def toggle_face_recognition():
    global enabled
    if facecheck_running:
        print("Face recognition is currently running, cannot disable until it finishes.")
        return

    enabled = not enabled
    update_icon()  # Immediately update the icon before starting the recognition
    rebuild_menu()  # Rebuild the menu to update the toggle label

    if enabled:
        print("Face recognition enabled.")
        # Run face recognition in a separate thread to avoid blocking the UI
        threading.Thread(target=start_face_recognition, daemon=True).start()
    else:
        print("Face recognition disabled.")

# Function to lock the screen
def lock_screen():
    print("Locking the screen...")
    os.system("osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")

# Function to update the menu bar icon when the state changes
def update_icon():
    if enabled:
        icon.icon = Image.open("icons/fo_enabled.png")
        icon.title = "Face Off: Enabled"
    else:
        icon.icon = Image.open("icons/fo_disabled.png")
        icon.title = "Face Off: Disabled"

    # Force refresh by toggling visibility
    if icon.visible:
        icon.visible = False
        icon.visible = True

# Function to rebuild the menu dynamically
def rebuild_menu():
    label = 'Disable Face Off' if enabled else 'Enable Face Off'
    if facecheck_running:
        menu = Menu(
            item(label, toggle_face_recognition, enabled=False),  # Disable menu item while running
            item('Quit', quit_app, enabled=False)  # Disable Quit while running
        )
    else:
        menu = Menu(
            item(label, toggle_face_recognition),  # Enable after re-authentication
            item('Quit', quit_app)
        )
    icon.menu = menu

# Function to quit the app
def quit_app(icon, item):
    if facecheck_running:
        print("Cannot quit the application while face recognition is running.")
        return
    print("Quitting the application...")
    global exit_event
    exit_event = True
    icon.stop()

# Set up pystray for the menu bar icon
def setup_icon():
    global icon
    menu = Menu(
        item('Enable Face Off', toggle_face_recognition),  # Initial label is 'Enable Face Off'
        item('Quit', quit_app)
    )
    icon = Icon("Face Off", Image.open("icons/fo_disabled.png"), menu=menu)
    icon.run()

# Hotkey handler using pynput
def on_press(key):
    try:
        if key == keyboard.HotKey([keyboard.Key.cmd, keyboard.Key.shift], 'x'):
            toggle_face_recognition()
    except AttributeError:
        pass

# Set up listener for hotkeys in a separate thread
def listen_hotkey():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Run the menu bar icon on the main thread
setup_icon()

# Start hotkey listener in a separate thread
hotkey_thread = threading.Thread(target=listen_hotkey, daemon=True)
hotkey_thread.start()

# Keep the script running until exit_event is set
while not exit_event:
    time.sleep(1)

print("Application has exited.")
