import subprocess
import sys
import time
import os

UDP_PORT = 1234  # UDP port
HTTP_PORT = 8080  # HTTP port for alternative streaming

# Get the correct path to video files
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
video_path = os.path.join(project_root, 'output', 'video1.mp4')

# Fallback to video.mp4 if video1.mp4 doesn't exist
if not os.path.exists(video_path):
    video_path = os.path.join(project_root, 'output', 'video.mp4')

VIDEO_FILE = video_path

# FFmpeg command to stream video over UDP (supports multiple clients)
UDP_FFMPEG_CMD = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
    "-c:v", "libx264",  # Re-encode for better compatibility
    "-preset", "ultrafast",  # Fast encoding
    "-c:a", "aac",
    "-b:a", "128k",
    "-f", "mpegts",
    f"udp://127.0.0.1:{UDP_PORT}?pkt_size=1316"  # Add packet size for UDP
]

# Alternative: HTTP streaming (more reliable for testing)
HTTP_FFMPEG_CMD = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-c:a", "aac",
    "-b:a", "128k",
    "-f", "flv",  # FLV format for HTTP streaming
    f"rtmp://127.0.0.1:{HTTP_PORT}/live/stream"
]

# Simple HTTP streaming option - supports multiple connections
SIMPLE_HTTP_CMD = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-c:a", "aac",
    "-f", "mpegts",
    "-listen", "1",
    "-listen_timeout", "-1",  # Don't timeout waiting for connections
    "-multiple_requests", "1",  # Allow multiple HTTP requests/connections
    f"http://127.0.0.1:{HTTP_PORT}"
]

def stream_udp():
    """Stream via UDP - requires VLC to be listening first"""
    print(f"Streaming {VIDEO_FILE} via UDP at udp://127.0.0.1:{UDP_PORT}")
    print("IMPORTANT: Start VLC first and open network stream: udp://@:1234")
    print("Press Ctrl+C to stop.")
    try:
        subprocess.run(UDP_FFMPEG_CMD)
    except KeyboardInterrupt:
        print("\nStreaming stopped.")

def stream_http():
    """Stream via HTTP - supports multiple connections (VLC + transcription)"""
    print(f"Streaming {VIDEO_FILE} via HTTP at http://127.0.0.1:{HTTP_PORT}")
    print("Multiple connections supported:")
    print("  - VLC: Open network stream: http://127.0.0.1:8080")
    print("  - Live transcription can connect simultaneously")
    print("Press Ctrl+C to stop.")
    try:
        subprocess.run(SIMPLE_HTTP_CMD)
    except KeyboardInterrupt:
        print("\nStreaming stopped.")

def main():
    # Check if video file exists
    if not os.path.exists(VIDEO_FILE):
        print("❌ Error: Video file not found!")
        print(f"   Looking for: {VIDEO_FILE}")
        print(f"   Available videos in output/:")
        output_dir = os.path.join(os.path.dirname(VIDEO_FILE))
        if os.path.exists(output_dir):
            videos = [f for f in os.listdir(output_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
            for video in videos:
                print(f"   - {video}")
        else:
            print("   Output directory not found!")
        return
    
    print(f"📹 Using video file: {os.path.basename(VIDEO_FILE)}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        stream_http()
    else:
        print("Choose streaming method:")
        print("1. UDP (default) - requires VLC to be ready first")
        print("2. HTTP - more reliable, VLC can connect anytime")
        
        choice = input("Enter 1 or 2 (or press Enter for UDP): ").strip()
        
        if choice == "2":
            stream_http()
        else:
            stream_udp()

if __name__ == "__main__":
    main()
