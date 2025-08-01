"""
Enhanced Profanity Filter with Dataset Support and Fast Search Algorithms
Supports multiple datasets, fuzzy matching, and optimized search performance.
"""

import re
import json
import os
import csv
import urllib.request
import gzip
from typing import List, Dict, Tuple, Set, Optional, Union, Callable
from enum import Enum
from collections import defaultdict
import time

class FilterAction(Enum):
    """Actions to take when profanity is detected."""
    ASTERISK = "asterisk"
    PLACEHOLDER = "placeholder" 
    REMOVE = "remove"
    FLAG = "flag"
    RED_HIGHLIGHT = "red_highlight"  # Highlight in red on console

class SeverityLevel(Enum):
    """Severity levels for different types of content."""
    MILD = 1
    MODERATE = 2
    SEVERE = 3

class TrieNode:
    """Node for Trie data structure for fast word matching."""
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_word: bool = False
        self.severity: Optional[SeverityLevel] = None
        self.original_word: Optional[str] = None

class ProfanityTrie:
    """Trie-based fast word matching for profanity detection."""
    
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
    
    def insert(self, word: str, severity: SeverityLevel):
        """Insert a word into the trie."""
        node = self.root
        word = word.lower().strip()
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end_word = True
        node.severity = severity
        node.original_word = word
        self.word_count += 1
    
    def search(self, word: str) -> Optional[Tuple[str, SeverityLevel]]:
        """Search for a word in the trie. Returns (word, severity) if found."""
        node = self.root
        word = word.lower().strip()
        
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        
        if node.is_end_word and node.original_word and node.severity:
            return (node.original_word, node.severity)
        return None
    
    def find_all_matches(self, text: str) -> List[Tuple[str, SeverityLevel, int, int]]:
        """Find all profanity matches in text using the trie."""
        matches = []
        words = re.finditer(r'\b\w+\b', text.lower())
        
        for match in words:
            word = match.group()
            start, end = match.span()
            
            result = self.search(word)
            if result:
                original_word, severity = result
                matches.append((original_word, severity, start, end))
        
        return matches

