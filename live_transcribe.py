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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import enhanced filter first, fallback to basic
try:
    from enhanced_profanity_filter import EnhancedProfanityFilter, FilterAction, SeverityLevel
    ENHANCED_FILTER_AVAILABLE = True
except ImportError:
    from profanity_filter import ProfanityFilter, FilterAction, SeverityLevel
    ENHANCED_FILTER_AVAILABLE = False
    print("⚠️ Enhanced filter not available, using basic filter")

# Try to import model-based filter
try:
    from model_profanity_filter import ModelBasedProfanityFilter
    MODEL_FILTER_AVAILABLE = True
except ImportError:
    MODEL_FILTER_AVAILABLE = False
    print("⚠️ Model-based filter not available (missing dependencies)")

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
FILTER_TYPE = "dictionary"  # Options: "dictionary", "model"
PROFANITY_CONFIG_FILE = "enhanced_profanity_config.json" if ENHANCED_FILTER_AVAILABLE else "profanity_config.json"
MODEL_CONFIG_FILE = "model_profanity_config.json"
TOXICITY_MODEL = "unitary/toxic-bert"  # Fast toxic detection model
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
        if FILTER_TYPE == "model" and MODEL_FILTER_AVAILABLE:
            # Use model-based filter
            config_path = MODEL_CONFIG_FILE if os.path.exists(MODEL_CONFIG_FILE) else None
            profanity_filter = ModelBasedProfanityFilter(
                config_path, 
                model_name=TOXICITY_MODEL,
                hf_token=os.getenv("HUGGINGFACE_TOKEN")
            )
            filter_type = f"Model-based ({profanity_filter.model_name})"
            
        elif FILTER_TYPE == "dictionary" or not MODEL_FILTER_AVAILABLE:
            # Use dictionary-based filter
            config_path = PROFANITY_CONFIG_FILE if os.path.exists(PROFANITY_CONFIG_FILE) else None
            
            if ENHANCED_FILTER_AVAILABLE:
                profanity_filter = EnhancedProfanityFilter(config_path, use_datasets=USE_ENHANCED_DATASETS)
                filter_type = f"Enhanced Dictionary (with {profanity_filter.trie.word_count} words)"
            else:
                profanity_filter = ProfanityFilter(config_path)
                filter_type = "Basic Dictionary"
        
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
    global ENABLE_PROFANITY_FILTER, profanity_filter, FILTER_TYPE
    
    parser = argparse.ArgumentParser(description='Live transcription of video stream with profanity filtering')
    parser.add_argument('--stream', choices=['udp', 'http'], default='udp',
                        help='Stream type to connect to (default: udp)')
    parser.add_argument('--model', default=MODEL_NAME,
                        help=f'Whisper model to use (default: {MODEL_NAME})')
    parser.add_argument('--language', default=LANGUAGE,
                        help=f'Language for transcription (default: {LANGUAGE})')
    parser.add_argument('--no-filter', action='store_true',
                        help='Disable profanity filtering')
    parser.add_argument('--filter-type', choices=['dictionary', 'model'], default=FILTER_TYPE,
                        help=f'Type of profanity filter to use (default: {FILTER_TYPE})')
    parser.add_argument('--filter-config', default=PROFANITY_CONFIG_FILE,
                        help=f'Dictionary filter config file (default: {PROFANITY_CONFIG_FILE})')
    parser.add_argument('--model-config', default=MODEL_CONFIG_FILE,
                        help=f'Model filter config file (default: {MODEL_CONFIG_FILE})')
    parser.add_argument('--toxicity-model', default=TOXICITY_MODEL,
                        help=f'Toxicity detection model (default: {TOXICITY_MODEL})')
    parser.add_argument('--create-filter-config', action='store_true',
                        help='Create a sample profanity filter configuration and exit')
    parser.add_argument('--create-model-config', action='store_true',
                        help='Create a sample model-based filter configuration and exit')
    
    args = parser.parse_args()
    
    # Handle config creation
    if args.create_filter_config:
        from profanity_filter import create_sample_config
        create_sample_config(args.filter_config)
        return
    
    if args.create_model_config:
        if MODEL_FILTER_AVAILABLE:
            from model_profanity_filter import create_sample_model_config
            create_sample_model_config(args.model_config)
        else:
            print("❌ Model-based filter not available. Install transformers: pip install transformers")
        return
    
    # Override global settings based on arguments
    
    FILTER_TYPE = args.filter_type
    
    if args.no_filter:
        ENABLE_PROFANITY_FILTER = False
        profanity_filter = None
    else:
        if ENABLE_PROFANITY_FILTER and not profanity_filter:
            # Reload filter with specified config and type
            try:
                if args.filter_type == "model" and MODEL_FILTER_AVAILABLE:
                    config_file = args.model_config
                    profanity_filter = ModelBasedProfanityFilter(
                        config_file if os.path.exists(config_file) else None,
                        model_name=args.toxicity_model,
                        hf_token=os.getenv("HUGGINGFACE_TOKEN")
                    )
                    filter_description = f"Model-based filter loaded with model: {args.toxicity_model}"
                else:
                    if args.filter_type == "model" and not MODEL_FILTER_AVAILABLE:
                        print("⚠️ Model-based filter requested but not available. Using dictionary filter.")
                    
                    config_file = args.filter_config
                    if ENHANCED_FILTER_AVAILABLE:
                        profanity_filter = EnhancedProfanityFilter(
                            config_file if os.path.exists(config_file) else None,
                            use_datasets=USE_ENHANCED_DATASETS
                        )
                    else:
                        profanity_filter = ProfanityFilter(
                            config_file if os.path.exists(config_file) else None
                        )
                    filter_description = f"Dictionary filter loaded with config: {config_file}"
                
                print(f"✅ {filter_description}")
            except Exception as e:
                print(f"⚠️ Error loading profanity filter: {e}")
                profanity_filter = None
    
    # Choose stream URL based on argument
    stream_url = HTTP_STREAM_URL if args.stream == 'http' else UDP_STREAM_URL
    
    print(f"🚀 Starting live transcription")
    print(f"   Stream: {stream_url}")
    print(f"   Model: {args.model}")
    print(f"   Language: {args.language}")
    
    # Show filter information
    if profanity_filter:
        if hasattr(profanity_filter, 'model_name'):  # Model-based filter
            print(f"   Profanity Filter: Model-based ({profanity_filter.model_name})")
        elif hasattr(profanity_filter, 'trie'):  # Enhanced dictionary filter
            print(f"   Profanity Filter: Enhanced Dictionary ({profanity_filter.trie.word_count} words)")
        else:  # Basic dictionary filter
            print(f"   Profanity Filter: Basic Dictionary")
    else:
        print(f"   Profanity Filter: Disabled")
    
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
            
            # Show additional stats for model-based filter
            if hasattr(profanity_filter, 'model_name'):
                print(f"   Model used: {stats.get('model_name', 'Unknown')}")
                print(f"   Sentences processed: {stats.get('sentences_processed', 0)}")
                print(f"   Toxic sentences: {stats.get('toxic_sentences', 0)}")
            
            # Show severity breakdown
            if stats.get('by_severity'):
                print("   By severity:")
                for severity, count in stats['by_severity'].items():
                    if count > 0:
                        print(f"     {severity}: {count}")


if __name__ == "__main__":
    main()
