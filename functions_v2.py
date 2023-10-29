
from copy import deepcopy
import cv2 as cv
import numpy as np
import face_recognition
import math
import pyttsx3

import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import PhotoImage
from PIL import Image, ImageTk


#Calculates the percentage of matching of the face and the bbox

def face_match_percent(face_distance):
    threshold=0.6
    range = (1.0 - threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > threshold:
        return linear_val * 100
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2)))
        return value * 100

# Class that defines the bounding box created around the face

class BoundingBox:
    
    def __init__(self, x1, y1, w, h):
        self.x1 = x1*2
        self.y1 = y1*2
        self.w = w*2
        self.h = h*2
        self.area = w*2 * h*2

        self.x2 = self.x1 + self.w
        self.y2 = self.y1 + self.h

    # Compares the areas between 2 bounding boxes
    def computeIOU(self, bbox2):
    
        x1_intr = min(self.x1, bbox2.x1)             
        y1_intr = min(self.y1, bbox2.y1)             
        x2_intr = max(self.x2, bbox2.x2)
        y2_intr = max(self.y2, bbox2.y2)

        w_intr = x2_intr - x1_intr
        h_intr = y2_intr - y1_intr
        A_intr = w_intr * h_intr

        A_union = self.area + bbox2.area - A_intr
        
        return A_intr / A_union

    # Extracts just the face from the frame
    def extractSmallImage(self, image_full):
        return image_full[self.y1:self.y1+self.h, self.x1:self.x1+self.w]


