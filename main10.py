# Sistemas Avançados de Visão Industrial (SAVI 23-24)
# Grupo 1 - Adriano Figueredo e Bernardo Peixoto, DEM, UA



import copy
from random import randint
import face_recognition
import cv2
from matplotlib import pyplot as plt
import numpy as np
from track import Detection, Track, computeIOU, Read_database, face_match_perc
import os
import pyttsx3


def main10():

    #-------------------------------------
    #Initialization
    #-------------------------------------

    cap = cv2.VideoCapture(0)

    # Create arrays with face encodings, names, and database information

    Data_Photos = []
    Data_Len = 0
    known_face_encodings = []
    known_face_names = []

    # Read database of saved images and creating names and encodings list

    #known_face_encodings, known_face_names = Read_database('Database')

    if len(os.listdir("Database")) != 0:
        # known_face_encodings, known_face_names, image = Read_database('Database')
        # Data_Photos.append(image)

        for file in os.listdir("Database"):

            if file.endswith(".jpg"):
                image = face_recognition.load_image_file("Database/" + file)
                image_encoding = face_recognition.face_encodings(image)[0]
                known_face_encodings.append(image_encoding)
                known_face_names.append(file.rsplit('.', 1)[0].capitalize())
                Data_Photos.append(image)

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    Greetings = []
    engine = pyttsx3.init()
    video_frame_number = 0

    # --------------------------------------
    # Execution
    # --------------------------------------
    while(cap.isOpened()): # iterate video frames
        
        # Grab a single frame of video
        ret, video = cap.read() # Capture frame-by-frame
        if ret is False:
            break

        frame_stamp = round(float(cap.get(cv2.CAP_PROP_POS_MSEC))/1000,2)
        height, width, _ = video.shape
        image_gui = copy.deepcopy(video) # good practice to have a gui image for drawing

        # ------------------------------------------------------
        # Detect people using Face Recognition
        # ------------------------------------------------------
        # Only process every other frame of video to save time

        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(video, (0, 0), fx=0.5, fy=0.5)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            # rgb_small_frame = small_frame[:, :, ::-1]
            # rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

            rgb_small_frame = cv2.cvtColor(small_frame,cv2.COLOR_BGR2RGB)
            
            # Find all the faces and face encodings in the current frame of video
               
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            Detections = []
            detection_idx = 0
            
            # ----------------------------------------
            # Create list od detections
            # ----------------------------------------

            for top, right, bottom, left in face_locations:
                detection_id = str(video_frame_number) + '_' +  str(detection_idx)
                detection = Detection(top, right, bottom, left, detection_id, frame_stamp)










if __name__ == "__main10__":
    main10()