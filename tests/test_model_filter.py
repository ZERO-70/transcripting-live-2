#!/usr/bin/env python3
"""
Test script for the model-based profanity filter with Hugging Face authentication.
"""

import sys
import time
import os
from dotenv import load_dotenv
from model_profanity_filter import ModelBasedProfanityFilter

# Load environment variables
load_dotenv()

def test_model_filter():
    """Test the model-based profanity filter."""
    print("🧪 Testing Model-Based Profanity Filter")
    print("=" * 50)
    
    # Test with HF token from environment
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    
    # Test different models
    models_to_test = [
        "unitary/toxic-bert",
        "martin-ha/toxic-comment-model",
        "cardiffnlp/twitter-roberta-base-offensive"
    ]
    
    for model_name in models_to_test:
        print(f"\n🤖 Testing model: {model_name}")
        print("-" * 40)
        
        try:
            # Initialize filter with HF token
            start_time = time.time()
            filter_obj = ModelBasedProfanityFilter(
                config_path="model_profanity_config.json",
                model_name=model_name,
                hf_token=hf_token
            )
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.2f} seconds")
            
            # Test texts
            test_texts = [
                "Hello everyone, this is a clean sentence",
                "What the hell is going on here?",
                "This is some real bullshit",
                "You are such an idiot",
                "That's fucking awesome!",
                "This presentation is great"
            ]
            
            print("\n📝 Testing toxicity detection:")
            total_processing_time = 0
            
            for i, text in enumerate(test_texts, 1):
                start_time = time.time()
                filtered_text, stats = filter_obj.filter_text(text, for_console=True)
                processing_time = time.time() - start_time
                total_processing_time += processing_time
                
                print(f"  {i}. Original: '{text}'")
                print(f"     Filtered: '{filtered_text}'")
                print(f"     Stats: {stats.get('words_filtered', 0)} words filtered")
                print(f"     Time: {processing_time*1000:.1f}ms")
                print()
            
            avg_time = (total_processing_time / len(test_texts)) * 1000
            print(f"📊 Average processing time: {avg_time:.1f}ms per sentence")
            
            # Show overall statistics
            overall_stats = filter_obj.get_statistics()
            print(f"📈 Total statistics:")
            print(f"   Sentences processed: {overall_stats.get('sentences_processed', 0)}")
            print(f"   Words processed: {overall_stats.get('total_words_processed', 0)}")
            print(f"   Words filtered: {overall_stats.get('words_filtered', 0)}")
            print(f"   Toxic sentences: {overall_stats.get('toxic_sentences', 0)}")
            
            print(f"✅ Model {model_name} works perfectly!")
            break  # If this model works, use it
            
        except Exception as e:
            print(f"❌ Model {model_name} failed: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("🎯 Model-based filter test completed!")

def compare_filters():
    """Compare dictionary vs model-based filtering."""
    print("\n🆚 Comparing Dictionary vs Model-Based Filtering")
    print("=" * 50)
    
    # Import dictionary filter for comparison
    try:
        from enhanced_profanity_filter import EnhancedProfanityFilter
        dict_filter = EnhancedProfanityFilter("enhanced_profanity_config.json")
        dict_available = True
    except ImportError:
        from profanity_filter import ProfanityFilter
        dict_filter = ProfanityFilter("profanity_config.json")
        dict_available = True
    except Exception as e:
        print(f"⚠️ Dictionary filter not available: {e}")
        dict_available = False
    
    # Initialize model filter
    try:
        model_filter = ModelBasedProfanityFilter(
            "model_profanity_config.json",
            model_name="unitary/toxic-bert",
            hf_token=os.getenv("HUGGINGFACE_TOKEN")
        )
        model_available = True
    except Exception as e:
        print(f"⚠️ Model filter not available: {e}")
        model_available = False
    
    if not (dict_available and model_available):
        print("❌ Cannot compare - one or both filters unavailable")
        return
    
    # Test cases that show the difference
    test_cases = [
        "You're being a real jerk today",  # Context-dependent
        "That movie was shit",  # Simple profanity
        "Stop being such a toxic person",  # Toxic behavior vs profanity
        "This damn thing is broken",  # Mild profanity
        "I hate this stupid assignment",  # Negative sentiment
        "You look great today!"  # Clean text
    ]
    
    print("📊 Comparison Results:")
    print()
    
    for i, text in enumerate(test_cases, 1):
        print(f"{i}. Original: '{text}'")
        
        if dict_available:
            dict_result, dict_stats = dict_filter.filter_text(text, for_console=False)
            dict_filtered = dict_stats.get('words_filtered', 0)
            print(f"   Dictionary: '{dict_result}' ({dict_filtered} words filtered)")
        
        if model_available:
            model_result, model_stats = model_filter.filter_text(text, for_console=False)
            model_filtered = model_stats.get('words_filtered', 0)
            print(f"   Model:      '{model_result}' ({model_filtered} words filtered)")
        
        print()
    
    print("🎯 Key Differences:")
    print("   • Dictionary: Fast, simple word matching")
    print("   • Model: Slower, but understands context and toxicity")
    print("   • Model can detect toxic behavior without explicit profanity")
    print("   • Dictionary is more predictable and consistent")

if __name__ == "__main__":
    try:
        test_model_filter()
        compare_filters()
        
        print("\n✅ All tests completed!")
        print("\nTo use in live transcription:")
        print("   python3 live_transcribe.py --filter-type model")
        print("   python3 live_transcribe.py --filter-type dictionary")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
