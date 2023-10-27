

# Sistemas Avançados de Visão Industrial (SAVI 23-24)
# Grupo 1 - Adriano Figueredo e Bernardo Peixoto, DEM, UA


# import copy
# import csv
# import time
import math
import os
import face_recognition
import cv2
import numpy as np

def Read_database(patch):
    names = []
    encodings = []
    for file in os.listdir(patch):

            if file.endswith(".jpg"):
                image = face_recognition.load_image_file("Database/" + file)
                image_encoding = face_recognition.face_encodings(image)[0]
                encodings.append(image_encoding)
                names.append(file.rsplit('.', 1)[0].capitalize())


    return encodings, names, image

def face_match_percent(face_distance):
    threshold=0.6
    range = (1.0 - threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > threshold:
        return linear_val * 100
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2)))
        return value * 100

def computeIOU(d1, d2):
    # box1 and box2 should be in the format (x1, y1, x2, y2)
    x1_1, y1_1, x2_1, y2_1 = d1.left, d1.top, d1.right, d1.bottom
    x1_2, y1_2, x2_2, y2_2 = d2.left, d2.top, d2.right, d2.bottom
    
    # Calculate the area of the first bounding box
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    
    # Calculate the area of the second bounding box
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    # Calculate the coordinates of the intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    # Check if there is an intersection
    if x1_i < x2_i and y1_i < y2_i:
        # Calculate the area of the intersection
        area_i = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate the area of the union
        area_u = area1 + area2 - area_i
        
        # Calculate IoU
        iou = area_i / area_u
        return iou
    else:
        return 0.0

class BoundingBox:
    
    def __init__(self, x1, y1, w, h):
        self.x1 = x1
        self.y1 = y1
        self.w = w
        self.h = h
        self.area = w * h

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




class Detection(BoundingBox):
     
    def __init__(self, x1, y1, w, h, image_full, id, stamp, face_encoding, our_faces, our_names):
        super().__init__(x1,y1,w,h) # call the super class constructor        
        self.id = id
        self.stamp = stamp
        self.image =self.extractSmallImage(image_full)
        self.assigned_to_tracker = False

        # See if the face is a match for the known faces using the face_recognition library
        found_face = face_recognition.compare_faces(our_faces, face_encoding)
        face_distances = face_recognition.face_distance(our_faces, face_encoding)
        match_id = np.argmin(face_distances)

        # If it finds a face in frame associate a known name to the detection
        if found_face[match_id]:
            confidence = face_match_percent(face_distances[match_id])
            if confidence > 80:
                self.person = our_names[match_id]

        # If the face is unknown ask for a name in the terminal and match the name with the face 
        # encoding of the know face face encodings
            else:
                person = input('Hello what s your name?')
                self.person = str(person)
                our_names.append(person)
                our_faces.append(face_encoding)

        # Write the new person into the database
        else:
            name = input('Hello what s your name?')
            self.name = str(name)
            our_names.append(person)
            our_faces.append(face_encoding)
            cv2.imwrite("Database/" + self.name.lower() + ".jpg", image_full[self.y1:self.y1+self.h, self.x1:self.x1+self.w])

    def draw(self, image_gui, color=(255,0,0)):
        image = cv2.putText(image_gui, 'd' , (self.x1, self.y1-5), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, color, 2, cv2.LINE_AA)


class Track():

    # Class constructor
    def __init__(self, id, detection,  color=(255, 0, 0)):
        self.track_id = id
        self.color = color
        self.detections = [detection]
        self.active = True

        print('Starting constructor for track id ' + str(self.track_id))

    def draw(self, image):

        #Draw only last detection
        self.detections[-1].draw(image, self.color, text=self.track_id, draw_position='top')

        for detection_a, detection_b in zip(self.detections[0:-1], self.detections[1:]):
            start_point = detection_a.getLowerMiddlePoint()
            end_point = detection_b.getLowerMiddlePoint()
            cv2.line(image, start_point, end_point, self.color, 1) 


    def update(self, detection):
        self.detections.append(detection)