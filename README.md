# Live Transcription Stream Project

A real-time transcription system with advanced profanity filtering capabilities and live audio playback.

## ✨ Key Features

- **Real-time Transcription**: Live speech-to-text using OpenAI Whisper
- **Advanced Profanity Filtering**: Multiple filtering approaches (dictionary, AI model-based)
- **🔊 Live Audio Playback**: Hear the stream audio while viewing transcriptions
- **Multiple Stream Support**: UDP and HTTP streaming protocols
- **Flexible Configuration**: Customizable filters, models, and audio settings
- **Easy-to-Use Interface**: Simple command-line runner for all features

## 📁 Project Structure

```
📁 stream/ (root)
├── 📁 src/              # Main source code
│   ├── 📁 filters/      # Profanity filtering implementations
│   │   ├── profanity_filter.py           # Dictionary-based filter
│   │   ├── enhanced_profanity_filter.py  # Enhanced dictionary filter
│   │   ├── model_profanity_filter.py     # AI model-based filter
│   │   └── test_profanity_filter.py      # Filter tests
│   ├── 📁 transcription/                  # Transcription functionality
│   │   └── live_transcribe.py            # Real-time transcription
│   └── 📁 streaming/                      # Streaming functionality
│       └── ffmpeg_stream.py              # Video streaming
├── 📁 config/           # Configuration files
│   ├── profanity_config.json            # Basic filter config
│   ├── enhanced_profanity_config.json   # Enhanced filter config
│   └── model_profanity_config.json      # Model filter config
├── 📁 data/             # Data files and datasets  
│   ├── hurtlex_EN.tsv                   # Offensive words dataset
│   └── offensive_words_en.txt           # Additional word list
├── 📁 tests/            # Test files
│   ├── test_comprehensive_filters.py    # Comprehensive tests
│   └── test_model_filter.py             # Model filter tests
├── 📁 demos/            # Demo scripts
│   ├── demo_filter_comparison.py        # Filter comparison demo
│   ├── demo_model_filter.py             # Model filter demo
│   └── demo_red_highlighting.py         # Highlighting demo
├── 📁 docs/             # Documentation
│   ├── COMPLETE_FILTER_GUIDE.md         # Complete filtering guide
│   ├── MODEL_FILTER_GUIDE.md            # Model filter guide
│   ├── PROFANITY_FILTER_GUIDE.md        # Profanity filter guide
│   ├── RED_HIGHLIGHTING_GUIDE.md        # Highlighting guide
│   ├── TRANSCRIPTION_GUIDE.md           # Transcription guide
│   ├── VLC_SETUP.md                     # VLC setup guide
│   └── IMPLEMENTATION_SUMMARY.md        # Implementation summary
├── 📁 output/           # Generated files
│   ├── video.mp4                        # Sample videos
│   ├── video1.mp4
│   └── transcript_20250801_204709.txt   # Generated transcripts
├── 📁 temp/             # Temporary files
│   ├── hls/                             # HLS streaming files
│   └── __pycache__/                     # Python cache
└── 📄 requirements.txt  # Python dependencies
```

## 🚀 Features

- **Real-time Transcription**: Live speech-to-text conversion
- **Multiple Profanity Filters**:
  - Dictionary-based filtering
  - Enhanced pattern matching
  - AI model-based toxicity detection
- **Streaming Support**: FFmpeg-based video streaming
- **Configurable**: JSON-based configuration system
- **Red Highlighting**: Visual indication of filtered content

## 📋 Requirements

### Prerequisites
- Python 3.8+
- FFmpeg (for streaming)
- VLC media player (optional, for viewing streams)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Environment Setup:**
Copy the example environment file and configure your API tokens:
```bash
cp .env.example .env
```

Edit `.env` and add your Hugging Face token:
```
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

Get your Hugging Face token from: https://huggingface.co/settings/tokens

> ⚠️ **Important**: Never commit the `.env` file to version control. It's already included in `.gitignore`.

## 🎯 Quick Start

### Using the Runner Script (Recommended)

The easiest way to run any component:

```bash
## 🚀 Quick Start

### With Audio Playback (New!)

```bash
# Basic transcription with live audio playback
python3 run.py transcribe-audio

# With AI model-based filtering and audio
python3 run.py transcribe-audio-model

# List available audio devices first
python3 run.py list-audio-devices

# Custom audio settings
python3 run.py transcribe-audio --audio-volume 0.5 --audio-device 0
```

### Standard Transcription

```bash
# Different filter types
python3 run.py transcribe-dict       # Dictionary-based filter
python3 run.py transcribe-model     # AI model-based filter (accurate)
python3 run.py transcribe-nofilter  # No filtering (raw transcription)
python3 run.py transcribe           # Default (dictionary filter)

# Add audio to any existing component
python3 run.py transcribe-model --enable-audio --audio-volume 0.6
```

# Demo scripts
python3 run.py demo-comparison      # Compare all filter types
python3 run.py demo-model          # Model-based filter demo
python3 run.py demo-highlight      # Red highlighting demo

# Test scripts
python3 run.py test-comprehensive  # Run all tests
python3 run.py test-model          # Test model filters

# Streaming
python3 run.py stream              # Start video streaming
```

### Audio Playback Features

```bash
# List available audio devices
python3 run.py list-audio-devices

# Audio-enabled transcription variants
python3 run.py transcribe-audio              # Basic with audio
python3 run.py transcribe-audio-model        # Model filter + audio
python3 run.py transcribe-audio-dict         # Dictionary filter + audio

# Audio options for any transcription
python3 run.py transcribe --enable-audio --audio-volume 0.7 --audio-device 2

# HTTP streaming with audio
python3 run.py transcribe-audio --stream http --audio-volume 0.5
```

### Advanced Transcription Options

```bash
# Custom Whisper models
python3 run.py transcribe-model --model large

# Different languages
python3 run.py transcribe-dict --language es

# HTTP streaming (more reliable)
python3 run.py transcribe-dict --stream http

# Custom toxicity models
python3 run.py transcribe-model --toxicity-model "unitary/toxic-bert"
```

### Direct Usage

If you prefer to run components directly:

```bash
# Set up Python path first
export PYTHONPATH="$PWD/src:$PWD/src/filters:$PWD/src/transcription:$PWD/src/streaming:$PYTHONPATH"

# Then run components
cd src/transcription && python3 live_transcribe.py --filter-type model
cd demos && python3 demo_filter_comparison.py
cd tests && python3 test_comprehensive_filters.py
```

## 📖 Documentation

### Audio Features
- `AUDIO_PLAYBACK_GUIDE.md` - Comprehensive audio playback guide
- `RUN_PY_AUDIO_GUIDE.md` - Updated run.py usage with audio features

### Core Documentation
- See `docs/` folder for detailed guides
- Configuration examples in `config/` folder
- Demo scripts in `demos/` folder

## 🔧 Configuration

Edit configuration files in `config/` to customize:
- Filter sensitivity levels
- Action types (highlight, censor, remove)
- Model parameters
- Toxicity thresholds

---

**Author**: ZERO-70  
**Version**: 1.0.0
