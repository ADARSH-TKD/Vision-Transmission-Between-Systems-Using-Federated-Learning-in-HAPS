import cv2
import os
import glob
import numpy as np

# Read the video from specified path
cam = cv2.VideoCapture("C:\\Users\\adarsh\\Downloads\\panorama\\video.mp4")

try:
    # creating a folder named data
    if not os.path.exists('data'):
        os.makedirs('data')
except OSError:
    print('Error: Creating directory of data')

# frame
currentframe = 0
frames = []

while(True):
    # reading from frame
    ret, frame = cam.read()

    if ret:
        # if video is still left continue creating images
        name = './data/frame' + str(currentframe) + '.jpg'
        print('Creating...' + name)

        # writing the extracted images
        cv2.imwrite(name, frame)

        # store frame for stitching
        frames.append(frame)

        # increasing counter
        currentframe += 1
    else:
        break

# Release video capture
cam.release()

# Create panorama from extracted frames
print("Creating panorama...")

# Initialize OpenCV's Stitcher
stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)

# Stitch all frames
status, panorama = stitcher.stitch(frames)

if status == cv2.Stitcher_OK:
    # Save the panorama
    cv2.imwrite('./data/panorama.jpg', panorama)
    print("Panorama created successfully and saved as './data/panorama.jpg'")
else:
    print("Error during stitching:", status)
    if status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Need more images for successful stitching")
    elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print("Homography estimation failed")
    elif status == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
        print("Camera parameters adjustment failed")

# Clean up: optionally remove individual frame images
# Comment out if you want to keep individual frames
for frame_file in glob.glob('./data/frame*.jpg'):
    os.remove(frame_file)

# Destroy all windows
cv2.destroyAllWindows()