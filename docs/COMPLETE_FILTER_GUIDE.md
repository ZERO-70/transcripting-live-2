# Model-Based vs Dictionary-Based Profanity Filtering Guide

## Overview

Your live transcription system now supports two types of profanity filtering:

1. **Dictionary-Based Filtering** - Fast, predictable word matching
2. **Model-Based Filtering** - AI-powered toxicity detection using BERT models

## Quick Start

### Using Dictionary Filter (Default)
```bash
python3 live_transcribe.py --filter-type dictionary
```

### Using Model-Based Filter  
```bash
python3 live_transcribe.py --filter-type model
```

### Disable Filtering
```bash
python3 live_transcribe.py --no-filter
```

## Filter Comparison

| Feature | Dictionary | Model-Based |
|---------|------------|-------------|
| **Speed** | ~1ms per sentence | ~100ms per sentence |
| **Accuracy** | Good for explicit words | Better for context/toxicity |
| **Setup Time** | Instant | ~3 minutes (first time) |
| **Memory Usage** | Low (~10MB) | High (~500MB) |
| **Internet Required** | No | Yes (first download) |
| **Context Awareness** | No | Yes |

## Available Models

The system includes several toxicity detection models:

### Primary Model (Recommended)
- **`unitary/toxic-bert`** - Fast, accurate toxicity detection
- Size: ~440MB
- Speed: ~100ms per sentence
- Best balance of speed and accuracy

### Alternative Models
- **`martin-ha/toxic-comment-model`** - Alternative toxic detection
- **`cardiffnlp/twitter-roberta-base-offensive`** - Social media focused
- **`cardiffnlp/twitter-roberta-base-hate`** - Hate speech detection

## Authentication

The model-based filter requires a HuggingFace token for authentication:

1. **Get your token**: Visit https://huggingface.co/settings/tokens
2. **Set up environment**: Copy `.env.example` to `.env` and add your token:
   ```
   HUGGINGFACE_TOKEN=your_token_here
   ```
3. **Security**: The token is loaded from environment variables for security

> ⚠️ **Never commit your actual token to version control!**

## Configuration

### Dictionary Filter Config
File: `enhanced_profanity_config.json`
```json
{
  "actions": {
    "mild": "replace",
    "moderate": "asterisk", 
    "severe": "remove"
  },
  "custom_replacements": {
    "damn": "darn",
    "shit": "shoot"
  }
}
```

### Model Filter Config  
File: `model_profanity_config.json`
```json
{
  "model_config": {
    "thresholds": {
      "mild": 0.7,
      "moderate": 0.8,
      "severe": 0.9
    },
    "actions": {
      "mild": "red_highlight",
      "moderate": "red_highlight",
      "severe": "red_highlight"
    }
  }
}
```

## Advanced Usage

### Custom Model
```bash
python3 live_transcribe.py \\
  --filter-type model \\
  --toxicity-model "martin-ha/toxic-comment-model"
```

### Custom Config Files
```bash
python3 live_transcribe.py \\
  --filter-type dictionary \\
  --filter-config "my_custom_config.json"
```

### Mixed Usage
```bash
# Use model filter for live transcription  
python3 live_transcribe.py --filter-type model --stream udp

# Use dictionary filter for HTTP stream
python3 live_transcribe.py --filter-type dictionary --stream http
```

## Performance Tips

### For Real-Time Use
- **Dictionary filter** recommended for live streaming
- Use `--model base` or `--model tiny` for faster Whisper processing
- Model filter works well but adds ~100ms latency

### For Post-Processing
- **Model filter** recommended for better accuracy
- Use `--model large` for better transcription quality
- Process in batches for efficiency

## Examples

### Example 1: Clean Text
```
Input:  "Hello everyone, welcome to the presentation"
Dictionary: "Hello everyone, welcome to the presentation" (0 filtered)
Model:      "Hello everyone, welcome to the presentation" (0 filtered)
```

### Example 2: Explicit Profanity  
```
Input:  "This damn thing is broken"
Dictionary: "This darn thing is broken" (1 filtered)
Model:      "This damn thing is broken" (0 filtered - not toxic enough)
```

### Example 3: Toxic Context
```
Input:  "You're being such a jerk today"
Dictionary: "You're being such a jerk today" (0 filtered)
Model:      "You're being such a jerk today" (potentially filtered if above threshold)
```

## Troubleshooting

### Model Not Loading
1. Check internet connection
2. Verify HuggingFace token is valid
3. Try alternative model:
   ```bash
   python3 live_transcribe.py --toxicity-model "martin-ha/toxic-comment-model"
   ```

### Slow Performance
1. Use dictionary filter for real-time: `--filter-type dictionary`
2. Use smaller Whisper model: `--model tiny`
3. Ensure CPU has sufficient resources

### Too Aggressive Filtering
1. Adjust thresholds in config file (increase values 0.7 → 0.8)
2. Use dictionary filter for predictable results
3. Disable filtering: `--no-filter`

### Too Lenient Filtering  
1. Lower thresholds in config file (0.7 → 0.5)
2. Add custom words to dictionary filter
3. Use stricter model like hate speech detection

## Testing

### Test Both Filters
```bash
python3 test_model_filter.py
```

### Test Dictionary Only
```bash  
python3 test_profanity_filter.py
```

### Test Live Without Stream
```bash
python3 live_transcribe.py --help
```

## Best Practices

1. **Start with dictionary filter** - easier to configure and debug
2. **Test thresholds** - adjust based on your content needs  
3. **Monitor performance** - model filter uses more resources
4. **Custom vocabulary** - add domain-specific terms to configs
5. **Backup filtering** - system falls back gracefully if model fails

## Configuration Files

Generate sample configurations:
```bash
# Dictionary filter config
python3 live_transcribe.py --create-filter-config

# Model filter config  
python3 live_transcribe.py --create-model-config
```

Your system is now ready for both basic word filtering and advanced AI-powered toxicity detection! 🚀
