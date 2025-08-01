#!/usr/bin/env python3
"""
Live Transcription Launcher
Wrapper script to run live transcription with proper imports.
"""

import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import and run the live transcription
if __name__ == "__main__":
    from transcription.live_transcribe import main
    main()
