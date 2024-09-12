
import face_recognition
import cv2
import pickle

# Open webcam
cap = cv2.VideoCapture(0)

# Set a higher resolution for better face detection
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Look at the camera to capture your face... HIT 'q' TO CAPTURE")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Display the frame to ensure the camera is working
    cv2.imshow('Frame', frame)

    # Press 'q' to take a snapshot and process the frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Capturing frame...")
        break

# Destroy the preview window after capturing
cv2.destroyAllWindows()

# Convert frame from BGR (OpenCV format) to RGB (face_recognition format)
rgb_frame = frame[:, :, ::-1]

# Directly calculate face encodings without manually passing face locations
try:
    print("Generating face encoding...")    
    # Let face_recognition automatically detect faces and generate encodings
    face_encodings = face_recognition.face_encodings(frame)

    if face_encodings:
        print("Face encoding generated successfully!")

        # Save the face encoding to a file
        with open('your_face_encoding.pkl', 'wb') as f:
            pickle.dump(face_encodings[0], f)
        print("Face encoding saved successfully!")
    else:
        print("No face detected or unable to generate face encoding.")

except Exception as e:
    print(f"Error during face encoding: {e}")

cap.release()
