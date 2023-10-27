# Sistemas Avançados de Visão Industrial (SAVI 23-24)
# Grupo 1 - Adriano Figueredo e Bernardo Peixoto, DEM, UA



import copy
from random import randint
import face_recognition
import cv2
from matplotlib import pyplot as plt
import numpy as np
from track_v3 import Detection, Track, computeIOU
import os
import pyttsx3


def main():

    # --------------------------------------
    # Initialization
    # --------------------------------------
    cap = cv2.VideoCapture(0)

    # Create arrays with face encodings, names, and database information

    Data_Photos = []
    Data_Len = 0
    Encodings_known = []
    Names_known = []


    # Read database of saved images and creating names and encodings list

    #known_face_encodings, known_face_names = Read_database('Database')

    if len(os.listdir("Database")) != 0:
        # known_face_encodings, known_face_names, image = Read_database('Database')
        # Data_Photos.append(image)

        for file in os.listdir("Database"):

            if file.endswith(".jpg"):
                person_face = face_recognition.load_image_file("Database/" + file)
                image_encoding = face_recognition.face_encodings(person_face)[0]
                Encodings_known.append(image_encoding)
                Names_known.append(file.rsplit('.', 1)[0].capitalize())
                Data_Photos.append(person_face)


    # Initialize some variables
    Greetings = []
    face_locations = []
    face_encodings = []
    face_names = []
    video_frame_number = 0
    process_this_frame = True  
    engine = pyttsx3.init()

    # Parameters
    distance_threshold = 100
    deactivate_threshold = 5.0 # secs
    iou_threshold = 0.3


    person_count = 0
    tracks = []

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
            
            # print(face_locations)
            # print(face_encodings)


            for idx, face_encoding in enumerate(face_encodings):
                # See if the face is a match for the known face(s)
                if len(Encodings_known) != 0:
                    matches = face_recognition.compare_faces(Encodings_known, face_encoding)
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                if len(Encodings_known) != 0:
                    face_distances = face_recognition.face_distance(Encodings_known, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = Names_known[best_match_index]
                        # confidence = face_match_perc(face_distances[best_match_index])  #escrever isto na imagem
                        if name not in Greetings:
                            engine.say("Hello " + name)
                            engine.runAndWait()
                            Greetings.append(name)
                face_names.append(name)

                if name.lower() == "unknown":
                    engine.say('Hello! Who are you?')
                    engine.runAndWait()
                    name = input("What is your name? ")
                    engine.say("Hello " + name)
                    engine.runAndWait()
                    Greetings.append(name)
                    cv2.imwrite("Database/" + name.lower() + ".jpg", small_frame[face_locations[idx][0]-30:face_locations[idx][2]+30, face_locations[idx][3]-30:face_locations[idx][1]+30])
                    person_face = face_recognition.load_image_file("Database/" + name.lower() + ".jpg")
                    image_encoding = face_recognition.face_encodings(person_face)[0]
                    Encodings_known.append(image_encoding)
                    Names_known.append(name)
                    Data_Photos.append(person_face)


                    face_names.append(name)
                

        process_this_frame = not process_this_frame

        # ------------------------------------------------------
        # Create list of detections
        # ------------------------------------------------------
        detections = []
        detection_idx = 0
        #video_gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)

        for top, right, bottom, left in face_locations:
            name = face_names[detection_idx]
            detection_id = str(video_frame_number) + '_' +  str(detection_idx)
            detection = Detection(video,left, right, top, bottom, detection_id, frame_stamp, name)
            detections.append(detection)
            detection_idx += 1

        all_detections = copy.deepcopy(detections)

        #------------------------------------------------------
        #Association step. Associate detections with tracks
        #------------------------------------------------------

        idxs_detections_to_remove = []
        for idx_detection, detection in enumerate(detections):
            for track in tracks:
                if not track.active:
                    continue
                # track.update(detection)  # add detection to track
                # idxs_detections_to_remove.append(idx_detection)
                
                # --------------------------------------
                # Using IOU
                # --------------------------------------
                iou = computeIOU(detection, track.detections[-1])
                print('IOU( ' + detection.detection_id + ' , ' + track.track_name + ') = ' + str(iou))
                if iou > iou_threshold: # This detection belongs to this tracker!!!
                    track.update(detection) # add detection to track
                    idxs_detections_to_remove.append(idx_detection)
                    break # do not test this detection with any other track

        idxs_detections_to_remove.reverse()

        # print('idxs_detections_to_remove ' + str(idxs_detections_to_remove))

        for idx in idxs_detections_to_remove:

            del detections[idx]

        # --------------------------------------
        # Find existing trackers that did not have an associated detection in this frame
        # --------------------------------------

        for track in tracks:

            if track.detections[-1].stamp == frame_stamp:
                print('Track ' + str(track.track_name) + ' has detection ' + track.detections[-1].detection_id 
                     + ' associated in this frame')
            else:
                print('Track ' + str(track.track_name) + ' does not have an associated detection in this frame')
                # This is the tracking part
                track.track(video, video_frame_number, frame_stamp)

        # --------------------------------------
        # Create new trackers
        # --------------------------------------

        for detection in detections:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
            track = Track(name, detection, color=color)
            tracks.append(track)
            person_count += 1

        # --------------------------------------
        # Deactivate tracks if last detection has been seen a long time ago
        # --------------------------------------
        for track in tracks:
            time_since_last_detection = frame_stamp - track.detections[-1].stamp
            if time_since_last_detection > deactivate_threshold:
                track.active = False
               
        #--------------------------------------
        # Visualization
        #--------------------------------------
        
        # Draw list of all detections (including those associated with the tracks)
        for detection in all_detections:
            detection.draw(image_gui, color)


        #Draw list of tracks

        for track in tracks:
            if not track.active:
                continue
            track.draw(image_gui)

        # Show Database if was someone added

        if len(Data_Photos) != 0:
            #print('Há foto')
            if Data_Len < len(Data_Photos):
                #print('+1')
                #cv2.namedWindow('Database', cv2.WINDOW_NORMAL)
                fig = plt.figure('DataBase', figsize=(10, 7), clear = True)
                rows = len(Data_Photos)
                columns = 1

                for idx_photo, photo in enumerate(Data_Photos):
                    fig = plt.figure('DataBase', figsize=(10, 7), clear = False)
                    fig.add_subplot(rows, columns, idx_photo + 1)
                    plt.imshow(photo)
                    plt.axis('off')
                    plt.title(Names_known[idx_photo])
                    plt.tight_layout()   # Positions photos more aesthetics
                plt.draw()
                key = plt.waitforbuttonpress(0.01)


        if video_frame_number == 0:
            cv2.namedWindow('GUI',cv2.WINDOW_NORMAL)
            cv2.resizeWindow('GUI', int(width), int(height))

        # Add frame number and time to top left corner
        cv2.putText(image_gui, 'Frame ' + str(video_frame_number) + ' Time ' + str(frame_stamp) + ' secs',
                    (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)

        # Display the resulting image
        cv2.imshow('GUI',image_gui)
        Data_Len = len(Data_Photos)

        
        # Hit 'q' on the keyboard to quit
        if cv2.waitKey(1) & 0xFF == ord('q') :
            break

        video_frame_number += 1

    
if __name__ == "__main__":
    main()