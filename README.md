# Live Transcription Stream Project

A real-time transcription system with advanced profanity filtering capabilities.

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

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Quick Start

### Using the Runner Script (Recommended)

The easiest way to run any component:

```bash
# Live transcription with different filters
python3 run.py transcribe-dict      # Dictionary-based filter (fast)
python3 run.py transcribe-model     # AI model-based filter (accurate)
python3 run.py transcribe-nofilter  # No filtering (raw transcription)
python3 run.py transcribe           # Default (dictionary filter)

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
