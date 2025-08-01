"""
Profanity Filter Module for Live Transcription
Provides configurable content filtering for text transcripts.
"""

import re
import json
import os
from typing import List, Dict, Tuple, Set, Optional, Union
from enum import Enum

class FilterAction(Enum):
    """Actions to take when profanity is detected."""
    ASTERISK = "asterisk"      # Replace with asterisks: "f***"
    PLACEHOLDER = "placeholder" # Replace with [FILTERED]
    REMOVE = "remove"          # Remove the word entirely
    FLAG = "flag"              # Keep word but add [!] flag
    RED_HIGHLIGHT = "red_highlight"  # Highlight in red on console

class SeverityLevel(Enum):
    """Severity levels for different types of content."""
    MILD = 1
    MODERATE = 2
    SEVERE = 3

class ProfanityFilter:
    """
    A configurable profanity filter for text content.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.word_lists: Dict[SeverityLevel, Set[str]] = {
            SeverityLevel.MILD: set(),
            SeverityLevel.MODERATE: set(),
            SeverityLevel.SEVERE: set()
        }
        self.actions: Dict[SeverityLevel, FilterAction] = {
            SeverityLevel.MILD: FilterAction.RED_HIGHLIGHT,
            SeverityLevel.MODERATE: FilterAction.RED_HIGHLIGHT,
            SeverityLevel.SEVERE: FilterAction.RED_HIGHLIGHT
        }
        self.custom_replacements: Dict[str, str] = {}
        self.stats: Dict[str, Union[int, Dict[str, int]]] = {
            "total_words_processed": 0,
            "words_filtered": 0,
            "by_severity": {
                "MILD": 0,
                "MODERATE": 0,
                "SEVERE": 0
            }
        }
        
        # Load configuration
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        else:
            self._load_default_words()
    
    def _load_default_words(self):
        """Load a basic set of profanity words organized by severity."""
        # Mild profanity (common swear words)
        mild_words = {
            "damn", "hell", "crap", "bloody", "darn", "piss"
        }
        
        # Moderate profanity
        moderate_words = {
            "shit", "fuck", "bitch", "ass", "asshole", "bastard", 
            "dickhead", "prick", "douche", "jackass"
        }
        
        # Severe profanity (highly offensive)
        severe_words = {
            # Racial slurs and highly offensive terms
            "nigger", "nigga", "faggot", "retard", "spic", "chink",
            "kike", "wetback", "raghead", "towelhead"
        }
        
        self.word_lists[SeverityLevel.MILD] = mild_words
        self.word_lists[SeverityLevel.MODERATE] = moderate_words
        self.word_lists[SeverityLevel.SEVERE] = severe_words
    
    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load word lists
            for severity_str, words in config.get('word_lists', {}).items():
                severity = SeverityLevel[severity_str.upper()]
                self.word_lists[severity] = set(words)
            
            # Load actions
            for severity_str, action_str in config.get('actions', {}).items():
                severity = SeverityLevel[severity_str.upper()]
                self.actions[severity] = FilterAction[action_str.upper()]
            
            # Load custom replacements
            self.custom_replacements = config.get('custom_replacements', {})
            
        except Exception as e:
            print(f"⚠️ Error loading profanity config: {e}. Using defaults.")
            self._load_default_words()
    
    def save_config(self, config_file: str):
        """Save current configuration to JSON file."""
        config = {
            'word_lists': {
                severity.name.lower(): list(words) 
                for severity, words in self.word_lists.items()
            },
            'actions': {
                severity.name.lower(): action.value 
                for severity, action in self.actions.items()
            },
            'custom_replacements': self.custom_replacements
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def add_word(self, word: str, severity: SeverityLevel):
        """Add a word to the filter list."""
        self.word_lists[severity].add(word.lower())
    
    def remove_word(self, word: str, severity: Optional[SeverityLevel] = None):
        """Remove a word from the filter list."""
        if severity:
            self.word_lists[severity].discard(word.lower())
        else:
            # Remove from all lists
            for word_set in self.word_lists.values():
                word_set.discard(word.lower())
    
    def set_action(self, severity: SeverityLevel, action: FilterAction):
        """Set the action for a specific severity level."""
        self.actions[severity] = action
    
    def _find_profanity(self, text: str) -> List[Tuple[str, SeverityLevel, int, int]]:
        """
        Find profanity in text and return list of (word, severity, start, end) tuples.
        """
        found = []
        words = re.finditer(r'\b\w+\b', text.lower())
        
        for match in words:
            word = match.group()
            start, end = match.span()
            
            # Check each severity level
            for severity in [SeverityLevel.SEVERE, SeverityLevel.MODERATE, SeverityLevel.MILD]:
                if word in self.word_lists[severity]:
                    found.append((word, severity, start, end))
                    break
        
        return found
    
    def _apply_filter(self, original_word: str, word: str, severity: SeverityLevel, for_console: bool = True) -> str:
        """Apply the appropriate filter action to a word."""
        # Check for custom replacement first
        if word in self.custom_replacements:
            return self.custom_replacements[word]
        
        action = self.actions[severity]
        
        if action == FilterAction.ASTERISK:
            if len(original_word) <= 2:
                return "*" * len(original_word)
            else:
                return original_word[0] + "*" * (len(original_word) - 2) + original_word[-1]
        
        elif action == FilterAction.PLACEHOLDER:
            return "[FILTERED]"
        
        elif action == FilterAction.REMOVE:
            return ""
        
        elif action == FilterAction.FLAG:
            return f"{original_word}[!]"
        
        elif action == FilterAction.RED_HIGHLIGHT:
            if for_console:
                # Return the word with ANSI red color codes for console display
                return f"\033[91m{original_word}\033[0m"
            else:
                # Return plain text for file storage
                return original_word
        
        return original_word
    
    def filter_text(self, text: str, for_console: bool = True) -> Tuple[str, Dict]:
        """
        Filter profanity from text and return filtered text with statistics.
        
        Args:
            text: The text to filter
            for_console: If True, applies console colors; if False, returns plain text
        
        Returns:
            Tuple of (filtered_text, filter_stats)
        """
        if not text:
            return text, {}
        
        profanity_found = self._find_profanity(text)
        
        if not profanity_found:
            self.stats["total_words_processed"] += len(text.split())  # type: ignore
            return text, {"words_filtered": 0, "original_length": len(text)}
        
        # Process text from right to left to maintain indices
        filtered_text = text
        words_filtered = 0
        
        for word, severity, start, end in reversed(profanity_found):
            original_word = text[start:end]
            replacement = self._apply_filter(original_word, word, severity, for_console)
            
            # Apply replacement
            if replacement:
                filtered_text = filtered_text[:start] + replacement + filtered_text[end:]
            else:
                # Remove word and handle spacing
                filtered_text = filtered_text[:start] + filtered_text[end:]
                # Clean up extra spaces
                filtered_text = re.sub(r'\s+', ' ', filtered_text)
            
            words_filtered += 1
            self.stats["words_filtered"] += 1  # type: ignore
            severity_stats = self.stats["by_severity"]  # type: ignore
            severity_stats[severity.name] += 1  # type: ignore
        
        self.stats["total_words_processed"] += len(text.split())  # type: ignore
        
        filter_stats = {
            "words_filtered": words_filtered,
            "original_length": len(text),
            "filtered_length": len(filtered_text),
            "profanity_found": [(word, severity.name) for word, severity, _, _ in profanity_found]
        }
        
        return filtered_text.strip(), filter_stats
    
    def get_statistics(self) -> Dict:
        """Get filtering statistics."""
        total_processed = self.stats["total_words_processed"]  # type: ignore
        words_filtered = self.stats["words_filtered"]  # type: ignore
        filter_rate = (words_filtered / total_processed * 100) if total_processed > 0 else 0  # type: ignore
        
        return {
            **self.stats,
            "filter_rate_percent": round(float(filter_rate), 2)
        }
    
    def reset_statistics(self):
        """Reset filtering statistics."""
        self.stats = {
            "total_words_processed": 0,
            "words_filtered": 0,
            "by_severity": {
                "MILD": 0,
                "MODERATE": 0,
                "SEVERE": 0
            }
        }


# Example configuration creator
def create_sample_config(filename: str = "profanity_config.json"):
    """Create a sample configuration file."""
    sample_config = {
        "word_lists": {
            "mild": ["damn", "hell", "crap", "bloody"],
            "moderate": ["shit", "fuck", "bitch", "ass"],
            "severe": ["nigger", "faggot", "retard"]
        },
        "actions": {
            "mild": "red_highlight",
            "moderate": "red_highlight", 
            "severe": "red_highlight"
        },
        "custom_replacements": {
            "fuck": "fudge",
            "shit": "shoot"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Sample profanity config created: {filename}")
    print("   All profanity will be highlighted in red on console")


if __name__ == "__main__":
    # Example usage
    filter_obj = ProfanityFilter()
    
    test_texts = [
        "This is a damn good test",
        "What the fuck is happening here?",
        "That's some bullshit right there",
        "Clean text with no profanity"
    ]
    
    print("🧪 Testing Profanity Filter:")
    print("=" * 50)
    
    for text in test_texts:
        filtered, stats = filter_obj.filter_text(text)
        print(f"Original: {text}")
        print(f"Filtered: {filtered}")
        print(f"Stats: {stats}")
        print("-" * 30)
    
    print("\n📊 Overall Statistics:")
    print(filter_obj.get_statistics())
    
    # Create sample config
    create_sample_config()
