#!/usr/bin/env python3
# Sistemas Avançados de Visão Industrial (SAVI 23-24)
# Grupo 1 - Adriano Figueredo e Bernardo Peixoto, DEM, UA

import cv2 as cv
import numpy as np
from copy import deepcopy
from functions_v2 import Detection, Tracker
import face_recognition
import os
from matplotlib import pyplot as plt
from random import randint

#----------------------------------
#--------Inititalization-----------
#----------------------------------  

# Read Database of saved images and creating names and encodings list

print('Welcome to this program!\n')
option = input("If you want to start with an empty Database press '1'\n If you want to start with the existing database press 2.\n Option: ")
option = str(option)
path = "Database"

# Initialize some variables
saved_face_names = []
saved_face_encodings = []
Data_Photos = []
Data_Len = 0
face_locations = []
face_encodings = []
detection_counter = 0
tracker_counter = 0
trackers = []
iou_threshold = 0.5 
names = []
frame_counter = 0
process_this_frame = True

if option == '1':
    if len(os.listdir('Database')) != 0:
         
        if os.path.exists(path):
            # List all files in folder
            ficheiros = os.listdir(path)
        
            # Percorrer a lista de ficheiros e eliminar cada um
            for ficheiro in ficheiros:
                caminho_completo = os.path.join(path, ficheiro)
                # Verificar se o caminho completo é um ficheiro (não é uma pasta)
                if os.path.isfile(caminho_completo):
                    os.remove(caminho_completo)
        
    print('Starting the program with empty Database ...')
	
else:
	try:
		if len(os.listdir('Database')) != 0:
			
			for photo in os.listdir(path):
				face_image = face_recognition.load_image_file(path + f'/{photo}')
				face_encoding = face_recognition.face_encodings(face_image)[0]
				name, extention = photo.split('.')
				saved_face_names.append(name)
				saved_face_encodings.append(face_encoding)
				Data_Photos.append(face_image)
                    
	except Exception as e:
		print(f"Error loading database: {e}")
    
	print('Starting the program ...')

#---------------------------------
#-----------Execution-------------
#---------------------------------
    
cap = cv.VideoCapture(0)

while True:
    # Get the frame
    ret, video = cap.read()
    frame = cv.flip(video, 1)

    if ret == False:
        break

    frame_counter +=1
    height, width, _ = frame.shape
    image_gui = deepcopy(frame) # good practice to have a gui image for drawing
    stamp = float(cap.get(cv.CAP_PROP_POS_MSEC))/1000

# --------------------------------------
# -Detect people usign Face Recognition-
# --------------------------------------

    if process_this_frame:
        # Resize frame of video to 1/2 size for faster face recognition processing
        small_frame = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)   

        # Convert form bgr to rgb for the face recognition library
        image_rgb_small = cv.cvtColor(small_frame, cv.COLOR_BGR2RGB)
        
        # face_recognition tool usage to find a face 
        face_locations = face_recognition.face_locations(image_rgb_small)
        face_encodings = face_recognition.face_encodings(image_rgb_small, face_locations)

        # Creates a Detection class and connects it with a face
        detections = []
        face_names = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            w = right-left
            h = bottom-top
            x1 = left
            y1 = top
            detection = Detection(x1, y1, w, h, image_rgb_small, id=detection_counter, stamp=stamp, face_encoding=face_encoding, saved_encodings = saved_face_encodings, saved_names = saved_face_names, Data_Photos = Data_Photos)
            detection_counter += 1
            #detection.draw(image_gui)
            detections.append(detection)

        # Detection to tracker evaluation and association
        for detection in detections: 
            for tracker in trackers: 
                if tracker.active:
                    tracker_bbox = tracker.detections[-1]
                    iou = detection.computeIOU(tracker_bbox)

                    if iou > iou_threshold:  
                        tracker.addDetection(detection, image_rgb_small)

        # Track using template matching
        for tracker in trackers:
            last_detection_id = tracker.detections[-1].id
            detection_ids = [d.id for d in detections]
            
            if not last_detection_id in detection_ids:
                tracker.track(image_rgb_small)

        # Deactivate Tracker if it doesn't detect for two seconds
        for tracker in trackers: 
            tracker.updateTime(stamp)

        # Create a Tracker class for each detection
        for detection in detections:
            if not detection.assigned_to_tracker:
                color = (randint(0, 255), randint(0, 255), randint(0, 255))
                tracker = Tracker(detection, id=tracker_counter, image=image_rgb_small, person = detection.person, color=color)
                tracker_counter += 1
                trackers.append(tracker)

    process_this_frame = not process_this_frame

    # ------------------------------------------
    # -------------Draw stuff-------------------
    # ------------------------------------------

    # Draw trackers
    for tracker in trackers:
        if tracker.active:
            tracker.draw(image_gui)

# Show Database if was someone added
    if len(Data_Photos) != 0:
        if Data_Len < len(Data_Photos):
            print('+1')
            fig = plt.figure('DataBase', figsize=(10, 7), clear = True)
            rows = len(Data_Photos)
            columns = 1

            for idx_photo, face_photo in enumerate(Data_Photos):
                fig = plt.figure('DataBase', figsize=(10, 7), clear = False)
                fig.add_subplot(rows, columns, idx_photo + 1)
                plt.imshow(face_photo)
                plt.axis('off')
                plt.title(saved_face_names[idx_photo])
                plt.tight_layout()   # Positions photos more aesthetics
            plt.draw()
            key = plt.waitforbuttonpress(0.01)

    # Show image in window    
    cv.imshow('Face Cam Detector',image_gui) # show the image
    Data_Len = len(Data_Photos)

    if cv.waitKey(50) == ord('q'):
        break

    frame_counter += 1

# ------------------------------------------
# ------------Termination-------------------
# ------------------------------------------
cap.release()
cv.destroyAllWindows()