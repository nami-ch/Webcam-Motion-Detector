from asyncio import queues
from os import stat
from tabnanny import check
import cv2, time 
from datetime import datetime
import pandas 

# First frame to be set as the base frame 
first_frame = None
status_list = [None, None]
times = []
df = pandas.DataFrame(columns=["Start", "End"])

# Capturing of the video through the webcam 
video = cv2.VideoCapture(0)

while True: 
    check, frame = video.read()
    status = 0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Blurring the image to remove the noise and smoothening
    gray = cv2.GaussianBlur(gray, (21,21),0) # parameter1 = width & height of guassion kernel 

    # Setting the first frame 
    if (first_frame is None):
        first_frame = gray
        continue
    
    # Difference between the current frame and the first frame 
    delta_frame = cv2.absdiff(first_frame, gray)
    
    # Setting a threshold 
    thresh_frame = cv2.threshold(delta_frame, 30, 255,cv2.THRESH_BINARY)[1]
    
    # Removing the black holes form the threshold frame, smoothening 
    thresh_frame = cv2.dilate(thresh_frame, None, iterations= 5)

    # Finding the contours 
    (cnts,_) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # external contours 

    # checking if the area of the cntour is below 1000, not detected as an object 
    for contour in cnts: 
        if cv2.contourArea(contour) < 10000:
            continue
        
        status = 1 # if an object is detected  
        # drawing rectangle around the objects 
        (x,y,w,h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3)
    
    # Status list for the entering and exiting of the object 
    status_list.append(status)

    status_list = status_list[-2:]
    
    # Capturing the time when the objects enters & exits through checking the last items at that frame 
    if status_list[-1] == 1 and status_list[-2]== 0:
        times.append(datetime.now())
    if status_list[-1] == 0 and status_list[-2]== 1:
        times.append(datetime.now())

    cv2.imshow("Capturing", gray)
    cv2.imshow("Delta frame",delta_frame)
    cv2.imshow("Threshold frame", thresh_frame)
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        # for when there is an object at the time of closing the window 
        if status == 1:
            times.append(datetime.now())
        break

print(times)
print(status_list)

# Saving the data 
for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End":times[i+1]}, ignore_index= True)


df.to_csv("Times.csv")
video.release()
cv2.destroyAllWindows()
