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

# Audio playback imports (optional)
AUDIO_PLAYBACK_AVAILABLE = False
try:
    import sounddevice as sd
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    print("⚠️ sounddevice not available, audio playback disabled")

# Load environment variables
load_dotenv()

# Try to import enhanced filter first, fallback to basic
import sys
import os

# Add the filters directory to the path
filters_dir = os.path.join(os.path.dirname(__file__), '..', 'filters')
sys.path.insert(0, filters_dir)

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

# Audio playback settings
ENABLE_AUDIO_PLAYBACK = False  # Enable live audio playback
AUDIO_PLAYBACK_VOLUME = 0.7   # Volume level (0.0 to 1.0)
AUDIO_PLAYBACK_DEVICE = None  # None for default device, or device index
AUDIO_BUFFER_SIZE = 256       # Audio buffer size for playback (smaller for less latency)
SHOW_PROCESSING_TIME = True   # Show processing time for each transcription chunk
# -------------------

# Set up transcription model (CPU-friendly)
print("🤖 Loading Whisper model...")
model = WhisperModel(MODEL_NAME, compute_type="int16")
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

# Audio playback queue and stream (independent from transcription)
audio_playback_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE * 2)  # Larger buffer for smoother playback
audio_stream = None
audio_playback_buffer = np.array([], dtype=np.float32)  # Continuous buffer for smooth playback

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


def setup_audio_playback():
    """Initialize audio playback stream."""
    global audio_stream, audio_playback_buffer
    if not ENABLE_AUDIO_PLAYBACK or not AUDIO_PLAYBACK_AVAILABLE:
        return False
    
    try:
        # Initialize the buffer
        audio_playback_buffer = np.array([], dtype=np.float32)
        
        # List available audio devices for debugging
        devices = sd.query_devices()
        print(f"🔊 Available audio devices: {len(devices)} found")
        
        # Initialize audio stream for playback with smaller buffer for lower latency
        audio_stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=1,  # Mono audio
            dtype=np.float32,
            blocksize=AUDIO_BUFFER_SIZE,
            device=AUDIO_PLAYBACK_DEVICE,
            callback=audio_playback_callback,
            latency='low'  # Request low latency
        )
        audio_stream.start()
        print(f"✅ Audio playback initialized (device: {audio_stream.device}, volume: {AUDIO_PLAYBACK_VOLUME})")
        print(f"   Buffer size: {AUDIO_BUFFER_SIZE} samples, Latency: {audio_stream.latency:.3f}s")
        return True
    except Exception as e:
        print(f"⚠️ Failed to initialize audio playback: {e}")
        return False


def audio_playback_callback(outdata, frames, time, status):
    """Callback function for audio playback with continuous buffering."""
    global audio_playback_buffer
    
    if status:
        print(f"⚠️ Audio playback status: {status}")
    
    try:
        # Fill buffer from queue if we don't have enough data
        while len(audio_playback_buffer) < frames:
            try:
                new_chunk = audio_playback_queue.get_nowait()
                audio_playback_buffer = np.concatenate([audio_playback_buffer, new_chunk])
            except queue.Empty:
                # If no more data available, break and pad with zeros if needed
                break
        
        # Extract the required number of frames
        if len(audio_playback_buffer) >= frames:
            # We have enough data
            output_data = audio_playback_buffer[:frames]
            audio_playback_buffer = audio_playback_buffer[frames:]  # Remove used data
            
            # Apply volume control and output
            outdata[:, 0] = output_data * AUDIO_PLAYBACK_VOLUME
        else:
            # Not enough data, output what we have and pad with zeros
            if len(audio_playback_buffer) > 0:
                outdata[:len(audio_playback_buffer), 0] = audio_playback_buffer * AUDIO_PLAYBACK_VOLUME
                outdata[len(audio_playback_buffer):, 0] = 0
                audio_playback_buffer = np.array([], dtype=np.float32)  # Clear buffer
            else:
                # No data at all, output silence
                outdata[:, 0] = 0
                
    except Exception as e:
        # On any error, output silence and continue
        outdata[:, 0] = 0


def cleanup_audio_playback():
    """Clean up audio playback resources."""
    global audio_stream, audio_playback_buffer
    if audio_stream:
        try:
            audio_stream.stop()
            audio_stream.close()
            print("🔇 Audio playback stopped")
        except Exception as e:
            print(f"⚠️ Error stopping audio playback: {e}")
        finally:
            audio_stream = None
            audio_playback_buffer = np.array([], dtype=np.float32)  # Clear buffer


