#!/usr/bin/env python3
"""
Test script to demonstrate profanity filtering functionality
without requiring video stream setup.
"""

from profanity_filter import ProfanityFilter, FilterAction, SeverityLevel

def test_profanity_filter():
    """Test the profanity filter with sample text."""
    
    print("🧪 Testing Profanity Filter Integration")
    print("=" * 50)
    
    # Initialize filter
    filter_obj = ProfanityFilter("profanity_config.json")
    
    # Test texts simulating transcription output
    test_transcripts = [
        "Hello everyone, welcome to the damn presentation",
        "What the fuck is going on with this system?", 
        "This is some real bullshit, I can't believe it",
        "The speaker said some really offensive words that were censored",
        "Thank you for attending this clean presentation",
        "Oh shit, I forgot to mention the important point",
        "This is a normal sentence with no issues"
    ]
    
    print("Sample transcription with profanity filtering:\n")
    
    total_original_words = 0
    total_filtered_words = 0
    
    for i, text in enumerate(test_transcripts, 1):
        # Simulate timestamp
        timestamp = f"[{i*15.5:.1f}s]"
        
        # Apply profanity filter
        filtered_text, stats = filter_obj.filter_text(text)
        
        # Show filtering in action
        if stats.get("words_filtered", 0) > 0:
            print(f"{timestamp} {filtered_text} [🛡️ Filtered: {stats['words_filtered']} words]")
            total_filtered_words += stats["words_filtered"]
        else:
            print(f"{timestamp} {filtered_text}")
        
        total_original_words += len(text.split())
    
    # Show statistics
    print("\n" + "=" * 50)
    print("📊 Session Statistics:")
    overall_stats = filter_obj.get_statistics()
    print(f"   Total words processed: {overall_stats['total_words_processed']}")
    print(f"   Words filtered: {overall_stats['words_filtered']}")
    print(f"   Filter rate: {overall_stats['filter_rate_percent']}%")
    
    if overall_stats['by_severity']:
        print("   Filtered by severity:")
        for severity, count in overall_stats['by_severity'].items():
            if count > 0:
                print(f"     {severity}: {count} words")
    
    print("\n🛡️ Filter Configuration:")
    for severity, action in filter_obj.actions.items():
        word_count = len(filter_obj.word_lists[severity])
        print(f"   {severity.name}: {action.value} ({word_count} words)")
    
    # Show examples of different filtering actions
    print("\n🔍 Filter Action Examples:")
    examples = [
        ("damn", SeverityLevel.MILD),
        ("fuck", SeverityLevel.MODERATE), 
        ("retard", SeverityLevel.SEVERE)
    ]
    
    for word, severity in examples:
        filtered, _ = filter_obj.filter_text(f"This is {word} text")
        action = filter_obj.actions[severity].value
        print(f"   {word} ({severity.name}): '{word}' → '{filtered.replace('This is ', '').replace(' text', '')}' [{action}]")

def show_configuration_options():
    """Show different configuration examples."""
    
    print("\n⚙️ Configuration Examples:")
    print("-" * 30)
    
    # Example 1: Strict filtering
    print("1. Strict Filtering (everything removed):")
    strict_filter = ProfanityFilter()
    for severity in [SeverityLevel.MILD, SeverityLevel.MODERATE, SeverityLevel.SEVERE]:
        strict_filter.set_action(severity, FilterAction.REMOVE)
    
    text = "This damn shit is fucking terrible"
    filtered, stats = strict_filter.filter_text(text)
    print(f"   Original: '{text}'")
    print(f"   Filtered: '{filtered}'")
    print(f"   Removed: {stats['words_filtered']} words")
    
    # Example 2: Gentle filtering (all asterisks)
    print("\n2. Gentle Filtering (asterisks only):")
    gentle_filter = ProfanityFilter()
    for severity in [SeverityLevel.MILD, SeverityLevel.MODERATE, SeverityLevel.SEVERE]:
        gentle_filter.set_action(severity, FilterAction.ASTERISK)
    
    filtered, stats = gentle_filter.filter_text(text)
    print(f"   Original: '{text}'")
    print(f"   Filtered: '{filtered}'")
    
    # Example 3: Custom replacements
    print("\n3. Custom Replacements:")
    custom_filter = ProfanityFilter()
    custom_filter.custom_replacements.update({
        "damn": "darn",
        "shit": "shoot", 
        "fuck": "fudge",
        "fucking": "fudging"
    })
    
    filtered, stats = custom_filter.filter_text(text)
    print(f"   Original: '{text}'")
    print(f"   Filtered: '{filtered}'")

if __name__ == "__main__":
    try:
        test_profanity_filter()
        show_configuration_options()
        
        print("\n✅ Profanity filter test completed successfully!")
        print("\nTo use with live transcription:")
        print("   /usr/bin/python3 live_transcribe.py  # With filtering (default)")
        print("   /usr/bin/python3 live_transcribe.py --no-filter  # Without filtering")
        print("   /usr/bin/python3 live_transcribe.py --filter-config custom.json  # Custom config")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Make sure profanity_config.json exists. Run:")
        print("   /usr/bin/python3 live_transcribe.py --create-filter-config")
