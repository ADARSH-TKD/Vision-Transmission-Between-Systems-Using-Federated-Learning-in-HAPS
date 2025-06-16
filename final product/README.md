# Video Processing and Panorama Creation System

## 1. Introduction
This project implements a client-server system for video processing, recording, and panorama creation. The server (`sever3.py`) captures video, processes frames with simulated federated learning, records videos, and distributes them to connected clients. The client (`client2.py`) receives video files, plays them, and creates panoramic images from the video frames. The system supports real-time video processing, file transfer, and automated panorama generation with a user-friendly interface.

<!DOCTYPE html>
<html>
<body>

  <div class="image-hover">
    <img src="https://github.com/ADARSH-TKD/Vision-Transmission-Between-Systems-Using-Federated-Learning-in-HAPS/raw/main/video/img1.png" alt="Federated Learning Image">
  </div>

</body>
</html>


## 2. Working Flow
1. **Server Side (`sever3.py`)**:
   - Initializes a video capture device (webcam) and a TCP server on `localhost:8080`.
   - Processes video frames with JPEG compression, overlays information (timestamp, client count, model version, etc.), and simulates federated learning by analyzing frame brightness.
   - Records videos to the `recordings` directory when triggered (spacebar).
   - Zips recorded videos and automatically sends them to connected clients if auto-send is enabled.
   - Maintains client connections, handles file transfers, and updates a simulated model version periodically.

2. **Client Side (`client2.py`)**:
   - Connects to the server to receive zipped video files or processes local videos.
   - Extracts videos from received zip files and saves them in the `downloads` directory.
   - Plays videos with controls (pause/resume, skip, restart) and displays a progress bar.
   - Creates panoramas from video frames using OpenCV's stitching algorithms, saving frames and panoramas in the `data` directory.
   - Supports both server-based and local video processing modes.

## 3. Modules Used
- **Python Standard Libraries**:
  - `os`, `time`, `datetime`, `threading`, `queue`, `zipfile`, `socket`, `struct`, `glob`, `pathlib`
- **Third-Party Libraries**:
  - `opencv-python` (cv2): For video capture, frame processing, and panorama stitching.
  - `numpy`: For numerical operations on frame data.
- **No additional installations** are required beyond these libraries, assuming a Python environment (3.6+).

## 4. Directory Structure
```
project_directory/
│
├── sever3.py              # Server script for video capture and distribution
├── client2.py             # Client script for video playback and panorama creation
├── recordings/            # Stores recorded .avi videos (created by server)
├── downloads/             # Stores received zip files and extracted videos (created by client)
│   └── extracted/         # Stores videos extracted from zip files
├── data/                  # Stores extracted frames and panorama images (created by client)
└── README.md              # Project documentation
```

## 5. How to Run the Code
### Prerequisites
- Python 3.6 or higher.
- Install required libraries:
  ```bash
  pip install opencv-python numpy
  ```
- A webcam connected to the server machine.
- Ensure `localhost:8080` is not blocked by a firewall.

### Steps to Run
1. **Start the Server**:
   - Open a terminal in the project directory.
   - Run the server script:
     ```bash
     python sever3.py
     ```
   - The server will start capturing video and listening for client connections.
   - Use keyboard controls:
     - `SPACE`: Start/stop recording.
     - `+/-`: Adjust compression quality.
     - `s`: Send the latest zip file to clients.
     - `a`: Toggle auto-send zip files.
     - `z`: List available zip files.
     - `h`: Show help.
     - `q`: Quit.

2. **Start the Client**:
   - Open another terminal in the project directory.
   - Run the client script:
     ```bash
     python client2.py
     ```
   - Choose an option:
     - **1**: Connect to the server (default: `localhost:8080`).
       - The client will wait for zip files from the server, play received videos, and create panoramas.
     - **2**: Process a local video file (play first, then create panorama).
     - **3**: Play a local video file only.
   - For server mode, ensure the server is running before connecting.

3. **Example Workflow**:
   - Start the server and press `SPACE` to record a video.
   - Stop recording with `SPACE` to create and send a zip file to connected clients.
   - On the client, select option 1 to receive the zip, play the videos, and generate panoramas.
   - Alternatively, use option 2 to process a local video file.

## 6. Outcomes
- **Server**:
  - Captures and processes video frames in real-time with overlays (timestamp, client count, recording status, model version).
  - Records videos in `.avi` format and creates zip archives in the `recordings` directory.
  - Distributes zip files to clients automatically or manually.
  - Simulates federated learning by updating a model version based on frame brightness analysis.

- **Client**:
  - Receives and extracts zip files containing videos, saving them in `downloads/extracted`.
  - Plays videos with a progress bar and controls (pause, skip, restart).
  - Generates panoramic images from video frames, saved in `data` as `.jpg` files.
  - Supports local video processing for testing without a server.

- **Panorama Creation**:
  - Extracts frames (every 5th by default) from videos and stitches them using OpenCV's Stitcher.
  - Handles both modern (OpenCV 4.x) and legacy (OpenCV 3.x) stitching APIs.
  - Provides error diagnostics for stitching failures (e.g., insufficient overlap).
  - Saves sample frames for debugging if panorama creation fails.

This system is ideal for applications requiring distributed video processing and panoramic image generation, with a focus on ease of use and extensibility.
