# Sistemas Avançados de Visão Industrial (SAVI 23-24)
# Grupo 1 - Adriano Figueredo e Bernardo Peixoto, DEM, UA


# import copy
# import csv
# import time
import os
import face_recognition
import cv2
import numpy as np
import math

# def Read_database(patch):
#     names = []
#     encodings = []
#     for file in os.listdir(patch):

#             if file.endswith(".jpg"):
#                 image = face_recognition.load_image_file("Database/" + file)
#                 image_encoding = face_recognition.face_encodings(image)[0]
#                 encodings.append(image_encoding)
#                 names.append(file.rsplit('.', 1)[0].capitalize())


#     return encodings, names, image

# def face_match_perc(face_distance):
#     threshold=0.6
#     range = (1.0 - threshold)
#     linear_val = (1.0 - face_distance) / (range * 2.0)

#     if face_distance > threshold:
#         return linear_val * 100
#     else:
#         value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2)))
#         return value * 100

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


class Detection():
    def __init__(self, image, left, right, top, bottom, id, stamp, name = ''):
        self.left = left*2
        self.right = right*2
        self.top = top*2
        self.bottom = bottom*2
        # self.cx = int((left + right)/2)*2
        # self.cy = int((top + bottom)/2)*2
        self.detection_image = image[self.top:self.bottom, self.left:self.right]
        self.detection_id = id
        self.stamp = stamp
        self.name = name


    def draw(self, image, color):
        start_point = (self.left, self.top)
        end_point = (self.right, self.bottom)
        cv2.rectangle(image, start_point, end_point, color, 2)

        # if text is None:
        #     text = 'Det ' + self.detection_id

        text = 'N: ' + self.name

        #cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        #cv2.rectangle(image, (self.left, self.bottom + 35), (self.right, self.bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(image, text, (self.left + 8, self.top - 35), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)


        # # Draw center of box
        # cv2.line(image, (self.cx, self.cy), (self.cx, self.cy), color, 3) 

    def getLowerMiddlePoint(self):
        return (self.left + int((self.right - self.left)/2) , self.bottom)

class Track():

    # Class constructor
    def __init__(self, name, detection, color=(255, 0, 0)):
        self.track_name = name
        self.color = color
        self.detections = [detection]
        self.active = True
        
        print('Starting constructor for track id ' + str(self.track_name))

    def draw(self, image):

        #Draw only last detection
        self.detections[-1].draw(image, self.color)

        for detection_a, detection_b in zip(self.detections[0:-1], self.detections[1:]):
            start_point = detection_a.getLowerMiddlePoint()
            end_point = detection_b.getLowerMiddlePoint()
            cv2.line(image, start_point, end_point, self.color, 1)

    def track(self, image, video_frame_number, stamp):

        template = self.detections[-1].detection_image
        h,w,_ = template.shape

        print('Track ' + self.track_name + ' running track ...')

        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

        _, _, _, max_loc = cv2.minMaxLoc(result)

        # Convert to Detection convention left, right, top, bottom
        x, y = max_loc
        left = x
        right = int(x + w)
        top = int(y)
        bottom = int(y + h)
        # print('left = ' + str(left))
        # print('right = ' + str(right))
        # print('top = ' + str(top))
        # print('bottom = ' + str(bottom))

        detection_id = 'Tracking ' + str(video_frame_number)
        detection = Detection(left, right, top, bottom, detection_id, stamp, self.track_name)
        self.detections.append(detection) 

    def update(self, detection):
        self.detections.append(detection)


        