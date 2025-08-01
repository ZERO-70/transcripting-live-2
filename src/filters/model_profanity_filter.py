"""
Model-based Profanity Filter using Toxic Detection Models
Fast and accurate toxicity detection using lightweight transformer models.
"""

import re
import json
import os
import time
import warnings
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum
from collections import defaultdict

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class FilterAction(Enum):
    """Actions to take when profanity is detected."""
    ASTERISK = "asterisk"
    PLACEHOLDER = "placeholder" 
    REMOVE = "remove"
    FLAG = "flag"
    RED_HIGHLIGHT = "red_highlight"

class SeverityLevel(Enum):
    """Severity levels for different types of content."""
    MILD = 1
    MODERATE = 2
    SEVERE = 3

class ModelBasedProfanityFilter:
    """
    Model-based profanity filter using lightweight toxic detection models.
    Much faster and more accurate than dictionary-based approaches.
    """
    
    def __init__(self, config_path: Optional[str] = None, model_name: str = "martin-ha/toxic-comment-model", hf_token: Optional[str] = None):
        """
        Initialize the model-based profanity filter.
        
        Args:
            config_path: Path to configuration file
            model_name: HuggingFace model name for toxicity detection
            hf_token: Hugging Face authentication token
        """
        self.model_name = model_name
        self.hf_token = hf_token or "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"
        self.model = None
        self.tokenizer = None
        self._load_dependencies()
        
        # Default configuration
        self.config = {
            "actions": {
                "mild": FilterAction.RED_HIGHLIGHT.value,
                "moderate": FilterAction.RED_HIGHLIGHT.value,
                "severe": FilterAction.RED_HIGHLIGHT.value
            },
            "thresholds": {
                "mild": 0.3,     # Lower threshold for mild toxicity
                "moderate": 0.6,  # Medium threshold
                "severe": 0.8     # High threshold for severe toxicity
            },
            "placeholders": {
                "mild": "[MILD]",
                "moderate": "[FILTERED]",
                "severe": "[CENSORED]"
            },
            "model_settings": {
                "max_length": 512,
                "batch_size": 1,
                "device": "cpu"  # Use CPU for compatibility
            }
        }
        
        # Load custom config if provided
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        # Initialize model
        self._load_model()
        
        # Statistics tracking
        self.stats = {
            "total_words_processed": 0,
            "words_filtered": 0,
            "sentences_processed": 0,
            "toxic_sentences": 0,
            "by_severity": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }
        
        # ANSI color codes for console highlighting
        self.colors = {
            "red": "\033[91m",
            "yellow": "\033[93m",
            "orange": "\033[38;5;208m",
            "reset": "\033[0m",
            "bold": "\033[1m"
        }
    
    def _load_dependencies(self):
        """Load required dependencies with fallback options."""
        try:
            import torch
            self.torch = torch
            print("✅ PyTorch loaded successfully")
        except ImportError:
            raise ImportError("PyTorch is required but not installed. Install with: pip install torch")
        
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self.AutoTokenizer = AutoTokenizer
            self.AutoModelForSequenceClassification = AutoModelForSequenceClassification
            print("✅ Transformers loaded successfully")
        except ImportError:
            print("❌ Transformers not found. Installing...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self.AutoTokenizer = AutoTokenizer
            self.AutoModelForSequenceClassification = AutoModelForSequenceClassification
            print("✅ Transformers installed and loaded")
    
    def _load_model(self):
        """Load the toxicity detection model."""
        print(f"🤖 Loading toxicity detection model: {self.model_name}")
        
        try:
            # Load tokenizer and model with authentication token
            self.tokenizer = self.AutoTokenizer.from_pretrained(
                self.model_name, 
                token=self.hf_token,
                trust_remote_code=True
            )
            self.model = self.AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                token=self.hf_token,
                trust_remote_code=True
            )
            
            # Set to evaluation mode
            self.model.eval()
            
            # Move to specified device
            device = self.config["model_settings"]["device"]
            if device == "cuda" and self.torch.cuda.is_available():
                self.model = self.model.cuda()
                print("🚀 Using GPU acceleration")
            else:
                self.model = self.model.cpu()
                print("💻 Using CPU (recommended for compatibility)")
            
            print(f"✅ Model loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Error loading model {self.model_name}: {e}")
            print("   Falling back to a lighter model...")
            
            # Fallback to a smaller, faster model
            fallback_models = [
                "unitary/toxic-bert",
                "martin-ha/toxic-comment-model",
                "cardiffnlp/twitter-roberta-base-offensive",
                "cardiffnlp/twitter-roberta-base-hate",
            ]
            
            for fallback_model in fallback_models:
                try:
                    print(f"🔄 Trying fallback model: {fallback_model}")
                    self.tokenizer = self.AutoTokenizer.from_pretrained(
                        fallback_model,
                        token=self.hf_token,
                        trust_remote_code=True
                    )
                    self.model = self.AutoModelForSequenceClassification.from_pretrained(
                        fallback_model,
                        token=self.hf_token,
                        trust_remote_code=True
                    )
                    self.model.eval()
                    self.model_name = fallback_model
                    print(f"✅ Fallback model loaded: {fallback_model}")
                    break
                except Exception as fe:
                    print(f"❌ Fallback model {fallback_model} failed: {fe}")
                    continue
            
            if self.model is None:
                raise Exception("Could not load any toxicity detection model")
    
    def _load_config(self, config_path: str):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                
                # Update configuration with custom settings
                if "model_config" in custom_config:
                    self.config.update(custom_config["model_config"])
                    
                print(f"✅ Model configuration loaded from: {config_path}")
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    def predict_toxicity(self, text: str) -> Tuple[float, str]:
        """
        Predict toxicity score for given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (toxicity_score, severity_level)
        """
        if not self.model or not self.tokenizer:
            return 0.0, "mild"
        
        try:
            # Tokenize input
            max_length = self.config["model_settings"]["max_length"]
            inputs = self.tokenizer(
                text,
                max_length=max_length,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            # Move to same device as model
            device = next(self.model.parameters()).device
            inputs = {key: value.to(device) for key, value in inputs.items()}
            
            # Get prediction
            with self.torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Apply softmax to get probabilities
                probabilities = self.torch.nn.functional.softmax(logits, dim=-1)
                
                # Get toxicity score (assuming binary classification where index 1 is toxic)
                if probabilities.shape[-1] == 2:
                    toxicity_score = probabilities[0][1].item()
                else:
                    # For multi-class, take the max non-neutral class
                    toxicity_score = probabilities[0].max().item()
            
            # Determine severity level
            thresholds = self.config["thresholds"]
            if toxicity_score >= thresholds["severe"]:
                severity = "severe"
            elif toxicity_score >= thresholds["moderate"]:
                severity = "moderate"
            elif toxicity_score >= thresholds["mild"]:
                severity = "mild"
            else:
                severity = None
            
            return toxicity_score, severity
            
        except Exception as e:
            print(f"⚠️ Error in toxicity prediction: {e}")
            return 0.0, "mild"
    
    def filter_text(self, text: str, for_console: bool = False) -> Tuple[str, Dict]:
        """
        Filter text using model-based toxicity detection.
        
        Args:
            text: Input text to filter
            for_console: Whether output is for console (enables colors)
            
        Returns:
            Tuple of (filtered_text, filter_statistics)
        """
        if not text.strip():
            return text, {"words_filtered": 0, "toxicity_found": []}
        
        # Update statistics
        self.stats["sentences_processed"] += 1
        words = text.split()
        self.stats["total_words_processed"] += len(words)
        
        # Get toxicity prediction
        toxicity_score, severity = self.predict_toxicity(text)
        
        filter_stats = {
            "words_filtered": 0,
            "toxicity_found": [],
            "toxicity_score": toxicity_score,
            "severity": severity
        }
        
        # If no toxicity detected, return original text
        if severity is None:
            return text, filter_stats
        
        # Handle toxic content based on severity and action
        self.stats["toxic_sentences"] += 1
        self.stats["by_severity"][severity] += 1
        self.stats["words_filtered"] += len(words)  # Count all words in toxic sentence
        
        filter_stats["words_filtered"] = len(words)
        filter_stats["toxicity_found"] = [{"text": text, "severity": severity, "score": toxicity_score}]
        
        action = FilterAction(self.config["actions"][severity])
        
        if action == FilterAction.RED_HIGHLIGHT and for_console:
            # Highlight in red for console
            color = self.colors["red"] if severity == "severe" else \
                   self.colors["orange"] if severity == "moderate" else \
                   self.colors["yellow"]
            filtered_text = f"{color}{self.colors['bold']}{text}{self.colors['reset']}"
        
        elif action == FilterAction.PLACEHOLDER:
            filtered_text = self.config["placeholders"][severity]
        
        elif action == FilterAction.ASTERISK:
            # Replace with asterisks (preserve length)
            filtered_text = "*" * len(text)
        
        elif action == FilterAction.REMOVE:
            filtered_text = ""
        
        elif action == FilterAction.FLAG:
            flag = f"[TOXIC:{severity.upper()}]"
            filtered_text = f"{text} {flag}"
        
        else:
            # Default to highlighting for console, plain text for file
            if for_console:
                filtered_text = f"{self.colors['red']}{self.colors['bold']}{text}{self.colors['reset']}"
            else:
                filtered_text = text
        
        return filtered_text, filter_stats
    
    def get_statistics(self) -> Dict:
        """Get filtering statistics."""
        total_processed = self.stats["total_words_processed"]
        filtered = self.stats["words_filtered"]
        filter_rate = (filtered / total_processed * 100) if total_processed > 0 else 0
        
        return {
            "total_words_processed": total_processed,
            "words_filtered": filtered,
            "sentences_processed": self.stats["sentences_processed"],
            "toxic_sentences": self.stats["toxic_sentences"],
            "filter_rate_percent": round(filter_rate, 2),
            "by_severity": dict(self.stats["by_severity"]),
            "model_name": self.model_name
        }
    
    def reset_statistics(self):
        """Reset all statistics."""
        self.stats = {
            "total_words_processed": 0,
            "words_filtered": 0,
            "sentences_processed": 0,
            "toxic_sentences": 0,
            "by_severity": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }


def create_sample_model_config(config_path: str = "model_profanity_config.json"):
    """Create a sample configuration file for model-based filtering."""
    sample_config = {
        "model_config": {
            "actions": {
                "mild": "red_highlight",
                "moderate": "red_highlight", 
                "severe": "placeholder"
            },
            "thresholds": {
                "mild": 0.3,
                "moderate": 0.6,
                "severe": 0.8
            },
            "placeholders": {
                "mild": "[MILD]",
                "moderate": "[FILTERED]",
                "severe": "[CENSORED]"
            },
            "model_settings": {
                "max_length": 512,
                "batch_size": 1,
                "device": "cpu"
            }
        },
        "_description": {
            "actions": "Actions to take: asterisk, placeholder, remove, flag, red_highlight",
            "thresholds": "Toxicity score thresholds (0.0 to 1.0) for each severity level",
            "placeholders": "Replacement text for placeholder action",
            "model_settings": "Model configuration settings"
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sample model configuration created: {config_path}")
    print("   Edit this file to customize toxicity detection settings")


if __name__ == "__main__":
    # Test the model-based filter
    import argparse
    
    parser = argparse.ArgumentParser(description='Test model-based profanity filter')
    parser.add_argument('--create-config', action='store_true',
                        help='Create sample configuration file')
    parser.add_argument('--text', type=str,
                        help='Test text to analyze')
    parser.add_argument('--model', type=str, default='unitary/toxic-bert',
                        help='Model to use for toxicity detection')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_model_config()
    elif args.text:
        print("🧪 Testing model-based profanity filter...")
        filter_instance = ModelBasedProfanityFilter(model_name=args.model)
        
        filtered_text, stats = filter_instance.filter_text(args.text, for_console=True)
        print(f"\nOriginal: {args.text}")
        print(f"Filtered: {filtered_text}")
        print(f"Toxicity Score: {stats.get('toxicity_score', 0):.3f}")
        print(f"Severity: {stats.get('severity', 'None')}")
        
        print("\n📊 Statistics:")
        final_stats = filter_instance.get_statistics()
        for key, value in final_stats.items():
            print(f"   {key}: {value}")
    else:
        print("Use --create-config to create a sample config or --text 'your text' to test")
