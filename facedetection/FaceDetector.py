import cv2
import numpy as np
import os

class FaceDetector:
    print(__file__)
    face_cascade = cv2.CascadeClassifier(os.path.dirname(__file__)+'/haarcascade_frontalface_default.xml')

    def detect_faces(self, image):
        # Convert image to grayscale (required for face detection)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Load pre-trained face detector (Haar cascade)


        # Detect faces in the image
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(75, 75))

        # If no faces are detected, return an empty list
        if len(faces) == 0:
            return []

        # Extract the bounding box coordinates of each detected face
        detected_faces = []
        for (x, y, w, h) in faces:
            detected_faces.append((x, y, x + w, y + h))  # (left, top, right, bottom)

        return detected_faces

if __name__ == '__main__':
    
    image_path = 'sample.webp'
    image = cv2.imread(image_path)
    print(f"{np.shape(image)}")
    input()

    # Ensure the image was properly loaded
    if image is None:
        print(f"Error: Unable to load image from {image_path}")
    else:
        # Detect faces in the image
        detector = FaceDetector()
        detected_faces = detector.detect_faces(image)

        # Draw rectangles around the detected faces
        for (left, top, right, bottom) in detected_faces:
            # cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)  # Green rectangle
            print(left, top, right, bottom)

