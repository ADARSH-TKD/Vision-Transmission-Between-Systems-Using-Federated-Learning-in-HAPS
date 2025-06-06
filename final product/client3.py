import socket
import os
import struct
import time

def receive_file(s, save_directory="downloads"):
    """Receive a file from the server"""
    try:
        # Create downloads directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # Receive file size
        file_size_bytes = s.recv(8)
        if len(file_size_bytes) != 8:
            print("Error receiving file size")
            return False
            
        file_size = struct.unpack('!Q', file_size_bytes)[0]
        
        if file_size == 0:
            print("Server reported file error or file not found")
            return False
            
        print(f"\n🎥 Receiving video recording file of size: {file_size / (1024*1024):.2f} MB")
        
        # Receive file name length
        file_name_len_bytes = s.recv(4)
        file_name_len = struct.unpack('!I', file_name_len_bytes)[0]
        
        # Receive file name
        file_name_bytes = s.recv(file_name_len)
        file_name = file_name_bytes.decode('utf-8')
        
        # Full path for saving
        file_path = os.path.join(save_directory, file_name)
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
                    return False
                    
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
        
        # Show file info
        if file_name.endswith('.zip'):
            print(f"🗂  Zip file received - contains video recordings from server")
        
        return True
        
    except Exception as e:
        print(f"❌ Error receiving file: {e}")
        return False


def main():
    print("🚀 Video Recording Client - Connecting to server...")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Replace with server's IP address for different computers
    host = '192.168.31.43'  # Change this to server's IP
    port = 8080

    try:
        s.connect((host, port))
        print(f"✅ Connected to video recording server at {host}:{port}")
        print("📺 Waiting for video recordings from server...")
        print("ℹ  Server will automatically send zip files when recording stops")
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
                    if receive_file(s):
                        print("🎉 Video file transfer completed successfully!")
                        print("📹 Check the 'downloads' folder for your video recordings")
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
        print("   3. Port 7634 is not blocked by firewall")
    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        s.close()
        print("🔌 Client connection closed.")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()