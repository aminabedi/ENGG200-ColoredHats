import cv2
import numpy as np
import imutils as imu
from collections import deque
from imutils.video import VideoStream
import argparse
import time

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the video file")
ap.add_argument("-b", "--buffer", type=int, default=10,
	help="max buffer size")
args = vars(ap.parse_args())

pts = deque(maxlen=args["buffer"])
vs = cv2.VideoCapture(args["video"])

frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
print(frame_width, frame_height)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = None

if (vs.isOpened()== False): 
  print("Error opening video stream or file")


  
print("Capture ready!")
# Read until video is completed
while(vs.isOpened()):
  # Capture frame-by-frame
  ret, frame = vs.read()
  if ret == True:
    #define kernel size  
    kernel = np.ones((7,7),np.uint8)
    # convert to hsv colorspace 
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower bound and upper bound for Green color 
    sensitivity = 100
    lower_bound = np.array([0,0,255-sensitivity])
    upper_bound = np.array([255,sensitivity,255])
    # lower_bound = np.array([50, 20, 20])     
    # upper_bound = np.array([100, 255, 255])

    # lower bound and upper bound for Yellow color 
    # lower_bound = np.array([20, 80, 80])     
    # upper_bound = np.array([30, 255, 255])

    frame = imu.resize(frame, width=600)
    if out is None:
      print("Setting outstream!")
      dim = frame.shape[-2::-1]
      print(dim)
      out = cv2.VideoWriter('output.mp4', fourcc, 50.0, dim)
      if out.isOpened()== False: 
        print("Error opening video writer stream or file")
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # find the colors within the boundaries
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    # Remove unnecessary noise from mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)



    # Segment only the detected region

    segmented_img = cv2.bitwise_and(frame, frame, mask=mask)

    # Find contours from the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_LIST,
		cv2.CHAIN_APPROX_SIMPLE)
    cnts = imu.grab_contours(cnts)
    center = None
    # only proceed if at least one contour was found

    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 0:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(frame, center, 5, (255, 255, 255), -1)
    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (255, 255, 255), thickness)

    # Draw contour on segmented image
    
    # output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)


    # Draw contour on original image
    # output = cv2.drawContours(frame, contours, -1, (0, 0, 255), 3)

    # Display the resulting frame
    cv2.imshow('Frame',frame)
    out.write(frame)
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

  # Break the loop
  else: 
    break

# When everything done, release the video capture object
print("RELEASING!")
vs.release()
out.release()
# Closes all the frames
cv2.destroyAllWindows()
exit()

# Reading the image

img = cv2.imread('image.jpg')

#define kernel size  
kernel = np.ones((7,7),np.uint8)


# convert to hsv colorspace 
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# lower bound and upper bound for Green color 
# lower_bound = np.array([50, 20, 20])     
# upper_bound = np.array([100, 255, 255])

# lower bound and upper bound for Yellow color 
lower_bound = np.array([20, 80, 80])     
upper_bound = np.array([30, 255, 255])


# find the colors within the boundaries
mask = cv2.inRange(hsv, lower_bound, upper_bound)


# Remove unnecessary noise from mask

mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)



# Segment only the detected region

segmented_img = cv2.bitwise_and(img, img, mask=mask)

# Find contours from the mask

contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw contour on segmented image
 
# output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)


# Draw contour on original image

output = cv2.drawContours(img, contours, -1, (0, 0, 255), 3)

# Showing the output

# cv2.imshow("Image", img)
cv2.imshow("Output", output)

cv2.waitKey(0)
cv2.destroyAllWindows()

