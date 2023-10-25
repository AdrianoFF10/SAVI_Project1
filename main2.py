import copy
import face_recognition
import cv2
from random import randint
from matplotlib import pyplot as plt
import numpy as np
import os
import pyttsx3
from track import Detection, Track, computeIOU

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.Data_Photos = []
        self.Data_Len = 0
        self.process_this_frame = True
        self.hellos = []
        self.engine = pyttsx3.init()

    def add_known_face(self, name, image):
        image_encoding = face_recognition.face_encodings(image)[0]
        self.known_face_encodings.append(image_encoding)
        self.known_face_names.append(name)
        self.Data_Photos.append(image)

class FaceRecognitionApp:
    def __init__(self, system):
        self.system = system
        self.cap = cv2.VideoCapture(0)
        self.video_frame_number = 0
        self.person_count = 0
        self.tracks = []

    def start(self):
        while self.cap.isOpened():
            result, image_rgb = self.cap.read()
            if result is False:
                break

            frame_stamp = round(float(self.cap.get(cv2.CAP_PROP_POS_MSEC)) / 1000, 2)
            height, width, _ = image_rgb.shape
            image_gui = copy.deepcopy(image_rgb)

            # Detect people using Face Recognition
            if self.system.process_this_frame:
                small_frame = cv2.resize(image_rgb, (0, 0), fx=0.5, fy=0.5)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []

                for idx, face_encoding in enumerate(face_encodings):
                    if len(self.system.known_face_encodings) != 0:
                        matches = face_recognition.compare_faces(self.system.known_face_encodings, face_encoding)
                    name = "Unknown"

                    if len(self.system.known_face_encodings) != 0:
                        face_distances = face_recognition.face_distance(self.system.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.system.known_face_names[best_match_index]
                            if name not in self.system.hellos:
                                self.system.engine.setProperty('rate', 100) 
                                self.system.engine.setProperty('voice', 'portugal') 
                                self.system.engine.say("Olá " + name)
                                self.system.engine.runAndWait()
                                self.system.hellos.append(name)
                    face_names.append(name)

                    if name.lower() == "unknown":
                        name = input("What is your name? ")
                        self.system.engine.setProperty('rate', 100) 
                        self.system.engine.setProperty('voice', 'portugal') 
                        self.system.engine.say("Olá " + name)
                        self.system.engine.runAndWait()
                        self.system.hellos.append(name)
                        cv2.imwrite("Database/" + name.lower() + ".jpg", small_frame[face_locations[idx][0] - 30:face_locations[idx][2] + 30, face_locations[idx][3] - 30:face_locations[idx][1] + 30])
                        image = face_recognition.load_image_file("Database/" + name.lower() + ".jpg")
                        image_encoding = face_recognition.face_encodings(image)[0]
                        self.system.known_face_encodings.append(image_encoding)
                        self.system.known_face_names.append(name)
                        self.system.Data_Photos.append(image)
                        face_names.append(name)

                # Create list of detections
                detections = []
                detection_idx = 0
                for top, right, bottom, left in face_locations:
                    name = face_names[detection_idx]
                    detection_id = str(self.video_frame_number) + '_' + str(detection_idx)
                    detection = Detection(left, right, top, bottom, detection_id, frame_stamp, name)
                    detections.append(detection)
                    detection_idx += 1

                all_detections = copy.deepcopy(detections)

                # Visualization
                for detection in all_detections:
                    detection.draw(image_gui, (255, 0, 0))
                if len(self.system.Data_Photos) != 0:
                    if self.system.Data_Len < len(self.system.Data_Photos):
                        fig = plt.figure('DataBase', figsize=(10, 7), clear=True)
                        rows = len(self.system.Data_Photos)
                        columns = 1

                        for idx_photo, photo in enumerate(self.system.Data_Photos):
                            fig = plt.figure('DataBase', figsize=(10, 7), clear=False)
                            fig.add_subplot(rows, columns, idx_photo + 1)
                            plt.imshow(photo)
                            plt.axis('off')
                            plt.title(self.system.known_face_names[idx_photo])
                            plt.tight_layout()
                        plt.draw()
                        key = plt.waitforbuttonpress(0.01)

                if self.video_frame_number == 0:
                    cv2.namedWindow('GUI', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('GUI', int(width), int(height))

                cv2.putText(image_gui, 'Frame ' + str(self.video_frame_number) + ' Time ' + str(frame_stamp) + ' secs',
                            (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                cv2.imshow('GUI', image_gui)
                self.system.Data_Len = len(self.system.Data_Photos)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                self.video_frame_number += 1

class FaceRecognitionSystemApp:
    def __init__(self):
        self.system = FaceRecognitionSystem()
        self.app = FaceRecognitionApp(self.system)
    def run(self):
        self.app.start()

if __name__ == "__main__":
    app = FaceRecognitionSystemApp()
    app.run()