def start_ffmpeg_stream(stream_url, max_retries=3):
    """Start ffmpeg process that outputs raw PCM audio from the stream."""
    
    # Different FFmpeg options based on stream type
    if stream_url.startswith("http://"):
        # HTTP stream - add HTTP-specific options
        cmd = [
            "ffmpeg",
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "5",
            "-timeout", "10000000",  # 10 second timeout for HTTP
            "-user_agent", "live-transcription-client",
            "-i", stream_url,
            "-f", "s16le",  # PCM 16-bit little-endian
            "-acodec", "pcm_s16le",
            "-ac", "1",  # mono
            "-ar", str(SAMPLE_RATE),
            "-loglevel", "error",  # Show errors but reduce verbosity
            "pipe:1"
        ]
    else:
        # UDP stream - use original options
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
            time.sleep(2)  # Give HTTP streams more time to establish connection
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
            
            # Add to transcription queue, drop oldest if full
            try:
                audio_queue.put_nowait(audio)
            except queue.Full:
                try:
                    audio_queue.get_nowait()  # Remove oldest
                    audio_queue.put_nowait(audio)  # Add new
                    print("⚠️ Audio buffer full, dropping old data")
                except queue.Empty:
                    pass
            
            # Add to audio playback queue if enabled (independent operation)
            if ENABLE_AUDIO_PLAYBACK and AUDIO_PLAYBACK_AVAILABLE:
                try:
                    # For audio playback, we want smaller, more frequent chunks for smoother playback
                    # Send the entire audio chunk to the playback queue without splitting
                    # The callback will handle buffering appropriately
                    audio_playback_queue.put_nowait(audio.copy())
                        
                except queue.Full:
                    # Drop old audio data if playback buffer is full
                    try:
                        audio_playback_queue.get_nowait()  # Remove oldest
                        audio_playback_queue.put_nowait(audio.copy())  # Add new
                    except queue.Empty:
                        pass
                except Exception as e:
                    # Don't let playback errors affect transcription
                    pass
                    
        except Exception as e:
            print(f"❌ Audio reader error: {e}")
            break


def transcriber():
    """Reads chunks from the queue and transcribes them."""
    print("🎙️  Live transcription started...\n")
    chunk_count = 0
    total_filtered_words = 0
    total_processing_time = 0

    while True:
        try:
            audio = audio_queue.get(timeout=5)  # 5 second timeout
            if audio is None:
                break

            chunk_count += 1
            current_time = time.time() - start_time if start_time else 0
            
            # Start timing the complete processing pipeline
            processing_start = time.time()
            
            # Transcription step
            segments, _ = model.transcribe(audio, language=LANGUAGE)
            
            # Process each segment and measure complete pipeline time
            for segment in segments:
                timestamp_str = f"[{current_time:.1f}s]"
                text = segment.text.strip()
                
                if text:  # Only process non-empty transcriptions
                    # Apply profanity filter if enabled (this is part of processing time)
                    console_text = text
                    file_text = text
                    
                    if profanity_filter:
                        # Get colored version for console
                        console_text, filter_stats = profanity_filter.filter_text(text, for_console=True)
                        # Get plain version for file
                        file_text, _ = profanity_filter.filter_text(text, for_console=False)
                        
                        if filter_stats.get("words_filtered", 0) > 0:
                            total_filtered_words += filter_stats["words_filtered"]
                    
                    # End timing here - after all processing is complete
                    processing_end = time.time()
                    processing_time = processing_end - processing_start
                    total_processing_time += processing_time
                    
                    # Prepare output with optional processing time
                    if SHOW_PROCESSING_TIME:
                        processing_str = f"[⚡{processing_time:.3f}s]"
                        console_output = f"{timestamp_str} {processing_str} {console_text}"
                        file_output = f"{timestamp_str} {processing_str} {file_text}"
                    else:
                        console_output = f"{timestamp_str} {console_text}"
                        file_output = f"{timestamp_str} {file_text}"
                    
                    print(console_output)
                    
                    # Save to file if enabled
                    if transcript_file:
                        transcript_file.write(f"{file_output}\n")
                        transcript_file.flush()
                        
        except queue.Empty:
            print("⏳ Waiting for audio data...")
            continue
        except Exception as e:
            print(f"⚠️ Transcription error: {e}", file=sys.stderr)


