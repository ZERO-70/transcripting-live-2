#!/usr/bin/env python3
"""
Comprehensive Test for Profanity Filtering Systems
Tests both basic and enhanced profanity filters with various scenarios.
"""

import time
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_filter():
    """Test the basic profanity filter."""
    print("🔹 Testing Basic Profanity Filter")
    print("-" * 50)
    
    try:
        from profanity_filter import ProfanityFilter, SeverityLevel
        
        filter_obj = ProfanityFilter()
        
        test_cases = [
            "This is a damn good example",
            "What the fuck is happening here?",
            "That's complete bullshit",
            "Clean text with no issues",
            "Multiple damn fucking problems here"
        ]
        
        total_time = 0
        for i, text in enumerate(test_cases, 1):
            start_time = time.time()
            filtered, stats = filter_obj.filter_text(text)
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            total_time += processing_time
            
            print(f"Test {i}:")
            print(f"  Original: {text}")
            print(f"  Filtered: {filtered}")
            print(f"  Words filtered: {stats.get('words_filtered', 0)}")
            print(f"  Time: {processing_time:.2f}ms")
            print()
        
        stats = filter_obj.get_statistics()
        print(f"📊 Basic Filter Summary:")
        print(f"   Total processing time: {total_time:.2f}ms")
        print(f"   Average per text: {total_time/len(test_cases):.2f}ms")
        print(f"   Words processed: {stats['total_words_processed']}")
        print(f"   Words filtered: {stats['words_filtered']}")
        print(f"   Filter rate: {stats['filter_rate_percent']}%")
        
        return True
        
    except ImportError as e:
        print(f"❌ Basic filter not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing basic filter: {e}")
        return False

def test_enhanced_filter():
    """Test the enhanced profanity filter with datasets."""
    print("🔹 Testing Enhanced Profanity Filter")
    print("-" * 50)
    
    try:
        from enhanced_profanity_filter import EnhancedProfanityFilter, SeverityLevel
        
        # Test with datasets (may download)
        print("Loading enhanced filter with datasets...")
        filter_obj = EnhancedProfanityFilter(use_datasets=True)
        
        print(f"✅ Loaded {filter_obj.trie.word_count} words into trie")
        print()
        
        test_cases = [
            "This is a damn good example with regular words",
            "What the f@ck is happening with obfuscated text?",
            "That's complete bullsh1t with numbers",
            "Clean text with no profanity at all",
            "Multiple d@mn f***ing pr0blems with obfuscation",
            "Some really offensive slurs that should be removed",
            "Testing severe hate speech content filtering"
        ]
        
        total_time = 0
        for i, text in enumerate(test_cases, 1):
            start_time = time.time()
            filtered, stats = filter_obj.filter_text(text)
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            total_time += processing_time
            
            print(f"Test {i}:")
            print(f"  Original: {text}")
            print(f"  Filtered: {filtered}")
            print(f"  Words filtered: {stats.get('words_filtered', 0)}")
            if stats.get('profanity_found'):
                print(f"  Found: {stats['profanity_found']}")
            print(f"  Time: {processing_time:.2f}ms")
            print()
        
        stats = filter_obj.get_statistics()
        print(f"📊 Enhanced Filter Summary:")
        print(f"   Trie size: {stats['trie_word_count']} words")
        print(f"   Total processing time: {total_time:.2f}ms")
        print(f"   Average per text: {total_time/len(test_cases):.2f}ms")
        print(f"   Words processed: {stats['total_words_processed']}")
        print(f"   Words filtered: {stats['words_filtered']}")
        print(f"   Filter rate: {stats['filter_rate_percent']}%")
        print(f"   By severity: {stats['by_severity']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Enhanced filter not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing enhanced filter: {e}")
        return False

def performance_comparison():
    """Compare performance between basic and enhanced filters."""
    print("🏃 Performance Comparison")
    print("-" * 50)
    
    # Large test text for performance testing
    large_text = """
    This is a comprehensive test text that contains various types of content
    including some damn profanity and fucking strong language. We need to test
    how well the filters perform with longer texts that might contain bullshit
    scattered throughout. The enhanced filter should handle obfuscated words
    like f@ck and sh1t better than the basic version. This text also includes
    clean sections to test the overall processing speed and accuracy.
    """ * 10  # Repeat to make it larger
    
    try:
        # Test basic filter
        from profanity_filter import ProfanityFilter
        basic_filter = ProfanityFilter()
        
        start_time = time.time()
        basic_result, basic_stats = basic_filter.filter_text(large_text)
        basic_time = (time.time() - start_time) * 1000
        
        print(f"📝 Basic Filter Performance:")
        print(f"   Processing time: {basic_time:.2f}ms")
        print(f"   Words filtered: {basic_stats.get('words_filtered', 0)}")
        print()
        
    except Exception as e:
        print(f"⚠️ Basic filter test failed: {e}")
        basic_time = 0
    
    try:
        # Test enhanced filter
        from enhanced_profanity_filter import EnhancedProfanityFilter
        enhanced_filter = EnhancedProfanityFilter(use_datasets=False)  # Skip dataset download for speed
        
        start_time = time.time()
        enhanced_result, enhanced_stats = enhanced_filter.filter_text(large_text)
        enhanced_time = (time.time() - start_time) * 1000
        
        print(f"🚀 Enhanced Filter Performance:")
        print(f"   Processing time: {enhanced_time:.2f}ms")
        print(f"   Words filtered: {enhanced_stats.get('words_filtered', 0)}")
        print(f"   Trie size: {enhanced_filter.trie.word_count} words")
        print()
        
        if basic_time > 0:
            speedup = basic_time / enhanced_time if enhanced_time > 0 else float('inf')
            print(f"⚡ Performance Comparison:")
            print(f"   Enhanced is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than basic")
        
    except Exception as e:
        print(f"⚠️ Enhanced filter test failed: {e}")

def main():
    """Run comprehensive profanity filter tests."""
    print("🧪 Comprehensive Profanity Filter Test Suite")
    print("=" * 60)
    print()
    
    # Test basic filter
    basic_available = test_basic_filter()
    print()
    
    # Test enhanced filter
    enhanced_available = test_enhanced_filter()
    print()
    
    # Performance comparison
    if basic_available and enhanced_available:
        performance_comparison()
    
    print("✅ Testing complete!")
    print()
    
    # Usage recommendations
    print("💡 Recommendations:")
    if enhanced_available:
        print("   ✅ Use Enhanced Filter for:")
        print("      - Production environments")
        print("      - Better obfuscation detection")
        print("      - Comprehensive word coverage")
        print("      - Fast trie-based searching")
    
    if basic_available:
        print("   📝 Use Basic Filter for:")
        print("      - Simple use cases")
        print("      - Custom word lists")
        print("      - Educational purposes")
        print("      - Minimal dependencies")

if __name__ == "__main__":
    main()
