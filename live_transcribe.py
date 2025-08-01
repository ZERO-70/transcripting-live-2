import subprocess
import numpy as np
import threading
import queue
import time
import sys
import argparse
from datetime import datetime
from faster_whisper import WhisperModel

# ----- CONFIG -----
UDP_STREAM_URL = "udp://127.0.0.1:1234"
HTTP_STREAM_URL = "http://127.0.0.1:8080"
SAMPLE_RATE = 16000
CHUNK_DURATION = 3  # in seconds
MODEL_NAME = "tiny"  # tiny/int8 recommended for CPU
LANGUAGE = "en"
MAX_QUEUE_SIZE = 10  # Prevent memory buildup
SAVE_TRANSCRIPT = True  # Save to file
# -------------------

# Set up transcription model (CPU-friendly)
print("🤖 Loading Whisper model...")
model = WhisperModel(MODEL_NAME, compute_type="int8")
print(f"✅ Model '{MODEL_NAME}' loaded successfully")

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
                
                if text:  # Only print non-empty transcriptions
                    output_line = f"{timestamp_str} {text}"
                    print(output_line)
                    
                    # Save to file if enabled
                    if transcript_file:
                        transcript_file.write(f"{output_line}\n")
                        transcript_file.flush()
                        
        except queue.Empty:
            print("⏳ Waiting for audio data...")
            continue
        except Exception as e:
            print(f"⚠️ Transcription error: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Live transcription of video stream')
    parser.add_argument('--stream', choices=['udp', 'http'], default='udp',
                        help='Stream type to connect to (default: udp)')
    parser.add_argument('--model', default=MODEL_NAME,
                        help=f'Whisper model to use (default: {MODEL_NAME})')
    parser.add_argument('--language', default=LANGUAGE,
                        help=f'Language for transcription (default: {LANGUAGE})')
    
    args = parser.parse_args()
    
    # Choose stream URL based on argument
    stream_url = HTTP_STREAM_URL if args.stream == 'http' else UDP_STREAM_URL
    
    print(f"🚀 Starting live transcription")
    print(f"   Stream: {stream_url}")
    print(f"   Model: {args.model}")
    print(f"   Language: {args.language}")
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

        print("\n🎯 Transcription running... Press Ctrl+C to stop\n")
        
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


if __name__ == "__main__":
    main()
