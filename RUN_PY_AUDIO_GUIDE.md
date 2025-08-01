# Updated run.py Usage Guide

## Overview

The `run.py` file has been updated to include comprehensive audio playback support for all transcription components. You can now easily run transcription with live audio playback using simple commands.

## New Audio-Enabled Components

### Core Transcription with Audio
- `transcribe-audio`: Basic transcription with audio playback and dictionary filter
- `transcribe-audio-model`: Transcription with audio playback and model-based filter  
- `transcribe-audio-dict`: Transcription with audio playback and dictionary filter (explicit)

### Audio Device Management
- `list-audio-devices`: List all available audio output devices

## Usage Examples

### Quick Start with Audio

```bash
# Basic transcription with audio playback
python3 run.py transcribe-audio

# With model-based profanity filter and audio
python3 run.py transcribe-audio-model

# With custom volume
python3 run.py transcribe-audio --audio-volume 0.5

# With specific audio device
python3 run.py transcribe-audio --audio-device 0
```

### Audio Device Discovery

```bash
# First, list available devices
python3 run.py list-audio-devices

# Then use a specific device
python3 run.py transcribe-audio --audio-device 2
```

### Adding Audio to Existing Components

You can add audio playback to any existing transcription component:

```bash
# Add audio to basic transcription
python3 run.py transcribe --enable-audio

# Add audio to model-based transcription  
python3 run.py transcribe-model --enable-audio --audio-volume 0.6

# Add audio to HTTP stream transcription
python3 run.py transcribe --stream http --enable-audio
```

### Advanced Audio Configuration

```bash
# Custom volume and device
python3 run.py transcribe-audio --audio-volume 0.3 --audio-device 5

# Different Whisper model with audio
python3 run.py transcribe-audio --model tiny --audio-volume 0.8

# Different language with audio
python3 run.py transcribe-audio --language es --audio-volume 0.6

# HTTP stream with audio and custom settings
python3 run.py transcribe-audio --stream http --audio-volume 0.7 --audio-device 0
```

## Command Reference

### Audio-Specific Arguments

- `--enable-audio`: Enable live audio playback for any transcription component
- `--audio-volume X.X`: Set playback volume (0.0 to 1.0, default: 0.7)  
- `--audio-device N`: Use specific audio device by index
- `--no-filter`: Disable profanity filtering (can be combined with audio)

### New Components

| Component | Description |
|-----------|-------------|
| `transcribe-audio` | Basic transcription with audio + dictionary filter |
| `transcribe-audio-model` | Transcription with audio + model-based filter |
| `transcribe-audio-dict` | Transcription with audio + dictionary filter (explicit) |
| `list-audio-devices` | Show all available audio output devices |

### Existing Components (with new audio support)

All existing components now support the `--enable-audio` flag:

| Component | Description | Audio Support |
|-----------|-------------|---------------|
| `transcribe` | Basic transcription | ✅ `--enable-audio` |
| `transcribe-model` | Model-based filter | ✅ `--enable-audio` |
| `transcribe-dict` | Dictionary filter | ✅ `--enable-audio` |
| `transcribe-nofilter` | No profanity filter | ✅ `--enable-audio` |

## Workflow Examples

### For Content Monitoring
```bash
# Start with device discovery
python3 run.py list-audio-devices

# Monitor with audio at comfortable volume
python3 run.py transcribe-audio --audio-volume 0.4 --audio-device 0
```

### For Production Transcription
```bash
# Full-featured with audio monitoring
python3 run.py transcribe-audio-model --stream http --audio-volume 0.5
```

### For Testing/Development
```bash
# Quick test with audio
python3 run.py transcribe-audio --model tiny --audio-volume 0.3
```

### For Different Languages
```bash
# Spanish transcription with audio
python3 run.py transcribe-audio --language es --audio-volume 0.6
```

## Backward Compatibility

All existing `run.py` commands continue to work exactly as before:

```bash
# These work unchanged
python3 run.py transcribe
python3 run.py transcribe-model --toxicity-model some-model  
python3 run.py transcribe --stream http
python3 run.py demo-comparison
```

## Troubleshooting

### No Audio Output
```bash
# Check available devices
python3 run.py list-audio-devices

# Try default device with low volume
python3 run.py transcribe-audio --audio-volume 0.2
```

### Audio Quality Issues
```bash
# Try different device
python3 run.py transcribe-audio --audio-device 1 --audio-volume 0.4

# Use faster model for better performance
python3 run.py transcribe-audio --model tiny --audio-volume 0.5
```

## Configuration Summary

The `run.py` now provides a complete interface for all audio features while maintaining full backward compatibility. The new audio-enabled components make it easy to start transcription with audio playback using simple, memorable commands.

All audio features are optional and gracefully degrade if the `sounddevice` library is not available, ensuring the system works in all environments.
