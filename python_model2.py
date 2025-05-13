import cv2
import numpy as np
import os
import time
from datetime import datetime
import threading
import queue
import zipfile

# Global variables for federated learning simulation
model_updates_queue = queue.Queue()
current_model_version = 0
is_recording = False
recording_start_time = None

class VideoProcessor:
    def __init__(self, resolution=(640, 480), fps=30.0, codec='XVID'):
        self.resolution = resolution
        self.fps = fps
        self.codec = cv2.VideoWriter_fourcc(*codec)
        self.output_file = None
        self.frame_buffer = []
        self.compression_quality = 50  # JPEG compression quality (0-100)
        self.record_path = "recordings"
        
        # Create recording directory if it doesn't exist
        if not os.path.exists(self.record_path):
            os.makedirs(self.record_path)
        
        # Simple "model" for frame analysis (placeholder for actual ML model)
        self.frame_analyzer = SimpleFrameAnalyzer()
    
    def start_recording(self):
        global is_recording, recording_start_time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(self.record_path, f"video_{timestamp}.avi")
        self.output_file = cv2.VideoWriter(
            output_filename, 
            self.codec, 
            self.fps, 
            self.resolution
        )
        is_recording = True
        recording_start_time = time.time()
        print(f"Recording started: {output_filename}")
        return output_filename
    
    def stop_recording(self):
        global is_recording
        if self.output_file is not None:
            self.output_file.release()
            self.output_file = None
            is_recording = False
            duration = time.time() - recording_start_time
            print(f"Recording stopped. Duration: {duration:.2f} seconds")
            zip_recordings()
    
    def compress_frame(self, frame):
        # Compress frame using JPEG compression
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.compression_quality]
        _, compressed = cv2.imencode('.jpg', frame, encode_param)
        return cv2.imdecode(compressed, cv2.IMREAD_COLOR)
    
    def process_frame(self, frame):
        # Resize frame to target resolution
        frame = cv2.resize(frame, self.resolution)
        
        # Apply compression
        compressed_frame = self.compress_frame(frame)
        
        # Process with frame analyzer (simulated federated learning)
        self.frame_analyzer.analyze_frame(compressed_frame)
        
        # Add text overlays
        self.add_frame_info(compressed_frame)
        
        # Save frame if recording
        if is_recording and self.output_file is not None:
            self.output_file.write(compressed_frame)
        
        return compressed_frame
    
    def add_frame_info(self, frame):
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add compression info
        comp_text = f"Compression: {self.compression_quality}%"
        cv2.putText(frame, comp_text, (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add recording indicator
        if is_recording:
            # Flashing red circle
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
            
            # Recording duration
            duration = time.time() - recording_start_time
            duration_text = f"REC {int(duration // 60):02d}:{int(duration % 60):02d}"
            cv2.putText(frame, duration_text, (frame.shape[1] - 150, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Add model version info
        model_text = f"Model v{current_model_version}"
        cv2.putText(frame, model_text, (10, frame.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


class SimpleFrameAnalyzer:
    """Simulates a federated learning model that analyzes frames"""
    def __init__(self):
        self.frame_count = 0
        self.update_interval = 30  # Generate model update every 30 frames
        self.features_buffer = []
    
    def analyze_frame(self, frame):
        # Extract "features" (simplified for demonstration)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        self.features_buffer.append(avg_brightness)
        
        self.frame_count += 1
        
        # Generate model update periodically
        if self.frame_count % self.update_interval == 0:
            self.generate_model_update()
    
    def generate_model_update(self):
        """Simulate generating a model update from collected features"""
        global model_updates_queue
        
        if not self.features_buffer:
            return
        
        # Simple "model update" - just average brightness values
        update = {
            'avg_brightness': np.mean(self.features_buffer),
            'frame_count': self.frame_count
        }
        
        # Add to queue for the federated learning process
        model_updates_queue.put(update)
        
        # Clear buffer
        self.features_buffer = []


def federated_learning_process():
    """Simulates a federated learning process running in background"""
    global current_model_version
    
    while True:
        # Collect updates (if any)
        updates = []
        while not model_updates_queue.empty():
            updates.append(model_updates_queue.get())
        
        # If we have updates, "improve" the model
        if updates:
            print(f"Received {len(updates)} model updates")
            # In a real system, would aggregate model updates here
            
            # Simulate model improvement
            current_model_version += 1
            print(f"Model updated to version {current_model_version}")
        
        # Sleep to simulate periodic model updates
        time.sleep(5)


def display_help():
    """Display keyboard shortcuts help"""
    help_text = """
    Keyboard Controls:
    ------------------
    SPACE - Start/Stop Recording
    + / - - Increase/Decrease Compression
    q     - Quit
    h     - Show this help
    """
    print(help_text)
    
def zip_recordings():
    zip_filename = f"recordings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk("recordings"):
            for file in files:
                if file.endswith(".avi"):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, "recordings")
                    zipf.write(file_path, arcname)

    print(f"Recordings zipped successfully: {zip_path}")

def stop_recording(self):
    global is_recording
    if self.output_file is not None:
        self.output_file.release()
        self.output_file = None
        is_recording = False
        duration = time.time() - recording_start_time
        print(f"Recording stopped. Duration: {duration:.2f} seconds")
        zip_recordings()  # Automatically zip after stopping



def main():
    # Start federated learning background process
    fl_thread = threading.Thread(target=federated_learning_process, daemon=True)
    fl_thread.start()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Initialize video processor
    processor = VideoProcessor()
    
    display_help()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        # Process the frame
        processed_frame = processor.process_frame(frame)
        
        # Display the processed frame
        cv2.imshow("Federated Learning Camera", processed_frame)
        
        # Process keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):  # Space to start/stop recording
            if is_recording:
                processor.stop_recording()
            else:
                processor.start_recording()
        elif key == ord('+') or key == ord('='):  # Increase quality
            processor.compression_quality = min(100, processor.compression_quality + 5)
            print(f"Compression quality: {processor.compression_quality}%")
        elif key == ord('-'):  # Decrease quality
            processor.compression_quality = max(5, processor.compression_quality - 5)
            print(f"Compression quality: {processor.compression_quality}%")
        elif key == ord('h'):  # Help
            display_help()
    
    # Clean up
    if is_recording:
        processor.stop_recording()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()