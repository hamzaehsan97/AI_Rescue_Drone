from djitellopy import Tello
import cv2
import pygame
from pygame.locals import *
import numpy as np
import time
import face_recognition
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
        ## Adjust safety checks on API updates
        # if not self.tello.connect():
        #     print("Tello not connected")
        #     return

        # if not self.tello.set_speed(self.speed):
        #     print("Not set speed to lowest possible")
        #     return

        
        # if not self.tello.streamoff():
        #     print("Could not stop video stream")
        #     return

        # if not self.tello.streamon():
        #     print("Could not start video stream")
        #     return

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





            # OLD CODE
            hsv = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0,70,50])
            upper_red = np.array([10,255,255])
            mask = cv2.inRange(hsv, lower_red, upper_red)
            # red = cv2.bitwise_and(frame,frame, mask= mask)
            redcnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
            #greyscale the frame
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #detect faces from grey frame
            faces = face.detectMultiScale(grey, 1.3, 5) 
            #detect upperbody from frame
            bodies = body.detectMultiScale(grey, scaleFactor=1.15, minNeighbors = 5, flags = cv2.CASCADE_SCALE_IMAGE )
            
            
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

            #####OLD CODE
            forward = 0
            rotate = 0
            
            #If faces are not available wait 4 seconds before staying still
            if self.auto == True:
                if len(faces)  == 0:
                    face_null_timer = face_null_timer+1
                    if face_null_timer >= 120:
                        self.yaw_velocity = 0
                        self.for_back_velocity = 0
                        self.left_right_velocity = 0
                        self.up_down_velocity = 0
                    
                
            #If faces exist then overlay rectangles on the frame 
            
            for (x,y,w,h) in faces:
                face_null_timer = 0
                rectangle = cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.circle(frame, (480, 360), 5, (0,255,0), thickness=2)
                xVal=int(x+(w/2))
                yVal=int(y+(h/2))
                circ = cv2.circle(frame,(xVal,yVal), 5, (255,0,0), 2)
                roi_grey = grey[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                xDistance = xVal - 480
                yDistance = yVal - 360

                #If autonomous flight is set to true then fly towards the face in the frame
                if(self.auto == True):
                    print("In the auto loop")
                    if(abs(xDistance) > 50 and abs(yDistance) > 50 and xVal,yVal != 0 and x,y != 0 and w,h == True):
                        print("Face detected, centering in")
                        # If subject is to the left or right
                        if(xDistance < horizontal_distance_face):
                            self.yaw_velocity = int(-S)
                            print("turn left")
                        elif(xDistance > horizontal_distance_face):
                            self.yaw_velocity = int(S)
                            print("turn right")
                        else:
                            self.yaw_velocity = 0
                            print("dont turn")
                        # If subject is above or below the frame    
                        if(yDistance < -130):
                            self.up_down_velocity = int(S)
                            print("Go up")
                        elif(yDistance > 130):
                            self.up_down_velocity = int(-S)
                            print("Go down")
                        else:
                            self.up_down_velocity = 0
                            print("Y constant")
                            # If subject is above or below the frame    
                        if(w < 70):
                            self.for_back_velocity = S
                            print("Go forward")
                        elif(w > 150):
                            self.for_back_velocity = -S
                            print("Go back")
                        else:
                            self.for_back_velocity = 0
                            print("z constant")
            #if Bodies exist in the frame then draw rectangles around them
            for (x,y,w,h) in bodies:
                bodyRectangle = cv2.rectangle(frame, (x,y), (x+w, y+h), (240,100,100), 1)
                xVal=int(x+(w/2))
                yVal=int(y+(h/2))
                bodyCircle = cv2.circle(frame,(xVal,yVal), 5, (240,100,100), 1)

                #if contour is available for red mask then draw a rectangle
                if len(redcnts)>0:
                    redArea = max(redcnts, key=cv2.contourArea)
                    (xg,yg,wg,hg) = cv2.boundingRect(redArea)
                    length = math.sqrt((wg*wg)+(hg*hg))
                    xValue = int(xg+(wg/2))
                    yValue = int(yg+(hg/2))
                    xDist = xVal - xValue
                    yDist = yVal - yValue
                    distanceToBody = math.sqrt((xDist * xDist)+(yDist * yDist))
                    if length >= 150 and distanceToBody < 300:
                        cv2.rectangle(frame,(xg,yg),(xg+wg, yg+hg),(0,100,100),2)
                        shirtCircle = cv2.circle(frame,(xValue,yValue), 5, (0,100,100), 1)
                    elif len(faces)  > 0:
                        print("Found body")
                        addToDatabase(datetime.date,self.tello.get_attitude)
                       
                        

            
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
        
        # hud = Hud()

        # if self.battery:
        #      hud.add(f"BAT {self.battery}")
        
        # hud.add(f"Battery")

        # hud.draw(frame)

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
