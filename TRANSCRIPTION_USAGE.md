# 🎤 Live Transcription Usage Guide

## 🎯 Quick Start Commands

### **1. Dictionary-Based Filter (Recommended for Speed)**
```bash
# Using enhanced dictionary with 8600+ profanity words
python3 run.py transcribe-dict

# Or with custom model
python3 run.py transcribe-dict --model large
```

### **2. AI Model-Based Filter (Recommended for Accuracy)**
```bash
# Using default toxic-bert model
python3 run.py transcribe-model

# Using different toxicity model
python3 run.py transcribe-model --toxicity-model "unitary/toxic-bert"
python3 run.py transcribe-model --toxicity-model "martin-ha/toxic-comment-model"
```

### **3. No Filter (Raw Transcription)**
```bash
# Pure transcription without filtering
python3 run.py transcribe-nofilter
```

### **4. Default (Dictionary Filter)**
```bash
# Same as transcribe-dict
python3 run.py transcribe
```

## ⚙️ Advanced Options

### **Stream Sources**
```bash
# UDP stream (default - requires ffmpeg streaming)
python3 run.py transcribe-dict --stream udp

# HTTP stream (more reliable)
python3 run.py transcribe-dict --stream http
```

### **Whisper Models**
```bash
# Fast but less accurate
python3 run.py transcribe-dict --model tiny

# Balanced (default)
python3 run.py transcribe-dict --model base

# More accurate but slower
python3 run.py transcribe-dict --model small
python3 run.py transcribe-dict --model medium
python3 run.py transcribe-dict --model large
```

### **Languages**
```bash
# English (default)
python3 run.py transcribe-dict --language en

# Spanish
python3 run.py transcribe-dict --language es

# French
python3 run.py transcribe-dict --language fr

# Auto-detect
python3 run.py transcribe-dict --language auto
```

## 🔧 Direct Usage (Alternative)

If you prefer running directly:
```bash
cd src/transcription

# Dictionary filter
python3 live_transcribe.py --filter-type dictionary

# Model filter  
python3 live_transcribe.py --filter-type model

# No filter
python3 live_transcribe.py --no-filter

# Custom configurations
python3 live_transcribe.py --filter-type dictionary --filter-config ../../config/enhanced_profanity_config.json
python3 live_transcribe.py --filter-type model --model-config ../../config/model_profanity_config.json
```

## 📊 Filter Comparison

| Filter Type | Speed | Accuracy | Memory | Best For |
|-------------|-------|----------|---------|----------|
| **Dictionary** | ⚡⚡⚡ | ⭐⭐⭐ | 💾 | Real-time streaming |
| **AI Model** | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💾💾💾 | High accuracy needs |
| **No Filter** | ⚡⚡⚡⚡ | N/A | 💾 | Raw transcription |

## 🎯 Complete Workflow

### Step 1: Start Video Streaming
```bash
# Terminal 1: Start streaming
python3 run.py stream
```

### Step 2: Start Transcription
```bash
# Terminal 2: Start transcription with your preferred filter
python3 run.py transcribe-model    # AI-based filtering
# OR
python3 run.py transcribe-dict     # Dictionary-based filtering
```

### Step 3: View Results
- Real-time transcription appears in terminal
- Transcript saved to `output/transcript_YYYYMMDD_HHMMSS.txt`
- Filter statistics shown when stopped (Ctrl+C)

## 🛡️ Filter Configurations

### Dictionary Filter Features:
- ✅ 8600+ profanity words from multiple datasets
- ✅ Severity levels (mild, moderate, severe)
- ✅ Customizable actions (highlight, censor, remove, flag)
- ✅ Very fast processing
- ✅ Low memory usage

### AI Model Filter Features:
- ✅ Context-aware toxicity detection
- ✅ Handles misspellings and variations
- ✅ Toxicity scoring (0.0 to 1.0)
- ✅ Multiple AI models available
- ✅ Higher accuracy than dictionary

## 📁 Output Files

Transcripts are saved to:
```
output/transcript_20250801_HHMMSS.txt
```

## 🎮 Interactive Features

During transcription:
- **Ctrl+C**: Stop transcription and save
- Real-time filtering visualization
- Statistics display on exit
- Color-coded severity levels (in terminal)

---

**🎉 Your transcription system is ready!** Choose the filter type that best fits your needs.
