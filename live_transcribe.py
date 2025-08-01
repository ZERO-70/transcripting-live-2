import subprocess
import numpy as np
import threading
import queue
import time
import sys
import os
import argparse
from datetime import datetime
from faster_whisper import WhisperModel

# Try to import enhanced filter first, fallback to basic
try:
    from enhanced_profanity_filter import EnhancedProfanityFilter, FilterAction, SeverityLevel
    ENHANCED_FILTER_AVAILABLE = True
except ImportError:
    from profanity_filter import ProfanityFilter, FilterAction, SeverityLevel
    ENHANCED_FILTER_AVAILABLE = False
    print("⚠️ Enhanced filter not available, using basic filter")

# ----- CONFIG -----
UDP_STREAM_URL = "udp://127.0.0.1:1234"
HTTP_STREAM_URL = "http://127.0.0.1:8080"
SAMPLE_RATE = 16000
CHUNK_DURATION = 3  # in seconds
MODEL_NAME = "base"  # tiny/int8 recommended for CPU
LANGUAGE = "en"
MAX_QUEUE_SIZE = 10  # Prevent memory buildup
SAVE_TRANSCRIPT = True  # Save to file
ENABLE_PROFANITY_FILTER = True  # Enable profanity filtering
PROFANITY_CONFIG_FILE = "enhanced_profanity_config.json" if ENHANCED_FILTER_AVAILABLE else "profanity_config.json"
SHOW_FILTER_STATS = True  # Show filtering statistics
USE_ENHANCED_DATASETS = True  # Use enhanced datasets if available
# -------------------

# Set up transcription model (CPU-friendly)
print("🤖 Loading Whisper model...")
model = WhisperModel(MODEL_NAME, compute_type="int8")
print(f"✅ Model '{MODEL_NAME}' loaded successfully")

# Set up profanity filter if enabled
profanity_filter = None
if ENABLE_PROFANITY_FILTER:
    print("🛡️  Loading profanity filter...")
    try:
        config_path = PROFANITY_CONFIG_FILE if os.path.exists(PROFANITY_CONFIG_FILE) else None
        
        if ENHANCED_FILTER_AVAILABLE:
            profanity_filter = EnhancedProfanityFilter(config_path, use_datasets=USE_ENHANCED_DATASETS)
            filter_type = f"Enhanced (with {profanity_filter.trie.word_count} words)"
        else:
            profanity_filter = ProfanityFilter(config_path)
            filter_type = "Basic"
        
        print(f"✅ {filter_type} profanity filter loaded successfully")
        if SHOW_FILTER_STATS:
            print("   Filter configuration loaded")
    except Exception as e:
        print(f"⚠️ Error loading profanity filter: {e}")
        print("   Continuing without profanity filtering...")
        profanity_filter = None

# Create a thread-safe queue to hold audio chunks
audio_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)

# Global variables for transcript logging
transcript_file = None
start_time = None


def setup_transcript_file():
    """Create a timestamped transcript file."""
    global transcript_file, start_time
    if SAVE_TRANSCRIPT:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{timestamp}.txt"
        transcript_file = open(filename, 'w', encoding='utf-8')
        start_time = time.time()
        print(f"📝 Saving transcript to: {filename}")
        return filename
    return None


def start_ffmpeg_stream(stream_url, max_retries=3):
    """Start ffmpeg process that outputs raw PCM audio from the stream."""
    cmd = [
        "ffmpeg",
        "-i", stream_url,
        "-f", "s16le",  # PCM 16-bit little-endian
        "-acodec", "pcm_s16le",
        "-ac", "1",  # mono
        "-ar", str(SAMPLE_RATE),
        "-loglevel", "error",  # Show errors but reduce verbosity
        "-reconnect", "1",  # Auto-reconnect for network streams
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "pipe:1"
    ]
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Connecting to stream: {stream_url} (attempt {attempt + 1}/{max_retries})")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Test if the process started successfully
            time.sleep(1)
            if proc.poll() is None:  # Process is still running
                print("✅ Successfully connected to stream")
                return proc
            else:
                try:
                    if proc.stderr:
                        stderr_data = proc.stderr.read()
                        stderr_output = stderr_data.decode() if isinstance(stderr_data, bytes) else str(stderr_data)
                    else:
                        stderr_output = "Unknown error"
                except:
                    stderr_output = "Could not read error details"
                print(f"❌ Failed to connect: {stderr_output}")
        except Exception as e:
            print(f"❌ Error starting FFmpeg: {e}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Retrying in 2 seconds...")
            time.sleep(2)
    
    raise Exception(f"Failed to connect to stream after {max_retries} attempts")


def audio_reader(proc):
    """Reads raw PCM audio from FFmpeg and puts chunks into the queue."""
    bytes_per_sample = 2  # 16-bit audio
    chunk_size = CHUNK_DURATION * SAMPLE_RATE * bytes_per_sample
    
    print(f"🎵 Audio reader started (chunk size: {chunk_size} bytes)")

    while True:
        try:
            chunk = proc.stdout.read(chunk_size)
            if not chunk:
                print("📡 End of audio stream")
                break
            
            audio = np.frombuffer(chunk, np.int16).astype(np.float32) / 32768.0
            
            # Add to queue, drop oldest if full
            try:
                audio_queue.put_nowait(audio)
            except queue.Full:
                try:
                    audio_queue.get_nowait()  # Remove oldest
                    audio_queue.put_nowait(audio)  # Add new
                    print("⚠️ Audio buffer full, dropping old data")
                except queue.Empty:
                    pass
                    
        except Exception as e:
            print(f"❌ Audio reader error: {e}")
            break