class EnhancedProfanityFilter:
    """
    Enhanced profanity filter with dataset support and fast search algorithms.
    """
    
    def __init__(self, config_file: Optional[str] = None, use_datasets: bool = True):
        self.trie = ProfanityTrie()
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
        self.obfuscation_patterns = self._create_obfuscation_patterns()
        
        # Load configuration and datasets
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        if use_datasets:
            self._load_datasets()
        else:
            self._load_default_words()
    
    def _create_obfuscation_patterns(self) -> Dict[str, str]:
        """Create patterns to detect obfuscated profanity (f@ck, sh1t, etc.)."""
        return {
            '@': 'a', '4': 'a', '3': 'e', '1': 'i', '!': 'i',
            '0': 'o', '5': 's', '7': 't', '$': 's', '8': 'b',
            '+': 't', 'ph': 'f', 'ck': 'ck', 'xx': 'ck'
        }
    
    def _normalize_word(self, word: str) -> str:
        """Normalize obfuscated words to their standard form."""
        word = word.lower()
        for obfuscated, normal in self.obfuscation_patterns.items():
            word = word.replace(obfuscated, normal)
        return word
    
    def _load_default_words(self):
        """Load basic word lists as fallback."""
        word_lists = {
            SeverityLevel.MILD: [
                "damn", "hell", "crap", "bloody", "darn", "piss", "suck",
                "stupid", "idiot", "moron", "dumb", "lame", "gay"
            ],
            SeverityLevel.MODERATE: [
                "shit", "fuck", "bitch", "ass", "asshole", "bastard",
                "dickhead", "prick", "douche", "jackass", "whore", "slut",
                "tits", "boobs", "cock", "dick", "pussy", "cunt"
            ],
            SeverityLevel.SEVERE: [
                "nigger", "nigga", "faggot", "retard", "spic", "chink",
                "kike", "wetback", "raghead", "towelhead", "gook", "jap"
            ]
        }
        
        for severity, words in word_lists.items():
            for word in words:
                self.trie.insert(word, severity)
    
    def _download_dataset(self, url: str, filename: str) -> bool:
        """Download a dataset from URL."""
        try:
            print(f"📥 Downloading dataset: {filename}")
            urllib.request.urlretrieve(url, filename)
            print(f"✅ Downloaded: {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
    
    def _load_datasets(self):
        """Load profanity datasets from various sources."""
        print("🔄 Loading profanity datasets...")
        
        # Define available datasets
        datasets: Dict[str, Dict[str, Union[str, Callable[[str], int]]]] = {
            "hurtlex": {
                "url": "https://raw.githubusercontent.com/valeriobasile/hurtlex/master/lexica/EN/1.2/hurtlex_EN.tsv",
                "filename": "hurtlex_EN.tsv",
                "parser": self._parse_hurtlex
            },
            "offensive_words": {
                "url": "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en",
                "filename": "offensive_words_en.txt",
                "parser": self._parse_simple_list
            }
        }
        
        # Create datasets directory
        datasets_dir = "datasets"
        if not os.path.exists(datasets_dir):
            os.makedirs(datasets_dir)
        
        words_loaded = 0
        
        # Try to load each dataset
        for dataset_name, info in datasets.items():
            filepath = os.path.join(datasets_dir, str(info["filename"]))
            
            # Download if not exists
            if not os.path.exists(filepath):
                if not self._download_dataset(str(info["url"]), filepath):
                    continue
            
            # Parse dataset
            try:
                parser_func = info["parser"]
                if callable(parser_func):
                    dataset_word_count = parser_func(filepath)
                    words_loaded += dataset_word_count
                    print(f"✅ Loaded {dataset_word_count} words from {dataset_name}")
            except Exception as e:
                print(f"⚠️ Error parsing {dataset_name}: {e}")
        
        # Fallback to default if no datasets loaded
        if words_loaded == 0:
            print("⚠️ No datasets loaded, using default word lists")
            self._load_default_words()
        else:
            print(f"🎯 Total words loaded: {words_loaded}")
    
    def _parse_hurtlex(self, filepath: str) -> int:
        """Parse HurtLex dataset (TSV format)."""
        words_loaded = 0
        severity_mapping = {
            "AN": SeverityLevel.MODERATE,  # Animals
            "ASF": SeverityLevel.SEVERE,   # Social and economic disadvantage
            "ASM": SeverityLevel.SEVERE,   # Male genitalia  
            "DDP": SeverityLevel.SEVERE,   # Cognitive disabilities
            "DDF": SeverityLevel.SEVERE,   # Physical disabilities
            "DMC": SeverityLevel.SEVERE,   # Moral and cognitive deficits
            "IS": SeverityLevel.SEVERE,    # Derogatory words
            "OR": SeverityLevel.MODERATE,  # Plants
            "QAS": SeverityLevel.SEVERE,   # With potential negative connotations
            "RE": SeverityLevel.SEVERE,    # Ethnic slurs
            "SV": SeverityLevel.MILD,      # Scatological/vulgar
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    word = row.get('lemma', '').strip().lower()
                    category = row.get('category', '')
                    
                    if word and len(word) > 1:
                        severity = severity_mapping.get(category, SeverityLevel.MODERATE)
                        self.trie.insert(word, severity)
                        words_loaded += 1
        except Exception as e:
            print(f"Error parsing HurtLex: {e}")
        
        return words_loaded
    
    def _parse_simple_list(self, filepath: str) -> int:
        """Parse simple text file with one word per line."""
        words_loaded = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word and len(word) > 1 and not word.startswith('#'):
                        # Assign severity based on word characteristics
                        if len(word) <= 4 or any(mild in word for mild in ['damn', 'hell', 'crap']):
                            severity = SeverityLevel.MILD
                        elif any(severe in word for severe in ['nig', 'fag', 'ret']):
                            severity = SeverityLevel.SEVERE
                        else:
                            severity = SeverityLevel.MODERATE
                        
                        self.trie.insert(word, severity)
                        words_loaded += 1
        except Exception as e:
            print(f"Error parsing simple list: {e}")
        
        return words_loaded
    
    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load actions
            for severity_str, action_str in config.get('actions', {}).items():
                severity = SeverityLevel[severity_str.upper()]
                self.actions[severity] = FilterAction[action_str.upper()]
            
            # Load custom replacements
            self.custom_replacements = config.get('custom_replacements', {})
            
            # Load additional words if specified
            for severity_str, words in config.get('additional_words', {}).items():
                severity = SeverityLevel[severity_str.upper()]
                for word in words:
                    self.trie.insert(word, severity)
            
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    def save_config(self, config_file: str):
        """Save current configuration to JSON file."""
        config = {
            'actions': {
                severity.name.lower(): action.value 
                for severity, action in self.actions.items()
            },
            'custom_replacements': self.custom_replacements,
            'stats': {
                'total_words_in_trie': self.trie.word_count,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def add_word(self, word: str, severity: SeverityLevel):
        """Add a word to the filter."""
        self.trie.insert(word, severity)
    
    def _apply_filter(self, original_word: str, word: str, severity: SeverityLevel, for_console: bool = True) -> str:
        """Apply the appropriate filter action to a word."""
        # Check for custom replacement first
        if word.lower() in self.custom_replacements:
            return self.custom_replacements[word.lower()]
        
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
        """Filter profanity from text using fast trie-based search."""
        if not text:
            return text, {}
        
        # Find profanity using trie
        profanity_found = self.trie.find_all_matches(text)
        
        # Also check for obfuscated versions
        normalized_matches = []
        words = re.finditer(r'\b\w+\b', text)
        for match in words:
            word = match.group()
            normalized = self._normalize_word(word)
            if normalized != word.lower():
                result = self.trie.search(normalized)
                if result:
                    _, severity = result
                    start, end = match.span()
                    normalized_matches.append((normalized, severity, start, end))
        
        # Combine regular and obfuscated matches
        all_matches = profanity_found + normalized_matches
        
        if not all_matches:
            self.stats["total_words_processed"] += len(text.split())  # type: ignore
            return text, {"words_filtered": 0, "original_length": len(text)}
        
        # Sort by position (reverse order for replacement)
        all_matches.sort(key=lambda x: x[2], reverse=True)
        
        # Process text from right to left to maintain indices
        filtered_text = text
        words_filtered = 0
        
        for word, severity, start, end in all_matches:
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
            "profanity_found": [(word, severity.name) for word, severity, _, _ in all_matches]
        }
        
        return filtered_text.strip(), filter_stats
    
    def get_statistics(self) -> Dict:
        """Get filtering statistics."""
        total_processed = self.stats["total_words_processed"]  # type: ignore
        words_filtered = self.stats["words_filtered"]  # type: ignore
        filter_rate = (words_filtered / total_processed * 100) if total_processed > 0 else 0  # type: ignore
        
        return {
            **self.stats,
            "filter_rate_percent": round(float(filter_rate), 2),
            "trie_word_count": self.trie.word_count
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

def create_enhanced_config(filename: str = "enhanced_profanity_config.json"):
    """Create a sample enhanced configuration file."""
    config = {
        "actions": {
            "mild": "red_highlight",
            "moderate": "red_highlight",
            "severe": "red_highlight"
        },
        "custom_replacements": {
            "fuck": "fudge",
            "shit": "shoot",
            "damn": "darn",
            "bitch": "witch"
        },
        "additional_words": {
            "mild": ["dammit", "freaking"],
            "moderate": ["bullcrap", "screwed"],
            "severe": []
        },
        "obfuscation_detection": True,
        "use_datasets": True
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Enhanced profanity config created: {filename}")
    print("   All profanity will be highlighted in red on console")

if __name__ == "__main__":
    # Test the enhanced filter
    print("🚀 Testing Enhanced Profanity Filter with Datasets")
    print("=" * 60)
    
    # Initialize filter (this will download datasets)
    filter_obj = EnhancedProfanityFilter(use_datasets=True)
    
    test_texts = [
        "This is a damn good test with regular profanity",
        "What the f@ck is happening with obfuscated words?",
        "That's some real bullsh1t right there",
        "Clean text with no profanity at all",
        "This contains s3v3r3 h@te words that should be removed"
    ]
    
    print(f"📊 Loaded {filter_obj.trie.word_count} words into trie")
    print("\n🧪 Testing with various text samples:")
    print("-" * 60)
    
    for i, text in enumerate(test_texts, 1):
        start_time = time.time()
        filtered, stats = filter_obj.filter_text(text)
        end_time = time.time()
        
        print(f"Test {i}:")
        print(f"  Original: {text}")
        print(f"  Filtered: {filtered}")
        print(f"  Stats: {stats}")
        print(f"  Processing time: {(end_time - start_time)*1000:.2f}ms")
        print("-" * 40)
    
    print("\n📊 Overall Statistics:")
    stats = filter_obj.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Create enhanced config
    create_enhanced_config()
