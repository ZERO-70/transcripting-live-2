# 🔧 HTTP Streaming + Live Transcription Setup Guide

## ✅ **Changes Made:**

### **1. Fixed HTTP Streaming (Multiple Connections)**
- Added `-multiple_requests 1` to support multiple simultaneous connections
- Added `-listen_timeout -1` to prevent connection timeouts
- Updated streaming description to clarify multiple connection support

### **2. Enhanced Live Transcription HTTP Support**
- Added HTTP-specific FFmpeg options in transcription
- Added timeout and user-agent for better HTTP compatibility
- Increased connection timeout for HTTP streams

### **3. New Runner Commands**
- Added `stream-http` command for direct HTTP streaming
- Enhanced argument handling for HTTP mode

## 🚀 **How to Use (Multiple Connections):**

### **Method 1: HTTP Streaming (Recommended for Multiple Connections)**

#### **Step 1: Start HTTP Streaming (Terminal 1)**
```bash
cd /home/zair/Documents/stream

# Option A: Direct HTTP streaming
python3 run.py stream-http

# Option B: Interactive mode
python3 run.py stream
# Choose option 2 (HTTP)
```

#### **Step 2: Connect VLC (Optional)**
1. Open VLC Media Player
2. Go to **Media** → **Open Network Stream**
3. Enter: `http://127.0.0.1:8080`
4. Click **Play**

#### **Step 3: Start Live Transcription (Terminal 2)**
```bash
cd /home/zair/Documents/stream

# With dictionary filter
python3 run.py transcribe-dict --stream http

# With AI model filter
python3 run.py transcribe-model --stream http

# Without filter
python3 run.py transcribe-nofilter --stream http
```

### **Method 2: UDP Streaming (Single Connection)**

#### **Step 1: Start UDP Streaming (Terminal 1)**
```bash
python3 run.py stream
# Choose option 1 (UDP) or press Enter
```

#### **Step 2: Connect VLC OR Transcription (not both simultaneously)**
```bash
# Either VLC: udp://@:1234
# OR transcription:
python3 run.py transcribe-dict --stream udp
```

## 📊 **Connection Support Comparison:**

| Stream Type | Multiple Connections | VLC + Transcription | Reliability |
|-------------|---------------------|---------------------|-------------|
| **HTTP** | ✅ Yes | ✅ Simultaneous | ⭐⭐⭐⭐ |
| **UDP** | ❌ No | ❌ One at a time | ⭐⭐⭐ |

## 🎯 **Complete Workflow (HTTP + Multiple Connections):**

### **Terminal 1: Start HTTP Streaming**
```bash
cd /home/zair/Documents/stream
python3 run.py stream-http
```
**Expected output:**
```
🚀 Running stream-http...
📹 Using video file: video1.mp4
Streaming via HTTP at http://127.0.0.1:8080
Multiple connections supported:
  - VLC: Open network stream: http://127.0.0.1:8080
  - Live transcription can connect simultaneously
Press Ctrl+C to stop.
```

### **Terminal 2: Start Live Transcription**
```bash
cd /home/zair/Documents/stream
python3 run.py transcribe-dict --stream http
```

### **VLC: Connect Simultaneously**
- Open VLC → Media → Open Network Stream
- URL: `http://127.0.0.1:8080`

## ✨ **Benefits of HTTP Streaming:**

1. **✅ Multiple Connections**: VLC + transcription can run simultaneously
2. **✅ More Reliable**: Better error handling and reconnection
3. **✅ Flexible**: Clients can connect/disconnect anytime
4. **✅ Better Debugging**: Clearer error messages

## 🛠️ **Technical Details:**

### **HTTP Streaming Command:**
```bash
ffmpeg -re -stream_loop -1 -i video.mp4 \
  -c:v libx264 -preset ultrafast -c:a aac \
  -f mpegts -listen 1 -listen_timeout -1 \
  -multiple_requests 1 http://127.0.0.1:8080
```

### **HTTP Transcription Command:**
```bash
ffmpeg -reconnect 1 -reconnect_streamed 1 \
  -timeout 10000000 -user_agent live-transcription-client \
  -i http://127.0.0.1:8080 \
  -f s16le -acodec pcm_s16le -ac 1 -ar 16000 pipe:1
```

---

**🎉 Your setup now supports multiple simultaneous connections!**
