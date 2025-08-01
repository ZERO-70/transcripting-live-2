# VLC Stream Setup Guide

## Method 1: UDP Streaming (Original approach)

### Steps:
1. **Start VLC first** (this is crucial for UDP)
2. In VLC: Media → Open Network Stream
3. Enter: `udp://@:1234`
4. Click Play (VLC will wait for the stream)
5. **Then** run your Python script: `python ffmpeg_stream.py`

### If UDP doesn't work:
- Try: `udp://127.0.0.1:1234` instead
- Check if port 1234 is blocked by firewall
- Make sure no other application is using port 1234

## Method 2: HTTP Streaming (Recommended)

### Steps:
1. Run your Python script with HTTP option: `python ffmpeg_stream.py http`
2. In VLC: Media → Open Network Stream  
3. Enter: `http://127.0.0.1:8080`
4. Click Play

### Alternative VLC Network URLs to try:
- `udp://@127.0.0.1:1234`
- `rtp://@:1234`
- `http://localhost:8080`

## Troubleshooting Commands:

Check if FFmpeg is working:
```bash
ffmpeg -version
```

Test if video file exists and is readable:
```bash
ffplay video.mp4
```

Check if port is in use:
```bash
netstat -tulpn | grep 1234
```
