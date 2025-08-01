#!/usr/bin/env python3
"""
Demo script to show red highlighting of profanity in console output
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_red_highlighting():
    """Demonstrate red highlighting of profanity words."""
    print("🎨 Profanity Red Highlighting Demo")
    print("=" * 50)
    
    try:
        from profanity_filter import ProfanityFilter
        
        # Create filter with red highlighting
        filter_obj = ProfanityFilter()
        
        demo_texts = [
            "This is a damn good presentation about filtering",
            "What the hell happened to the audio quality?",
            "The system is working like shit today",
            "That's some fucking amazing technology right there",
            "Clean professional content with no issues"
        ]
        
        print("📺 Console Output (with red highlighting):")
        print("-" * 40)
        
        for i, text in enumerate(demo_texts, 1):
            # Get colored version for console
            console_output, stats = filter_obj.filter_text(text, for_console=True)
            
            # Get plain version for comparison
            plain_output, _ = filter_obj.filter_text(text, for_console=False)
            
            print(f"[{i:02d}] {console_output}")
            
            if stats.get('words_filtered', 0) > 0:
                print(f"     📄 File version: {plain_output}")
                print(f"     🛡️  Highlighted: {stats['words_filtered']} word(s)")
                print()
        
        print("\n📊 Demo Statistics:")
        overall_stats = filter_obj.get_statistics()
        print(f"   Words processed: {overall_stats['total_words_processed']}")
        print(f"   Words highlighted: {overall_stats['words_filtered']}")
        print(f"   Highlight rate: {overall_stats['filter_rate_percent']}%")
        
        print("\n💡 What you see:")
        print("   ✅ Console: Profanity words appear in RED")
        print("   📄 File: Same words appear in normal text")
        print("   🎯 Original content is preserved, just highlighted")
        
    except ImportError as e:
        print(f"❌ Filter not available: {e}")
    except Exception as e:
        print(f"❌ Demo error: {e}")

def demo_live_transcription_format():
    """Show how this would look in live transcription."""
    print("\n" + "=" * 60)
    print("🎙️  Live Transcription Preview (Red Highlighting)")
    print("=" * 60)
    
    # Simulate transcript with timestamps
    transcript_samples = [
        ("[12.3s]", "Welcome everyone to this damn presentation"),
        ("[28.7s]", "The audio quality is working like shit today"),
        ("[45.1s]", "But the technology is fucking amazing"),
        ("[62.8s]", "Thank you for your attention and questions")
    ]
    
    try:
        from profanity_filter import ProfanityFilter
        filter_obj = ProfanityFilter()
        
        for timestamp, text in transcript_samples:
            filtered_text, stats = filter_obj.filter_text(text, for_console=True)
            filter_info = ""
            
            if stats.get("words_filtered", 0) > 0:
                filter_info = f" [🛡️ Highlighted: {stats['words_filtered']} words]"
            
            print(f"{timestamp} {filtered_text}{filter_info}")
        
        print("\n📝 In the transcript file, these would be saved without color codes")
        
    except Exception as e:
        print(f"❌ Preview error: {e}")

if __name__ == "__main__":
    demo_red_highlighting()
    demo_live_transcription_format()
