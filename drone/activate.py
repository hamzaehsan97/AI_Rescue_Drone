from djitellopy import Tello
import faceEncodings
import knownFaces
import cv2
import pygame
from pygame.locals import *
import numpy as np
import time
import math
import datetime
import json
import requests
import face_recognition
import sqlite3
import pathlib

S = 35
FPS = 30

#OLD CLASSIFIER
face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml' )

horizontal_distance_face = 70
face_null_timer = 0
flight_control_bool = True


# Tasks list. 
class FrontEnd(object):
   

    def __init__(self):
        
        pygame.init()

       
        pygame.display.set_caption("Rescue Feed")
        self.screen = pygame.display.set_mode([960, 720])

       
        self.tello = Tello()

        self.auto = False
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10
        self.battery = 0
        
        

        self.send_rc_control = False

        
        pygame.time.set_timer(USEREVENT + 1, 50)

    def run(self):

        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return

        
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return

        #Read incoming from from tello
        frame_read = self.tello.get_frame_read()

        should_stop = False
        
        #create image encodings array
        image_encodings_array = []

        #create image labels array 
        known_faces_labels = []

        #Get path to img folder for extraction
        image_directory = pathlib.Path('/Users/hamzaehsan/Desktop/drone/drone/img/upload')

        for image in image_directory.iterdir():

            #create instances of faceEncoding and knonFacesLabels class
            face_encoder = faceEncodings.faceEncoding(image)
            face_labels = knownFaces.knownFacesLabels(image.name)

            #Encode faces into numpy arrays, get image labels(names)
            face_encoded = face_encoder.face_encoding
            image_label = face_labels.label

            #Append to respective arrays
            image_encodings_array.append(face_encoded)
            known_faces_labels.append(image_label)

        face_locations = []
        face_encodings = []
        process_frame = True
        
        

        #Update, Emergency quit, Esc quit, event key, frame read failure 
        while not should_stop:

            for event in pygame.event.get():
                if event.type == USEREVENT + 1:
                    self.update()
                elif event.type == QUIT:
                    should_stop = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == KEYUP:
                    self.keyup(event.key)


            if frame_read.stopped:
                frame_read.stop()
                break

           

            
            self.screen.fill([0, 0, 0])

            frame = frame_read.frame

            #Increase processing speeds by reducing frame size to 1/4 size. Tune this variable based on drone camera quality for prime accuracy.
            reduced_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)

            #Convert frame to BGR colors to RGB for face_recognition library
            rgb_frame = cv2.cvtColor(reduced_frame, cv2.COLOR_BGR2RGB)





               
            
            if process_frame == True:

                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                
                face_labels=[]
                for encoding in face_encodings:

                    matches = face_recognition.compare_faces(image_encodings_array, encoding)
                    name = "unknown"

                    distance = face_recognition.face_distance(image_encodings_array, encoding)
                    best_match = np.argmin(distance)

                    if matches[best_match]:
                        name = known_faces_labels[best_match]
                    
                    face_labels.append(name)
            
            process_frame = not process_frame

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_labels):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

           
            
            #Get drone battery information
            self.battery = self.tello.get_battery()  
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            #Add flight information to the frame
            frame = self.info(frame)
            #Add frame to the pygame surface
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            print(self.tello.get_battery())
            #Update the screen
            pygame.display.update()
            
            #Wait for next frame to come in before repeating the for statement
            time.sleep(1 / FPS)
        #End the process before exiting
        self.tello.end()


    
    def info(self,frame):

        class Hud():
            def __init__(self,selfColor=(255,255,255)):
                self.selfColor = selfColor
                self.infos = []
            def add(self,info, color=None):
                if color == None: color = self.selfColor
                self.infos.append((info,color))
            def draw(self, frame):
                i=0
                # for (info,color) in self.infos:
                #     cv2.putText(frame,info,(0,30+(i*30)),cv2.FONT_HERSHEY_COMPLEX,10
                #     ,color,thickness=10)
                #     i+=1
        
        hud = Hud()

        if self.battery:
             hud.add(f"BAT {self.battery}")
        
        hud.add(f"Battery")

        hud.draw(frame)

        return frame





    def keydown(self, key):
        
        if key == pygame.K_UP:  # forward
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # backward
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # left
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  #right
            self.left_right_velocity = S
        elif key == pygame.K_w:  # up
            self.up_down_velocity = S
        elif key == pygame.K_s:  # down
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # clockwise
            self.yaw_velocity = -2*S
        elif key == pygame.K_d:  # anti-clockwise
            self.yaw_velocity = 2*S
        elif key == pygame.K_p:  # anti-clockwise
            self.auto = True
        elif key == pygame.K_m:  # anti-clockwise
            self.yaw_velocity = 0
            self.for_back_velocity = 0
            self.left_right_velocity = 0
            self.up_down_velocity = 0
            self.auto = False


    def keyup(self, key):
        
        if key == pygame.K_UP or key == pygame.K_DOWN:  
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  
            self.yaw_velocity = 0
        elif key == pygame.K_t: 
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  
            self.tello.land()
            self.send_rc_control = False
        elif key == pygame.K_m:
            self.yaw_velocity = 0
            self.for_back_velocity = 0
            self.left_right_velocity = 0
            self.up_down_velocity = 0
            self.auto = False

    def update(self):
        # Send updates
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)

    def videofeed(self):
        frame_read = self.tello.get_frame_read()
        return frame_read.frame

   
            




def main():
    frontend = FrontEnd()
    
    # run frontend
    frontend.run()
    



if __name__ == '__main__':
    main()
