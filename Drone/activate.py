from djitellopy import Tello
import cv2
import pygame
from pygame.locals import *
import numpy as np
import time
import math

S = 20
FPS = 30
face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lowerbody.xml')
noice = 30


class FrontEnd(object):
   

    def __init__(self):
        
        pygame.init()

       
        pygame.display.set_caption("Rescue Feed")
        self.screen = pygame.display.set_mode([960, 720])

       
        self.tello = Tello()

        
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 9

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

        frame_read = self.tello.get_frame_read()

        should_stop = False
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
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
            # frame1 = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2HSV)
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face.detectMultiScale(grey, 1.3, 5)
            forward = 0
            rotate = 0
            for (x,y,w,h) in faces:
                rectangle = cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                cv2.circle(frame, (480, 360), 5, (0,0,255), thickness=2)
                xVal=int(x+(w/2))
                yVal=int(y+(h/2))
                circ = cv2.circle(frame,(xVal,yVal), 5, (255,0,0), 2)
                roi_grey = grey[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                eyes = eye.detectMultiScale(roi_grey)
                print("width "+ str(w)+" height "+str(h))
                xDistance = xVal - 480
                yDistance = yVal - 360
                # if(circ != True):
                #     if(self.tello.get_height)
                #     self.tello.for_back_velocity = S
                # height= self.tello.get_height()
                # height = int(''.join([i for i in height if i.isdigit()]))
                
                # if("No face is detected"):
                # if(height<150):
                #     self.up_down_velocity = int(S/10)
                #     print("Going up")
                # elif(height>250):
                #     self.up_down_velocity = int(S/10)
                #     print("Going down")
                # else:
                #     self.up_down_velocity = 0
                #     #Go forward forward for one second, rotate for 0.5 seconds if no face found
                #     if(forward = 0):
                #         self.for_back_velocity = int(S/10)
                #         forward=forward+1
                #         if(forward >= 20):
                #             self.for_back_velocity = 0
                #             self.yaw_velocity = int(S/10)
                #             rotate = rotate+1
                #             if(rotate >= 10):
                #                 self.yaw_velocity = 0
                #                 rotate = 0
                #                 forward = 0
                # el
                if(abs(xDistance) > 50 and abs(yDistance) > 50 and xVal,yVal != 0 and x,y != 0 and w,h == True):
                    print("Face detected, centering in")
                    # If subject is to the left or right
                    if(xDistance < noice):
                        self.yaw_velocity = int(-1.5*S)
                        print("turn left")
                    elif(xDistance > noice):
                        self.yaw_velocity = int(1.5*S)
                        print("turn right")
                    else:
                        self.yaw_velocity = 0
                        print("dont turn")
                    # If subject is above or below the frame    
                    if(yDistance < -noice-100):
                        self.up_down_velocity = int(S/5)
                        print("Go up")
                    elif(yDistance > noice+100):
                        self.up_down_velocity = int(-S/5)
                        print("Go down")
                    else:
                        self.up_down_velocity = 0
                        print("Y constant")
                        # If subject is above or below the frame    
                    if(w < 300):
                        self.for_back_velocity = S
                        print("Go forward")
                    elif(w > 400):
                        self.for_back_velocity = -S
                        print("Go back")
                    else:
                        self.for_back_velocity = 0
                        print("z constant")
                    # if(height < 150):
                    #     self.up_down_velocity = int(S/10)
                    #     print("Go forward")
                    # elif(height > 200):
                    #     self.up_down_velocity = int(-S/10)
                    #     print("Go back")
                    # else:
                    #     self.up_down_velocity = 0
                    #     print("z constant")
                    
                for(ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (255,0,0), 2)
            cv2.circle(frame, (480, 360), 5, (0,0,255), thickness=2)
            # frame1 = np.rot90(frame1)
            # frame1 = np.rot90(frame1)
            # frame1 = np.flipud(frame1)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            # a = np.array([0,70,50])
            # b = np.array([10,255,255])
            # mask = cv2.inRange(frame1,a,b)
            # faces, confidences = cv2.detect_face(frame)
            # (startX,startY) = face[0],face[1]
            # (endX,endY) = face[2],face[3]
            # face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
            # recognizer = cv2.face.EigenFaceRecognizer_create()
            # res = cv2.bitwise_and(frame,frame, mask=mask) USELESS FOR NOW
            #cv2.imshow("face", frame)
            # cv2.imshow("RED",mask)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()
            # print(self.tello.get_battery())
            
            time.sleep(1 / FPS)
        # CALL BEFORE END!!!!!!!!!!!!!!!!!!
        self.tello.end()

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
            self.yaw_velocity = -S
        elif key == pygame.K_d:  # anti-clockwise
            self.yaw_velocity = S

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

    def update(self):
        # Send updates
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)


def main():
    frontend = FrontEnd()

    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()
