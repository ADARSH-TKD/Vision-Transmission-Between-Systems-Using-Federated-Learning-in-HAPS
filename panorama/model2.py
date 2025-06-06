import cv2
import os

# Read the video
cam = cv2.VideoCapture("C:\\Users\\adarsh\\Downloads\\panorama\\video.mp4")

try:
    if not os.path.exists('data'):
        os.makedirs('data')
except OSError:
    print('Error: Creating directory of data')

# Frame extraction
currentframe = 0
frames = []
skip_frames = 5  # Process every 5th frame
frame_count = 0

while True:
    ret, frame = cam.read()
    if not ret:
        break
    if frame_count % skip_frames == 0:
        # Downscale frame
        frame = cv2.resize(frame, (640, 360))
        name = f'./data/frame{currentframe}.jpg'
        print(f'Creating...{name}')
        cv2.imwrite(name, frame)
        frames.append(frame)
        currentframe += 1
    frame_count += 1

# Release video
cam.release()

# Stitch frames
print("Stitching frames into panorama...")
stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)  # Optimized for linear panning
status, panorama = stitcher.stitch(frames)

if status == cv2.Stitcher_OK:
    cv2.imwrite('./data/panorama.jpg', panorama)
    print("Panorama saved as './data/panorama.jpg'")
else:
    print("Stitching failed with status:", status)
    if status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Need more images")
    elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print("Homography estimation failed")
    elif status == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
        print("Camera parameters adjustment failed")

cv2.destroyAllWindows()