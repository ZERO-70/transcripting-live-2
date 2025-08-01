# Audio Playback Feature Guide

## Overview

The live transcription system now supports real-time audio playback alongside transcription. This feature allows you to hear the audio stream while simultaneously viewing the transcribed text.

## Requirements

The audio playback feature requires the `sounddevice` library, which is already included in the project's `requirements.txt`.

To install manually if needed:
```bash
pip install sounddevice
```

## Usage

### Basic Audio Playback

Enable audio playback with default settings:
```bash
python src/transcription/live_transcribe.py --enable-audio
```

### Custom Volume

Set a specific volume level (0.0 to 1.0):
```bash
python src/transcription/live_transcribe.py --enable-audio --audio-volume 0.5
```

### Specific Audio Device

First, list available audio devices:
```bash
python src/transcription/live_transcribe.py --list-audio-devices
```

Then use a specific device by its index:
```bash
python src/transcription/live_transcribe.py --enable-audio --audio-device 2
```

### Combined with Other Features

Audio playback can be combined with all existing features:
```bash
# With HTTP stream and profanity filtering
python src/transcription/live_transcribe.py --stream http --enable-audio --audio-volume 0.7

# With model-based profanity filter
python src/transcription/live_transcribe.py --enable-audio --filter-type model --audio-volume 0.6
```

## Command Line Options

- `--enable-audio`: Enable live audio playback
- `--audio-volume`: Set playback volume (0.0-1.0, default: 0.7)
- `--audio-device`: Specify audio output device by index
- `--list-audio-devices`: List all available audio devices

## Technical Details

### Independence from Transcription

The audio playback system is designed to be completely independent from the transcription process:

- Uses a separate audio queue (`audio_playback_queue`)
- Runs in the audio device's callback thread
- Failures in audio playback don't affect transcription
- Can be enabled/disabled without changing transcription behavior

### Performance Considerations

- Audio is split into small chunks (512 samples by default) for smooth playback
- Separate buffer management prevents audio dropouts
- Uses float32 format for better quality
- Automatic volume clamping prevents audio distortion

### Buffer Management

- Larger playback buffer (2x transcription buffer) for smoother audio
- Automatic dropping of old audio data if buffer fills up
- Non-blocking operations ensure transcription isn't affected

## Troubleshooting

### No Audio Output

1. Check if sounddevice is installed:
   ```bash
   python3 -c "import sounddevice; print('sounddevice available')"
   ```

2. List audio devices to verify your output device:
   ```bash
   python src/transcription/live_transcribe.py --list-audio-devices
   ```

3. Try the default device first:
   ```bash
   python src/transcription/live_transcribe.py --enable-audio
   ```

### Audio Crackling or Distortion

1. Lower the volume:
   ```bash
   python src/transcription/live_transcribe.py --enable-audio --audio-volume 0.3
   ```

2. Try a different audio device:
   ```bash
   python src/transcription/live_transcribe.py --enable-audio --audio-device 1
   ```

### Performance Issues

If you experience performance issues with audio playback enabled:

1. The audio playback is designed to not interfere with transcription
2. Audio dropouts may occur under high CPU load but won't affect text output
3. Consider using a faster Whisper model (e.g., `--model tiny`)

## Configuration

Default configuration values in the script:
- `ENABLE_AUDIO_PLAYBACK = False`
- `AUDIO_PLAYBACK_VOLUME = 0.7`
- `AUDIO_PLAYBACK_DEVICE = None` (uses system default)
- `AUDIO_BUFFER_SIZE = 512`

These can be modified in the script if you want different defaults.

## Example Workflows

### Basic Monitoring
```bash
# Start with audio playback for live monitoring
python src/transcription/live_transcribe.py --enable-audio --audio-volume 0.5
```

### Production Transcription
```bash
# Full-featured transcription with audio monitoring
python src/transcription/live_transcribe.py \
    --stream http \
    --enable-audio \
    --audio-volume 0.6 \
    --filter-type enhanced \
    --model base
```

### Device Testing
```bash
# Test different audio devices
python src/transcription/live_transcribe.py --list-audio-devices
python src/transcription/live_transcribe.py --enable-audio --audio-device 2 --audio-volume 0.8
```
