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
import os
import sys

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

        


    def run(self):

        if not self.tello.connect():
            print("Tello not connected")
            return
        else:
            print('connected')

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return

        
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return


def main():
    frontend = FrontEnd()
    
    # run frontend
    frontend.run()
    



if __name__ == '__main__':
    main()