# Classifies the bbox as a detection to be then tracked
class Detection(BoundingBox):

    def __init__(self, x1, y1, w, h, image_full, id, stamp, face_encoding, saved_encodings, saved_names, Data_Photos):
        super().__init__(x1,y1,w,h) # call the super class constructor        
        self.id = id
        self.stamp = stamp
        self.image =self.extractSmallImage(image_full)
        #cv.imshow(self.image)
        self.assigned_to_tracker = False

        self.person = 'Unknown'

        if len(saved_encodings) != 0:
        # See if the face is a match for the known faces using the face_recognition library
            found_face = face_recognition.compare_faces(saved_encodings, face_encoding)
            face_distances = face_recognition.face_distance(saved_encodings, face_encoding)
            match_id = np.argmin(face_distances)

            # If it finds a face in frame associate a known name to the detection
            if found_face[match_id]:
                confidence = face_match_percent(face_distances[match_id])
                if confidence > 80:
                    self.person = saved_names[match_id]

        # If the face is unknown ask for a name in the terminal and match the name with the face 
        # encoding of the know face face encodings

            else:
                
                face_rgb = image_full[self.y1 // 2 : (self.y1//2 + self.w //2) , self.x1 //2 : (self.x1//2  + self.h//2)  ]
                face_bgr = cv.cvtColor(face_rgb, cv.COLOR_RGB2BGR)
                cv.imwrite('Database_prov/1.jpg', face_bgr)
                def save_input():
                    global user_input
                    user_input = entry.get()
                    root.destroy()
               #user_input = ""
                root=tk.Tk()
                # Create a Tkinter window to display the face image
                root.title("Face Image")
                face_image = Image.open('Database_prov/1.jpg')
                face_image = ImageTk.PhotoImage(face_image)
                face_label = tk.Label(root, image=face_image)
                face_label.pack()
              
                label = tk.Label(root, text="Enter some text:")
                label.pack()

                entry = tk.Entry(root)
                entry.pack()

                button = tk.Button(root, text="Save and Close", command=save_input)
                button.pack()

                root.mainloop()

                
                #os.remove('Database_prov/1.jpg')
                self.person = str(user_input)
                
                saved_names.append(self.person)
                saved_encodings.append(face_encoding)
                cv.imwrite('Database/' + self.person + '.jpg', face_bgr)
                Data_Photos.append(face_rgb)


        # Write the new person into the database
        else:
            face_rgb = image_full[self.y1 // 2 : (self.y1//2 + self.w //2) , self.x1 //2 : (self.x1//2  + self.h//2)  ]
            face_bgr = cv.cvtColor(face_rgb, cv.COLOR_RGB2BGR)
            cv.imwrite('Database_prov/1.jpg', face_bgr)
            def save_input():
                global user_input
                user_input = entry.get()
                root.destroy()
            #user_input = ""
            root=tk.Tk()
            # Create a Tkinter window to display the face image
            root.title("Face Image")
            face_image = Image.open('Database_prov/1.jpg')
            face_image = ImageTk.PhotoImage(face_image)
            face_label = tk.Label(root, image=face_image)
            face_label.pack()
            
            label = tk.Label(root, text="Enter some text:")
            label.pack()

            entry = tk.Entry(root)
            entry.pack()

            button = tk.Button(root, text="Save and Close", command=save_input)
            button.pack()

            root.mainloop()

            #os.remove('Database_prov/1.jpg')
            self.person = str(user_input)
            saved_names.append(self.person)
            saved_encodings.append(face_encoding)
            cv.imwrite('Database/' + self.person + '.jpg', face_bgr)
            Data_Photos.append(face_rgb)


    def draw(self, image_gui, color=(255,0,0)):

        
        cv.putText(image_gui, 'd' , (self.x1, self.y1-5), cv.FONT_HERSHEY_SIMPLEX, 
                        1, color, 2, cv.LINE_AA)
        
    def getLowerMiddlePoint(self):
        return (self.x1 + int((self.x1 - self.x1 + self.w)/2) , int(self.y1 + self.h))


# Classifies the trackers using the detections using a CSRT tracker embedder in opencv
class Tracker():

    def __init__(self, detection, id, image, person):
        self.id = id
        self.active = True
        self.bboxes = []
        self.detections = []
        self.tracker = cv.TrackerCSRT_create()
        self.time_since_last_detection = None
        self.person = person

        self.addDetection(detection, image)

    # Says hello to the person associated with a new tracker
        engine = pyttsx3.init()
        engine.say("Hello" + self.person)
        engine.runAndWait()
        engine.stop()

    # Gets the time of the last detection
    def getLastDetectionStamp(self):
        return self.detections[-1].stamp

    def updateTime(self, stamp):
        self.time_since_last_detection = round(stamp-self.getLastDetectionStamp(),1)

        if self.time_since_last_detection > 2:        
            self.active = False

    # Draws on the video a bbox, the person's name and the time since the last detection
    def draw(self, image_gui, color=(255,0,255)):

        bbox = self.bboxes[-1] # get last bounding box

        for detection_a, detection_b in zip(self.detections[0:-1], self.detections[1:]):
            start_point = detection_a.getLowerMiddlePoint()
            end_point = detection_b.getLowerMiddlePoint()
            cv.line(image_gui, start_point, end_point, color, 1) 

        cv.rectangle(image_gui,(bbox.x1,bbox.y1),(bbox.x2, bbox.y2),color,3)

        cv.putText(image_gui, str(self.person) + ' T' + str(self.id), 
                            (bbox.x1+25, bbox.y1-5), cv.FONT_HERSHEY_SIMPLEX, 
                        1, color, 2, cv.LINE_AA)

        cv.putText(image_gui, str(self.time_since_last_detection) + ' s', 
                            (bbox.x1, bbox.y1-30), cv.FONT_HERSHEY_SIMPLEX, 
                        1, color, 2, cv.LINE_AA)

    # Adds a new detection to the detection list
    def addDetection(self, detection, image):

        self.tracker.init(image, (detection.x1//2, detection.y1//2, detection.w//2, detection.h//2))  # alteração aqui

        self.detections.append(detection)
        detection.assigned_to_tracker = True
        self.template = detection.image
        bbox = BoundingBox(detection.x1 // 2, detection.y1 // 2, detection. w// 2, detection.h // 2)
        self.bboxes.append(bbox)

    # Updates the tracker and attaches the bounding box to the list
    def track(self, image):

        ret, bbox = self.tracker.update(image)
        x1,y1,w,h = bbox


        bbox = BoundingBox(x1, y1, w, h)
        self.bboxes.append(bbox)