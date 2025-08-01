#!/usr/bin/env python3
"""
Demo script showing dictionary vs model-based filtering in action.
"""

import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'filters'))

from enhanced_profanity_filter import EnhancedProfanityFilter
from model_profanity_filter import ModelBasedProfanityFilter

def demo_filter_comparison():
    """Show real-time comparison of both filter types."""
    
    print("🎯 Live Transcription Filter Demo")
    print("=" * 50)
    print("This demo shows how both filter types work on sample transcriptions.")
    print()
    
    # Initialize filters
    print("🔧 Loading filters...")
    start_time = time.time()
    
    # Dictionary filter
    dict_filter = EnhancedProfanityFilter("enhanced_profanity_config.json")
    dict_load_time = time.time() - start_time
    
    # Model filter
    start_time = time.time()
    model_filter = ModelBasedProfanityFilter(
        "model_profanity_config.json",
        model_name="unitary/toxic-bert",
        hf_token=os.getenv("HUGGINGFACE_TOKEN")
    )
    model_load_time = time.time() - start_time
    
    print(f"✅ Dictionary filter loaded in {dict_load_time:.2f}s")
    print(f"✅ Model filter loaded in {model_load_time:.2f}s")
    print()
    
    # Sample transcription segments (like what would come from live audio)
    transcript_segments = [
        "Welcome everyone to today's presentation",
        "Let me show you how this damn system works",
        "You guys are being really stupid about this",
        "This is some real bullshit we're dealing with",
        "What the hell is wrong with this setup?",
        "I fucking hate when technology doesn't work",
        "Can we please just focus on the task?",
        "You're acting like a complete jerk right now",
        "This assignment is totally pointless",
        "Thank you all for your attention today"
    ]
    
    print("🎙️  Simulated Live Transcription")
    print("=" * 50)
    print("Format: [Timestamp] Original → Dictionary → Model")
    print()
    
    total_dict_time = 0
    total_model_time = 0
    
    for i, text in enumerate(transcript_segments):
        # Simulate real-time timing
        timestamp = f"[{i*5.5:.1f}s]"
        
        # Dictionary filtering
        start_time = time.time()
        dict_result, dict_stats = dict_filter.filter_text(text, for_console=False)
        dict_time = time.time() - start_time
        total_dict_time += dict_time
        
        # Model filtering  
        start_time = time.time()
        model_result, model_stats = model_filter.filter_text(text, for_console=False)
        model_time = time.time() - start_time
        total_model_time += model_time
        
        # Display results
        print(f"{timestamp} Original: '{text}'")
        print(f"          Dictionary: '{dict_result}' [{dict_stats.get('words_filtered', 0)} filtered | {dict_time*1000:.1f}ms]")
        print(f"          Model:      '{model_result}' [{model_stats.get('words_filtered', 0)} filtered | {model_time*1000:.1f}ms]")
        print()
        
        # Simulate real-time delay
        time.sleep(0.5)
    
    # Show statistics
    print("📊 Performance Summary")
    print("=" * 30)
    
    segments_count = len(transcript_segments)
    avg_dict_time = (total_dict_time / segments_count) * 1000
    avg_model_time = (total_model_time / segments_count) * 1000
    
    print(f"Dictionary Filter:")
    print(f"  Average: {avg_dict_time:.1f}ms per segment")
    print(f"  Total:   {total_dict_time*1000:.1f}ms")
    print(f"  Real-time Ready: {'✅ Yes' if avg_dict_time < 50 else '❌ No'}")
    print()
    
    print(f"Model Filter:")
    print(f"  Average: {avg_model_time:.1f}ms per segment")
    print(f"  Total:   {total_model_time*1000:.1f}ms")
    print(f"  Real-time Ready: {'✅ Yes' if avg_model_time < 200 else '❌ No'}")
    print()
    
    # Show filter statistics
    dict_overall = dict_filter.get_statistics()
    model_overall = model_filter.get_statistics()
    
    print("🔍 Filtering Statistics")
    print("=" * 30)
    print(f"Dictionary: {dict_overall.get('words_filtered', 0)}/{dict_overall.get('total_words_processed', 0)} words filtered")
    print(f"Model:      {model_overall.get('words_filtered', 0)}/{model_overall.get('total_words_processed', 0)} words filtered")
    print()
    
    # Recommendations
    print("💡 Recommendations")
    print("=" * 20)
    if avg_dict_time < 50 and avg_model_time < 200:
        print("✅ Both filters are suitable for real-time use!")
        print("   • Use Dictionary for: Predictable, fast filtering")
        print("   • Use Model for: Context-aware, intelligent filtering")
    elif avg_dict_time < 50:
        print("✅ Dictionary filter is ideal for real-time use")
        print("⚠️  Model filter may cause latency in live streams")
        print("   • Consider model filter for post-processing")
    else:
        print("⚠️  Both filters may be too slow for real-time")
        print("   • Check system performance")
        print("   • Consider using smaller Whisper model")

def show_usage_examples():
    """Show command examples for both filter types."""
    
    print("\n🚀 Usage Examples")
    print("=" * 20)
    
    print("Live Transcription Commands:")
    print("----------------------------")
    print("# Dictionary filtering (fast, predictable)")
    print("python3 live_transcribe.py --filter-type dictionary")
    print()
    print("# Model filtering (smart, context-aware)")  
    print("python3 live_transcribe.py --filter-type model")
    print()
    print("# No filtering")
    print("python3 live_transcribe.py --no-filter")
    print()
    print("# Custom model")
    print("python3 live_transcribe.py --filter-type model --toxicity-model martin-ha/toxic-comment-model")
    print()
    
    print("Testing Commands:")
    print("-----------------")
    print("# Test both filters")
    print("python3 test_model_filter.py")
    print()
    print("# Test dictionary only")
    print("python3 test_profanity_filter.py")
    print()
    print("# Run this demo")
    print("python3 demo_filter_comparison.py")

if __name__ == "__main__":
    try:
        demo_filter_comparison()
        show_usage_examples()
        
        print("\n🎯 Demo completed successfully!")
        print("Your system now supports both dictionary and model-based filtering.")
        print("Choose the filter type that best fits your needs!")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Make sure all dependencies are installed and config files exist.")
