# Live Transcription Setup Guide

## Installation

Make sure you have the required packages installed:
```bash
pip install faster-whisper numpy
```

## Usage

### Basic Usage
```bash
# Transcribe UDP stream (default)
python3 live_transcribe.py

# Transcribe HTTP stream  
python3 live_transcribe.py --stream http

# Use different model (better accuracy, slower)
python3 live_transcribe.py --model small

# Different language
python3 live_transcribe.py --language es
```

### Complete Workflow

1. **Start your video stream:**
   ```bash
   python3 ffmpeg_stream.py
   # Choose option 2 for HTTP streaming (recommended)
   ```

2. **In another terminal, start transcription:**
   ```bash
   python3 live_transcribe.py --stream http
   ```

## Features

✅ **Auto-reconnection** - Handles network interruptions  
✅ **Buffer management** - Prevents memory buildup  
✅ **File logging** - Saves transcripts with timestamps  
✅ **Multiple streams** - Supports both UDP and HTTP  
✅ **Model selection** - Choose speed vs accuracy  
✅ **Error handling** - Graceful failure recovery  

## Whisper Models

| Model  | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| tiny   | Fast  | Basic    | Real-time, CPU limited |
| small  | Medium| Good     | Balanced performance |
| medium | Slow  | Better   | Higher accuracy needed |

## Troubleshooting

### "Could not connect to stream"
- Make sure your streaming script is running first
- Check if ports 1234 (UDP) or 8080 (HTTP) are available
- Try HTTP streaming instead of UDP

### "Transcription error"
- Check if the stream has audio
- Try a different Whisper model (--model tiny)
- Ensure sufficient CPU/memory

### "Audio buffer full"
- This is normal - old audio is dropped to prevent lag
- Consider using a faster Whisper model

## Output Files

Transcripts are automatically saved to:
`transcript_YYYYMMDD_HHMMSS.txt`

Example content:
```
[12.3s] Hello, this is a test of the transcription system
[15.7s] The audio quality is quite good
[19.2s] Transcription is working as expected
```
