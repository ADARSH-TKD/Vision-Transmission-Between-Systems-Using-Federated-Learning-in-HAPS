import socket
import os
import struct
import time
import zipfile
import cv2
import glob
from pathlib import Path

class VideoClientPanorama:
    def __init__(self, save_directory="downloads", data_directory="data"):
        self.save_directory = save_directory
        self.data_directory = data_directory
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories"""
        for directory in [self.save_directory, self.data_directory]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Created directory: {directory}")

    def play_video(self, video_path, window_name="Video Player", auto_close=True):
        """
        Play video using OpenCV with controls
        
        Args:
            video_path: Path to the video file
            window_name: Name of the display window
            auto_close: Whether to auto-close after video ends
        
        Controls:
            - SPACE: Pause/Resume
            - ESC/Q: Quit
            - R: Restart video
            - Arrow keys: Skip forward/backward
        """
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        print(f"🎬 Playing video: {os.path.basename(video_path)}")
        print("Controls: SPACE=Pause/Resume, ESC/Q=Quit, R=Restart, Arrow Keys=Skip")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ Cannot open video file: {video_path}")
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        frame_delay = int(1000 / fps) if fps > 0 else 33  # milliseconds
        
        print(f"📹 Video info: {total_frames} frames, {fps:.2f} FPS, {duration:.2f}s")
        
        # Create window - Fixed OpenCV compatibility issue
        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # Changed from WINDOW_RESIZABLE
        except AttributeError:
            cv2.namedWindow(window_name)  # Fallback for older versions
        
        paused = False
        current_frame = 0
        
        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        print("🏁 Video playback finished")
                        if auto_close:
                            break
                        else:
                            # Loop video
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            current_frame = 0
                            continue
                    
                    current_frame += 1
                    
                    # Display frame info
                    height, width = frame.shape[:2]
                    progress = (current_frame / total_frames) * 100
                    time_elapsed = current_frame / fps if fps > 0 else 0
                    
                    # Add progress bar overlay
                    cv2.rectangle(frame, (10, height - 30), (width - 10, height - 10), (0, 0, 0), -1)
                    progress_width = int((width - 20) * (current_frame / total_frames))
                    cv2.rectangle(frame, (10, height - 30), (10 + progress_width, height - 10), (0, 255, 0), -1)
                    
                    # Add text info
                    info_text = f"Frame: {current_frame}/{total_frames} | Time: {time_elapsed:.1f}s/{duration:.1f}s | {progress:.1f}%"
                    cv2.putText(frame, info_text, (15, height - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    if paused:
                        cv2.putText(frame, "PAUSED - Press SPACE to resume", (15, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                cv2.imshow(window_name, frame)
                
                # Handle keyboard input
                key = cv2.waitKey(frame_delay if not paused else 1) & 0xFF
                
                if key == 27 or key == ord('q'):  # ESC or Q to quit
                    print("⏹️ Playback stopped by user")
                    break
                elif key == ord(' '):  # SPACE to pause/resume
                    paused = not paused
                    print("⏸️ Paused" if paused else "▶️ Resumed")
                elif key == ord('r'):  # R to restart
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    current_frame = 0
                    paused = False
                    print("🔄 Video restarted")
                elif key == 83:  # Right arrow - skip forward
                    new_frame = min(current_frame + int(fps * 5), total_frames - 1)  # Skip 5 seconds
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    current_frame = new_frame
                    print(f"⏭️ Skipped forward to frame {current_frame}")
                elif key == 81:  # Left arrow - skip backward
                    new_frame = max(current_frame - int(fps * 5), 0)  # Skip back 5 seconds
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    current_frame = new_frame
                    print(f"⏮️ Skipped backward to frame {current_frame}")
        
        except KeyboardInterrupt:
            print("\n⏹️ Playback interrupted")
        
        finally:
            cap.release()
            cv2.destroyWindow(window_name)
            print("✅ Video playback completed")
        
        return True

    def play_multiple_videos(self, video_paths, auto_advance=True):
        """
        Play multiple videos in sequence
        
        Args:
            video_paths: List of video file paths
            auto_advance: Whether to automatically advance to next video
        """
        if not video_paths:
            print("❌ No videos to play")
            return
        
        print(f"🎬 Playing {len(video_paths)} video(s) in sequence")
        
        for i, video_path in enumerate(video_paths):
            print(f"\n{'='*50}")
            print(f"📺 Playing video {i+1}/{len(video_paths)}: {os.path.basename(video_path)}")
            
            if not self.play_video(video_path, f"Video {i+1}/{len(video_paths)}", auto_close=auto_advance):
                print(f"❌ Failed to play video: {video_path}")
                continue
            
            if not auto_advance and i < len(video_paths) - 1:
                response = input(f"\nPress Enter to play next video, or 'q' to quit: ").strip().lower()
                if response == 'q':
                    print("🛑 Playback stopped by user")
                    break
        
        print("🏁 All videos played successfully!")

    def receive_file(self, s):
        """Receive a file from the server"""
        try:
            # Receive file size
            file_size_bytes = s.recv(8)
            if len(file_size_bytes) != 8:
                print("Error receiving file size")
                return None
                
            file_size = struct.unpack('!Q', file_size_bytes)[0]
            
            if file_size == 0:
                print("Server reported file error or file not found")
                return None
                
            print(f"\n🎥 Receiving video recording file of size: {file_size / (1024*1024):.2f} MB")
            
            # Receive file name length
            file_name_len_bytes = s.recv(4)
            file_name_len = struct.unpack('!I', file_name_len_bytes)[0]
            
            # Receive file name
            file_name_bytes = s.recv(file_name_len)
            file_name = file_name_bytes.decode('utf-8')
            
            # Full path for saving
            file_path = os.path.join(self.save_directory, file_name)
            print(f"📁 Saving as: {file_path}")
            
            # Receive file data with progress bar
            with open(file_path, 'wb') as f:
                bytes_received = 0
                start_time = time.time()
                last_update = time.time()
                
                while bytes_received < file_size:
                    chunk_size = min(4096, file_size - bytes_received)
                    chunk = s.recv(chunk_size)
                    if not chunk:
                        print("Connection lost during file transfer")
                        return None
                        
                    f.write(chunk)
                    bytes_received += len(chunk)
                    
                    # Show progress every 0.5 seconds
                    current_time = time.time()
                    if current_time - last_update >= 0.5:
                        progress = (bytes_received / file_size) * 100
                        speed = bytes_received / (current_time - start_time) / 1024  # KB/s
                        eta = (file_size - bytes_received) / (bytes_received / (current_time - start_time))
                        
                        print(f"📊 Progress: {progress:.1f}% | Speed: {speed:.1f} KB/s | ETA: {eta:.1f}s", end='\r')
                        last_update = current_time
            
            print(f"\n✅ File received successfully: {file_path}")
            print(f"🎯 File size: {file_size / (1024*1024):.2f} MB")
            
            return file_path
            
        except Exception as e:
            print(f"❌ Error receiving file: {e}")
            return None

    def extract_zip(self, zip_path):
        """Extract zip file and return list of video files"""
        try:
            extract_path = os.path.join(self.save_directory, "extracted")
            if not os.path.exists(extract_path):
                os.makedirs(extract_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
                print(f"📦 Extracted zip file to: {extract_path}")
                
                # Find video files
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
                video_files = []
                
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in video_extensions):
                            video_files.append(os.path.join(root, file))
                
                print(f"🎬 Found {len(video_files)} video file(s)")
                return video_files
                
        except Exception as e:
            print(f"❌ Error extracting zip: {e}")
            return []

    def create_panorama_from_video(self, video_path, skip_frames=5, resize_dims=(640, 360)):
        """Extract frames from video and create panorama"""
        try:
            print(f"\n🎬 Processing video: {os.path.basename(video_path)}")
            
            # Read the video
            cam = cv2.VideoCapture(video_path)
            
            if not cam.isOpened():
                print(f"❌ Could not open video file: {video_path}")
                return None
            
            # Get video properties
            total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cam.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            print(f"📹 Video info: {total_frames} frames, {fps:.2f} FPS, {duration:.2f}s duration")
            
            # Frame extraction
            currentframe = 0
            frames = []
            frame_count = 0
            
            print(f"🔄 Extracting every {skip_frames} frame(s)...")
            
            while True:
                ret, frame = cam.read()
                if not ret:
                    break
                    
                if frame_count % skip_frames == 0:
                    # Downscale frame for better processing
                    frame_resized = cv2.resize(frame, resize_dims)
                    
                    # Save frame for debugging
                    frame_name = os.path.join(self.data_directory, f'frame{currentframe}.jpg')
                    cv2.imwrite(frame_name, frame_resized)
                    
                    frames.append(frame_resized)
                    currentframe += 1
                    
                    if currentframe % 10 == 0:
                        print(f"📸 Extracted {currentframe} frames...")
                
                frame_count += 1
            
            # Release video
            cam.release()
            
            print(f"✅ Extracted {len(frames)} frames total")
            
            if len(frames) < 2:
                print("❌ Need at least 2 frames to create panorama")
                return None
            
            # Create panorama - Fixed OpenCV compatibility
            print("🔧 Stitching frames into panorama...")
            
            panorama_path = None
            
            try:
                # Try to use the newer Stitcher API first
                if hasattr(cv2, 'Stitcher_create'):
                    # OpenCV 4.x
                    stitcher_modes = [
                        (cv2.Stitcher_SCANS, "SCANS"),
                        (cv2.Stitcher_PANORAMA, "PANORAMA")
                    ]
                    
                    for mode, mode_name in stitcher_modes:
                        try:
                            print(f"🎯 Trying {mode_name} mode...")
                            stitcher = cv2.Stitcher_create(mode)
                            status, panorama = stitcher.stitch(frames)
                            
                            if status == cv2.Stitcher_OK:
                                # Save panorama
                                video_name = Path(video_path).stem
                                panorama_path = os.path.join(self.data_directory, f'panorama_{video_name}_{mode_name.lower()}.jpg')
                                cv2.imwrite(panorama_path, panorama)
                                print(f"✅ Panorama created successfully: {panorama_path}")
                                break
                            else:
                                print(f"❌ {mode_name} mode failed with status: {status}")
                                self.print_stitcher_error(status)
                                
                        except Exception as e:
                            print(f"❌ Error with {mode_name} mode: {e}")
                
                else:
                    # Fallback for older OpenCV versions (3.x)
                    print("🎯 Using legacy OpenCV Stitcher...")
                    stitcher = cv2.createStitcher(False)  # False for scans mode
                    status, panorama = stitcher.stitch(frames)
                    
                    if status == cv2.Stitcher_OK:
                        video_name = Path(video_path).stem
                        panorama_path = os.path.join(self.data_directory, f'panorama_{video_name}_legacy.jpg')
                        cv2.imwrite(panorama_path, panorama)
                        print(f"✅ Panorama created successfully: {panorama_path}")
                    else:
                        print(f"❌ Legacy stitcher failed with status: {status}")
                        self.print_stitcher_error(status)
                        
            except Exception as e:
                print(f"❌ Error during stitching: {e}")
            
            if panorama_path is None:
                print("❌ All stitching methods failed. Consider:")
                print("   - Using a video with more overlapping scenes")
                print("   - Adjusting skip_frames parameter")
                print("   - Ensuring camera movement is smooth and linear")
                
                # Save a sample of frames for manual inspection
                sample_frames = frames[::max(1, len(frames)//5)]  # Take 5 sample frames
                for i, frame in enumerate(sample_frames):
                    sample_path = os.path.join(self.data_directory, f'sample_frame_{i}.jpg')
                    cv2.imwrite(sample_path, frame)
                print(f"💡 Saved {len(sample_frames)} sample frames for inspection")
            
            return panorama_path
            
        except Exception as e:
            print(f"❌ Error creating panorama: {e}")
            return None
        finally:
            cv2.destroyAllWindows()

    def print_stitcher_error(self, status):
        """Print detailed stitcher error information"""
        error_messages = {
            1: "Need more images with better overlap",  # ERR_NEED_MORE_IMGS
            2: "Homography estimation failed - images may not overlap enough",  # ERR_HOMOGRAPHY_EST_FAIL  
            3: "Camera parameters adjustment failed"  # ERR_CAMERA_PARAMS_ADJUST_FAIL
        }
        
        # Try to use OpenCV constants if available, otherwise use numeric values
        try:
            error_messages.update({
                cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images with better overlap",
                cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed - images may not overlap enough",
                cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameters adjustment failed"
            })
        except AttributeError:
            pass  # Use numeric values for older OpenCV versions
        
        if status in error_messages:
            print(f"   💡 {error_messages[status]}")

    def process_received_videos(self, video_files):
        """Process all received video files - PLAY FIRST, then create panoramas"""
        print(f"\n🎬 Playing {len(video_files)} extracted video(s) FIRST...")
        
        # STEP 1: Play all videos first
        self.play_multiple_videos(video_files, auto_advance=True)
        
        print(f"\n🎨 Now creating panoramas from the videos...")
        
        # STEP 2: Then create panoramas
        panorama_results = []
        for video_file in video_files:
            print(f"\n{'='*60}")
            panorama_path = self.create_panorama_from_video(video_file)
            if panorama_path:
                panorama_results.append(panorama_path)
                print(f"🎉 Successfully created panorama: {os.path.basename(panorama_path)}")
            else:
                print(f"❌ Failed to create panorama for: {os.path.basename(video_file)}")
        
        return panorama_results

    def connect_to_server(self, host = 'localhost', port=8080):
        """Connect to server and receive video files"""
        print("🚀 Video Recording Client - Connecting to server...")
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((host, port))
            print(f"✅ Connected to video recording server at {host}:{port}")
            print("📺 Waiting for video recordings from server...")
            print("ℹ  Server will automatically send zip files when recording stops")
            print("🎬 Videos will be PLAYED FIRST, then panoramas will be created")
            print("-" * 60)

            while True:
                try:
                    # Receive message type
                    msg_type = s.recv(7)
                    if not msg_type:
                        print("📡 Server disconnected.")
                        break
                    
                    msg_type = msg_type.decode('utf-8').strip()
                    
                    if msg_type == 'FILE':
                        # Receive file
                        print("📥 Server is sending a video recording file...")
                        file_path = self.receive_file(s)
                        
                        if file_path:
                            print("🎉 Video file transfer completed successfully!")
                            
                            # Check if it's a zip file and extract
                            if file_path.endswith('.zip'):
                                print("📦 Extracting zip file...")
                                video_files = self.extract_zip(file_path)
                                
                                if video_files:
                                    print("🎬 PLAYING videos first, then creating panoramas...")
                                    panorama_results = self.process_received_videos(video_files)
                                    
                                    if panorama_results:
                                        print(f"\n🌟 Successfully created {len(panorama_results)} panorama(s):")
                                        for panorama in panorama_results:
                                            print(f"   📸 {os.path.basename(panorama)}")
                                    else:
                                        print("❌ No panoramas could be created")
                                else:
                                    print("❌ No video files found in zip")
                            
                            elif any(file_path.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']):
                                # Direct video file - PLAY FIRST, then create panorama
                                print("🎬 Playing received video FIRST...")
                                self.play_video(file_path)
                                
                                print("🎨 Now creating panorama from video...")
                                panorama_path = self.create_panorama_from_video(file_path)
                                if panorama_path:
                                    print(f"🌟 Panorama created: {os.path.basename(panorama_path)}")
                        else:
                            print("❌ File transfer failed!")
                        
                        print("-" * 60)
                        
                    elif msg_type == 'PING':
                        # Respond to server ping to maintain connection
                        s.send(b'PONG')
                        
                    elif msg_type == 'QUIT':
                        print("🔴 Server is closing connection.")
                        break
                    
                    else:
                        if msg_type:  # Only print if not empty
                            print(f"❓ Unknown message type: {msg_type}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ Connection error: {e}")
                    break

        except ConnectionRefusedError:
            print(f"❌ Could not connect to server at {host}:{port}")
            print("💡 Make sure:")
            print("   1. The server is running")
            print("   2. The IP address is correct")
            print("   3. Port is not blocked by firewall")
        except Exception as e:
            print(f"❌ Client error: {e}")
        finally:
            s.close()
            print("🔌 Client connection closed.")

    def process_local_video(self, video_path, play_first=True):
        """Process a local video file - PLAY FIRST, then create panorama"""
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return None
        
        print(f"🎬 Processing local video: {video_path}")
        
        if play_first:
            print("🎬 Playing video FIRST...")
            self.play_video(video_path)
            print("🎨 Now creating panorama...")
        
        panorama_path = self.create_panorama_from_video(video_path)
        
        return panorama_path


def main():
    # Create client instance
    client = VideoClientPanorama()
    
    print("🎯 Video Client with Panorama Creation - PLAY FIRST, PANORAMA SECOND")
    print("Choose an option:")
    print("1. Connect to server and receive videos")
    print("2. Process local video file")
    print("3. Play video file only")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == '1':
        # Get server details
        host = input("Enter server IP (press Enter for default localhost): ").strip()
        if not host:
            host = 'localhost'
        
        port_input = input("Enter server port (press Enter for default 8080): ").strip()
        if port_input:
            try:
                port = int(port_input)
            except ValueError:
                print("Invalid port, using default 8080")
                port = 8080
        else:
            port = 8080
        
        # Connect to server
        client.connect_to_server(host, port)
        
    elif choice == '2':
        # Process local video - PLAY FIRST, then panorama
        video_path = input("Enter path to video file: ").strip()
        play_first = input("Play video first before creating panorama? (y/n, default=y): ").strip().lower()
        play_first = play_first != 'n'
        
        panorama_path = client.process_local_video(video_path, play_first)
        
        if panorama_path:
            print(f"🌟 Panorama created successfully: {panorama_path}")
        else:
            print("❌ Failed to create panorama")
    
    elif choice == '3':
        # Just play a video
        video_path = input("Enter path to video file: ").strip()
        client.play_video(video_path, auto_close=False)
    
    else:
        print("❌ Invalid choice")
    
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()