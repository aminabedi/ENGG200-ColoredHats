import cv2
import numpy as np
import imutils as imu
from collections import deque
from imutils.video import VideoStream
import argparse
import pandas as pd
import time

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True,
    help="path to the video file")
ap.add_argument("-r", "--radius", type=int, default=10,
	help="Minimum radius of the object to be detected")
ap.add_argument("-o", "--output",
	help="Filename to save the coordinates of the detected objects")
ap.add_argument("-d", "--display", dest='display', action='store_true',
	help="Display frames as they are processed")
args = vars(ap.parse_args())

display = args["display"]
#lower bound, upper bound and RGB values for the detected colors using detect.py
colors = {
  "Y": {
    "bounds": [[12, 138, 147], [28, 208, 229]],
    "rgb": [0, 255, 255]
  },
  "R": {
    "bounds": [[177, 144, 95], [179, 255, 228]],
    "rgb": [0, 0, 255]
  }
}

df = pd.DataFrame({c: pd.Series(dtype=t) for c, t in {'Frame#': 'int', 'Color': 'str', 'x':'int', 'y': 'int', "x_max":'int', 'y_max': 'int'}.items()})

vs = cv2.VideoCapture(args["video"])

frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
length = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
frame_no = 0 #0-indexed frame numbers

if (vs.isOpened()== False): 
  print("Error opening video stream or file")
  
# Read until video is completed
while(frame_no < length and vs.isOpened()): #In some versions, isOpened freezes on the last frame, so we also manually check the frame count
  # Capture frame-by-frame
  ret, frame = vs.read()
  if ret == True:
    #define kernel size  
    kernel = np.ones((7,7),np.uint8)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    for c in colors:
      # find the regions within the boundaries
      bounds = (np.array(colors[c]["bounds"][0], dtype="uint8"),
                np.array(colors[c]["bounds"][1], dtype="uint8"))
      rgb = colors[c]["rgb"]
      mask = cv2.inRange(hsv, bounds[0], bounds[1])
      
      # Remove unnecessary noise from mask
      mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
      mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
      
      # Find contours from the mask
      contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)
      contours = imu.grab_contours(contours)
      center = None
      # only proceed if at least one contour was found
      if len(contours):
          cnts = contours
          # find the largest contour in the mask, then use
          # it to compute the minimum enclosing circle and
          # centroid
          for cnt in contours:
            # c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            M = cv2.moments(cnt)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > args["radius"]:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                if display:
                  cv2.circle(frame, (int(x), int(y)), int(radius), rgb , 2)
                  cv2.circle(frame, center, 5, rgb, -1)
                df = pd.concat([df, pd.DataFrame([{
                  "Frame#": frame_no, 
                  "Color": c, 
                  "x": center[0], "y": center[1], 
                  "x_max": frame_width, "y_max": frame_height}])], ignore_index=True)
            #else: Not big enough to capture!
      

    if display:
      # Display the resulting frame
      cv2.imshow('Frame',frame)
      # Press Q on keyboard to  exit
      if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    print(f"Frames processed: {frame_no + 1}/{length}, detected: {len(df)}", end="\r")
    frame_no += 1
if "output" in args:
  print("Writing CSV file")
  df.to_csv(args["output"], index=False)
# When everything done, release the video capture object
vs.release()
# Closes all the frames
cv2.destroyAllWindows()

