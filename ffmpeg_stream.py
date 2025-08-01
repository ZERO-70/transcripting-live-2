import subprocess
import sys
import time

UDP_PORT = 1234  # UDP port
HTTP_PORT = 8080  # HTTP port for alternative streaming
VIDEO_FILE = "video.mp4"

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

# Simple HTTP streaming option
SIMPLE_HTTP_CMD = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-i", VIDEO_FILE,
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-c:a", "aac",
    "-f", "mpegts",
    "-listen", "1",  # Listen for incoming connections
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
    """Stream via HTTP - VLC can connect anytime"""
    print(f"Streaming {VIDEO_FILE} via HTTP at http://127.0.0.1:{HTTP_PORT}")
    print("VLC: Open network stream: http://127.0.0.1:8080")
    print("Press Ctrl+C to stop.")
    try:
        subprocess.run(SIMPLE_HTTP_CMD)
    except KeyboardInterrupt:
        print("\nStreaming stopped.")

def main():
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