def transcriber():
    """Reads chunks from the queue and transcribes them."""
    print("🎙️  Live transcription started...\n")
    chunk_count = 0
    total_filtered_words = 0

    while True:
        try:
            audio = audio_queue.get(timeout=5)  # 5 second timeout
            if audio is None:
                break

            chunk_count += 1
            current_time = time.time() - start_time if start_time else 0
            
            segments, _ = model.transcribe(audio, language=LANGUAGE)
            
            for segment in segments:
                timestamp_str = f"[{current_time:.1f}s]"
                text = segment.text.strip()
                
                if text:  # Only process non-empty transcriptions
                    # Apply profanity filter if enabled
                    console_text = text
                    file_text = text
                    filter_info = ""
                    
                    if profanity_filter:
                        # Get colored version for console
                        console_text, filter_stats = profanity_filter.filter_text(text, for_console=True)
                        # Get plain version for file
                        file_text, _ = profanity_filter.filter_text(text, for_console=False)
                        
                        if filter_stats.get("words_filtered", 0) > 0:
                            total_filtered_words += filter_stats["words_filtered"]
                            if SHOW_FILTER_STATS:
                                profanity_words = filter_stats.get("profanity_found", [])
                                filter_info = f" [🛡️ Highlighted: {len(profanity_words)} words]"
                    
                    # Prepare console output (with colors)
                    console_output = f"{timestamp_str} {console_text}{filter_info}"
                    print(console_output)
                    
                    # Save to file if enabled (save plain text version)
                    if transcript_file:
                        file_output = f"{timestamp_str} {file_text}"
                        transcript_file.write(f"{file_output}\n")
                        transcript_file.flush()
                        
        except queue.Empty:
            print("⏳ Waiting for audio data...")
            continue
        except Exception as e:
            print(f"⚠️ Transcription error: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Live transcription of video stream with profanity filtering')
    parser.add_argument('--stream', choices=['udp', 'http'], default='udp',
                        help='Stream type to connect to (default: udp)')
    parser.add_argument('--model', default=MODEL_NAME,
                        help=f'Whisper model to use (default: {MODEL_NAME})')
    parser.add_argument('--language', default=LANGUAGE,
                        help=f'Language for transcription (default: {LANGUAGE})')
    parser.add_argument('--no-filter', action='store_true',
                        help='Disable profanity filtering')
    parser.add_argument('--filter-config', default=PROFANITY_CONFIG_FILE,
                        help=f'Profanity filter config file (default: {PROFANITY_CONFIG_FILE})')
    parser.add_argument('--create-filter-config', action='store_true',
                        help='Create a sample profanity filter configuration and exit')
    
    args = parser.parse_args()
    
    # Handle config creation
    if args.create_filter_config:
        from profanity_filter import create_sample_config
        create_sample_config(args.filter_config)
        return
    
    # Override global settings based on arguments
    global ENABLE_PROFANITY_FILTER, profanity_filter
    
    if args.no_filter:
        ENABLE_PROFANITY_FILTER = False
        profanity_filter = None
    else:
        config_file = args.filter_config
        if ENABLE_PROFANITY_FILTER and not profanity_filter:
            # Reload filter with specified config
            try:
                profanity_filter = ProfanityFilter(config_file)
                print(f"✅ Profanity filter loaded with config: {config_file}")
            except Exception as e:
                print(f"⚠️ Error loading profanity filter: {e}")
                profanity_filter = None
    
    # Choose stream URL based on argument
    stream_url = HTTP_STREAM_URL if args.stream == 'http' else UDP_STREAM_URL
    
    print(f"🚀 Starting live transcription")
    print(f"   Stream: {stream_url}")
    print(f"   Model: {args.model}")
    print(f"   Language: {args.language}")
    print(f"   Profanity Filter: {'Enabled' if profanity_filter else 'Disabled'}")
    print("=" * 50)
    
    # Setup transcript file
    transcript_filename = setup_transcript_file()
    
    try:
        proc = start_ffmpeg_stream(stream_url)

        # Launch audio reader and transcriber threads
        audio_thread = threading.Thread(target=audio_reader, args=(proc,), daemon=True)
        transcriber_thread = threading.Thread(target=transcriber, daemon=True)
        
        audio_thread.start()
        transcriber_thread.start()

        print("\n🎯 Transcription running... Press Ctrl+C to stop")
        if profanity_filter:
            print("🛡️  Profanity filtering is active")
        print()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping live transcription...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        audio_queue.put(None)
        if 'proc' in locals():
            proc.terminate()
        if transcript_file:
            transcript_file.close()
            print(f"📁 Transcript saved to: {transcript_filename}")
        
        # Show profanity filter statistics if enabled
        if profanity_filter and SHOW_FILTER_STATS:
            stats = profanity_filter.get_statistics()
            print("\n🛡️  Profanity Filter Statistics:")
            print(f"   Words processed: {stats['total_words_processed']}")
            print(f"   Words filtered: {stats['words_filtered']}")
            print(f"   Filter rate: {stats['filter_rate_percent']}%")
            if stats['by_severity']:
                print("   By severity:")
                for severity, count in stats['by_severity'].items():
                    if count > 0:
                        print(f"     {severity}: {count}")


if __name__ == "__main__":
    main()
