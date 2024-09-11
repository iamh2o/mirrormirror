#!/usr/bin/env python3

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