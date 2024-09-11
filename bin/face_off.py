#!/usr/bin/env python3

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

