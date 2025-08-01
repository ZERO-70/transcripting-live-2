#!/usr/bin/env python3
"""
Demo script to showcase model-based vs dictionary-based profanity filtering
"""

import time
import os

def test_filter_comparison():
    """Compare model-based and dictionary-based filters"""
    
    # Test sentences with varying toxicity levels
    test_sentences = [
        "This is a completely normal sentence.",
        "You're such an idiot for thinking that.",
        "I absolutely hate this stupid thing.",
        "What the hell is wrong with you?",
        "This is mildly annoying but okay.",
        "That's totally awesome and amazing!",
        "You moron, that's completely wrong.",
        "I love this beautiful sunny day."
    ]
    
    print("🧪 Profanity Filter Comparison Demo")
    print("=" * 50)
    
    # Test dictionary filter first
    print("\n📚 DICTIONARY-BASED FILTER:")
    print("-" * 30)
    
    try:
        from enhanced_profanity_filter import EnhancedProfanityFilter
        dict_filter = EnhancedProfanityFilter()
        print("✅ Enhanced dictionary filter loaded")
    except ImportError:
        try:
            from profanity_filter import ProfanityFilter
            dict_filter = ProfanityFilter()
            print("✅ Basic dictionary filter loaded")
        except ImportError:
            print("❌ No dictionary filter available")
            dict_filter = None
    
    if dict_filter:
        for i, sentence in enumerate(test_sentences, 1):
            start_time = time.time()
            filtered, stats = dict_filter.filter_text(sentence, for_console=True)
            end_time = time.time()
            
            print(f"{i}. Original: {sentence}")
            print(f"   Filtered: {filtered}")
            print(f"   Words filtered: {stats.get('words_filtered', 0)}")
            print(f"   Processing time: {(end_time - start_time)*1000:.1f}ms")
            print()
    
    # Test model-based filter
    print("\n🤖 MODEL-BASED FILTER:")
    print("-" * 30)
    
    try:
        from model_profanity_filter import ModelBasedProfanityFilter
        
        print("Loading model-based filter...")
        model_filter = ModelBasedProfanityFilter()
        print("✅ Model-based filter loaded")
        
        for i, sentence in enumerate(test_sentences, 1):
            start_time = time.time()
            filtered, stats = model_filter.filter_text(sentence, for_console=True)
            end_time = time.time()
            
            print(f"{i}. Original: {sentence}")
            print(f"   Filtered: {filtered}")
            print(f"   Toxicity Score: {stats.get('toxicity_score', 0):.3f}")
            print(f"   Severity: {stats.get('severity', 'None')}")
            print(f"   Processing time: {(end_time - start_time)*1000:.1f}ms")
            print()
        
        # Show final statistics
        print("📊 Model Filter Statistics:")
        final_stats = model_filter.get_statistics()
        for key, value in final_stats.items():
            print(f"   {key}: {value}")
            
    except ImportError:
        print("❌ Model-based filter not available")
        print("   Install with: pip install transformers")
    except Exception as e:
        print(f"❌ Error loading model filter: {e}")

def demo_live_transcription_setup():
    """Show how to set up live transcription with different filter types"""
    
    print("\n🎙️  LIVE TRANSCRIPTION SETUP DEMO")
    print("=" * 50)
    
    print("\n1. Dictionary-based filtering:")
    print("   python live_transcribe.py --filter-type dictionary")
    
    print("\n2. Model-based filtering:")
    print("   python live_transcribe.py --filter-type model")
    
    print("\n3. Custom model:")
    print("   python live_transcribe.py --filter-type model --toxicity-model martin-ha/toxic-comment-model")
    
    print("\n4. Create configurations:")
    print("   python live_transcribe.py --create-model-config")
    print("   python live_transcribe.py --create-filter-config")
    
    print("\n5. No filtering:")
    print("   python live_transcribe.py --no-filter")

def check_dependencies():
    """Check what dependencies are available"""
    
    print("\n🔍 DEPENDENCY CHECK")
    print("=" * 30)
    
    # Check basic requirements
    try:
        import numpy
        print("✅ NumPy available")
    except ImportError:
        print("❌ NumPy not available")
    
    try:
        from faster_whisper import WhisperModel
        print("✅ Faster-Whisper available")
    except ImportError:
        print("❌ Faster-Whisper not available")
    
    # Check filter availability
    try:
        from profanity_filter import ProfanityFilter
        print("✅ Basic profanity filter available")
    except ImportError:
        print("❌ Basic profanity filter not available")
    
    try:
        from enhanced_profanity_filter import EnhancedProfanityFilter
        print("✅ Enhanced profanity filter available")
    except ImportError:
        print("❌ Enhanced profanity filter not available")
    
    # Check model dependencies
    try:
        import torch
        print(f"✅ PyTorch available (version: {torch.__version__})")
    except ImportError:
        print("❌ PyTorch not available")
    
    try:
        import transformers
        print(f"✅ Transformers available (version: {transformers.__version__})")
    except ImportError:
        print("❌ Transformers not available")
        print("   Install with: pip install transformers")
    
    try:
        from model_profanity_filter import ModelBasedProfanityFilter
        print("✅ Model-based profanity filter available")
    except ImportError:
        print("❌ Model-based profanity filter not available")

if __name__ == "__main__":
    print("🚀 Live Transcription Filter Demo")
    print("This demo showcases the new model-based profanity filtering")
    print()
    
    # Check what's available
    check_dependencies()
    
    # Show setup options
    demo_live_transcription_setup()
    
    # Run comparison if possible
    try:
        test_filter_comparison()
    except Exception as e:
        print(f"\n❌ Could not run filter comparison: {e}")
        print("Make sure you have the required dependencies installed.")
    
    print("\n" + "=" * 50)
    print("Demo complete! Choose your preferred filter type and enjoy blazingly fast,")
    print("accurate profanity detection in your live transcriptions! 🎉")
