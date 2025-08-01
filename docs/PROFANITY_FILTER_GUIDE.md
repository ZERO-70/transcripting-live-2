# Profanity Filtering for Live Transcription

This document explains the profanity filtering feature added to the live transcription system.

## Overview

The profanity filter provides configurable content filtering for transcribed text, helping to maintain appropriate content standards in live transcription output.

## Features

### 🛡️ Multi-Level Filtering
- **Mild**: Common swear words (damn, hell, crap) → Replaced with asterisks (d**n)
- **Moderate**: Strong profanity (f***, s***) → Replaced with [FILTERED]
- **Severe**: Highly offensive content → Completely removed

### ⚙️ Configurable Actions
- **Asterisk**: Replace with asterisks keeping first/last letters
- **Placeholder**: Replace with [FILTERED] 
- **Remove**: Remove the word entirely
- **Flag**: Keep word but add [!] flag

### 📊 Statistics Tracking
- Total words processed
- Words filtered by severity level
- Overall filter percentage rate

## Usage

### Basic Usage
```bash
# Run with profanity filtering enabled (default)
/usr/bin/python3 live_transcribe.py

# Disable profanity filtering
/usr/bin/python3 live_transcribe.py --no-filter

# Use custom filter configuration
/usr/bin/python3 live_transcribe.py --filter-config my_config.json
```

### Create Configuration File
```bash
# Create a sample configuration file
/usr/bin/python3 live_transcribe.py --create-filter-config
```

### Configuration File Format
```json
{
  "word_lists": {
    "mild": ["damn", "hell", "crap", "bloody"],
    "moderate": ["shit", "fuck", "bitch", "ass"],
    "severe": ["nigger", "faggot", "retard"]
  },
  "actions": {
    "mild": "asterisk",
    "moderate": "placeholder", 
    "severe": "remove"
  },
  "custom_replacements": {
    "fuck": "fudge",
    "shit": "shoot"
  }
}
```

## Output Examples

### Console Output
```
[12.3s] This is a d**n good test
[15.8s] What the [FILTERED] is happening here? [🛡️ Filtered: 1 words]
[18.2s] Clean text with no profanity
```

### File Output
When saving to transcript files, both original and filtered versions are saved:
```
[12.3s] [ORIGINAL] This is a damn good test
[12.3s] [FILTERED] This is a d**n good test
```

## Configuration Options

### Filter Actions Available
1. **asterisk**: d**n, f**k (preserves first/last character)
2. **placeholder**: [FILTERED]
3. **remove**: (word completely removed)
4. **flag**: damn[!] (flagged but visible)

### Severity Levels
- **MILD**: Minor profanity, typically censored with asterisks
- **MODERATE**: Strong profanity, replaced with placeholders
- **SEVERE**: Highly offensive content, removed entirely

### Custom Replacements
You can define specific word replacements:
- "fuck" → "fudge"
- "shit" → "shoot"

## Statistics Output

At the end of transcription, filtering statistics are displayed:

```
🛡️ Profanity Filter Statistics:
   Words processed: 156
   Words filtered: 8
   Filter rate: 5.13%
   By severity:
     MILD: 3
     MODERATE: 4
     SEVERE: 1
```

## Integration Details

The profanity filter integrates seamlessly with the existing transcription system:

1. **No Performance Impact**: Filtering happens after transcription
2. **Optional Feature**: Can be disabled with `--no-filter`
3. **Configurable**: Customize word lists and actions
4. **Preserves Original**: Both versions saved to transcript file
5. **Statistics**: Track filtering effectiveness

## Customization

### Adding Words
```python
from profanity_filter import ProfanityFilter, SeverityLevel

filter = ProfanityFilter()
filter.add_word("newword", SeverityLevel.MODERATE)
filter.save_config("my_config.json")
```

### Changing Actions
```python
from profanity_filter import FilterAction

filter.set_action(SeverityLevel.MILD, FilterAction.PLACEHOLDER)
```

## Privacy and Offline Operation

- **Fully Offline**: No external API calls required
- **Local Processing**: All filtering done locally
- **Configurable**: Complete control over word lists
- **Privacy Friendly**: No data sent to external services

## Best Practices

1. **Review Configuration**: Customize word lists for your use case
2. **Test First**: Use `--create-filter-config` to create sample config
3. **Context Matters**: Some words may be appropriate in certain contexts
4. **Regular Updates**: Review and update word lists periodically
5. **Backup Originals**: Always keep original transcripts for reference

## Troubleshooting

### Filter Not Working
- Check if `profanity_config.json` exists
- Verify word lists in configuration
- Ensure `--no-filter` is not set

### Performance Issues
- Filter processing is minimal overhead
- Use smaller word lists if needed
- Consider disabling statistics with `SHOW_FILTER_STATS = False`

### Custom Configuration
- Use `--create-filter-config` to generate template
- Modify word lists as needed
- Test with sample text before live use
