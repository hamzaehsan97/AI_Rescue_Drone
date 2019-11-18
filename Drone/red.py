import numpy as np
import cv2  
import math

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in HSV
    lower_red = np.array([0,70,50])
    upper_red = np.array([10,255,255])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange (hsv, lower_red, upper_red)
    bluecnts = cv2.findContours(mask.copy(),
                              cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_SIMPLE)[-2]

    if len(bluecnts)>0:
        blue_area = max(bluecnts, key=cv2.contourArea)
        (xg,yg,wg,hg) = cv2.boundingRect(blue_area)
        length = math.sqrt((wg*wg)+(hg*hg))
        if length >= 150:
            cv2.rectangle(frame,(xg,yg),(xg+wg, yg+hg),(0,255,0),2)

    cv2.imshow('frame',frame)
    # cv2.imshow('mask',mask)

    k = cv2.waitKey(5) 
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()