def main():
    global ENABLE_PROFANITY_FILTER, profanity_filter, FILTER_TYPE
    global ENABLE_AUDIO_PLAYBACK, AUDIO_PLAYBACK_VOLUME, AUDIO_PLAYBACK_DEVICE
    global SHOW_PROCESSING_TIME
    
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
    
    # Audio playback arguments
    parser.add_argument('--enable-audio', action='store_true',
                        help='Enable live audio playback of the stream')
    parser.add_argument('--audio-volume', type=float, default=AUDIO_PLAYBACK_VOLUME,
                        help=f'Audio playback volume (0.0 to 1.0, default: {AUDIO_PLAYBACK_VOLUME})')
    parser.add_argument('--audio-device', type=int, default=AUDIO_PLAYBACK_DEVICE,
                        help='Audio output device index (default: system default)')
    parser.add_argument('--list-audio-devices', action='store_true',
                        help='List available audio devices and exit')
    
    # Performance monitoring arguments
    parser.add_argument('--show-timing', action='store_true', default=SHOW_PROCESSING_TIME,
                        help='Show processing time for each transcription chunk')
    parser.add_argument('--no-timing', action='store_true',
                        help='Hide processing time information')
    
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
    
    # Handle audio device listing
    if args.list_audio_devices:
        if AUDIO_PLAYBACK_AVAILABLE:
            print("🔊 Available audio devices:")
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                device_type = "🎧" if device['max_output_channels'] > 0 else "🎤"
                default_marker = " (default)" if i == sd.default.device[1] else ""
                print(f"   {i}: {device_type} {device['name']}{default_marker}")
                print(f"      Max output channels: {device['max_output_channels']}")
                print(f"      Sample rate: {device['default_samplerate']}")
        else:
            print("❌ sounddevice not available. Install with: pip install sounddevice")
        return
    
    # Override global settings based on arguments
    
    FILTER_TYPE = args.filter_type
    
    # Handle audio playback settings
    if args.enable_audio:
        if AUDIO_PLAYBACK_AVAILABLE:
            ENABLE_AUDIO_PLAYBACK = True
            AUDIO_PLAYBACK_VOLUME = max(0.0, min(1.0, args.audio_volume))  # Clamp between 0.0 and 1.0
            AUDIO_PLAYBACK_DEVICE = args.audio_device
            print(f"🔊 Audio playback enabled (volume: {AUDIO_PLAYBACK_VOLUME}, device: {AUDIO_PLAYBACK_DEVICE or 'default'})")
        else:
            print("⚠️ Audio playback requested but sounddevice not available")
            print("   Install with: pip install sounddevice")
            ENABLE_AUDIO_PLAYBACK = False
    
    # Handle timing display settings
    if args.no_timing:
        SHOW_PROCESSING_TIME = False
    elif args.show_timing:
        SHOW_PROCESSING_TIME = True
    
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
    
    # Show audio playback information
    if ENABLE_AUDIO_PLAYBACK:
        if AUDIO_PLAYBACK_AVAILABLE:
            device_info = f"device {AUDIO_PLAYBACK_DEVICE}" if AUDIO_PLAYBACK_DEVICE is not None else "default device"
            print(f"   Audio Playback: Enabled (volume: {AUDIO_PLAYBACK_VOLUME}, {device_info})")
        else:
            print(f"   Audio Playback: Disabled (sounddevice not available)")
    else:
        print(f"   Audio Playback: Disabled")
    
    # Show timing information setting
    timing_status = "Enabled" if SHOW_PROCESSING_TIME else "Disabled"
    print(f"   Processing Time Display: {timing_status}")
    
    print("=" * 50)
    
    # Setup transcript file
    transcript_filename = setup_transcript_file()
    
    # Setup audio playback if enabled
    audio_playback_initialized = False
    if ENABLE_AUDIO_PLAYBACK:
        audio_playback_initialized = setup_audio_playback()
    
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
        if audio_playback_initialized:
            print("🔊 Live audio playback is active")
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
        
        # Cleanup audio playback
        if audio_playback_initialized:
            cleanup_audio_playback()
        
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
        
        # Show transcription performance statistics
        if 'transcriber_thread' in locals() and hasattr(transcriber, '__globals__'):
            print("\n⚡ Transcription Performance Statistics:")
            # These would be accessible if we made them global or returned them
            # For now, this is a placeholder for future enhancement


if __name__ == "__main__":
    main()
