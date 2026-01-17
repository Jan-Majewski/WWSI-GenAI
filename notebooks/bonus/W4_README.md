# W4 - Voice-Enabled AI Applications (Bonus)

This bonus module demonstrates voice interaction with AI using OpenAI's audio APIs.

## Overview

Two approaches to voice-enabled AI:

| Approach | File | Type | Best For |
|----------|------|------|----------|
| **STT→LLM→TTS** | `W4_voice_chat_app.py` | Streamlit | Learning, demos, flexibility |
| **Realtime API** | `W4_realtime_voice_agent.py` | Terminal | Low latency, production |

---

## Files

```
notebooks/bonus/
├── W4_README.md                      # This file
├── W4_voice_utils.py                 # STT/TTS helper functions
├── W4_voice_chat_app.py              # Streamlit voice chat (complete)
├── W4_voice_chat_app_BLANK.py        # Exercise version (5 TODOs)
├── W4_realtime_voice_agent.py        # Terminal app (complete)
├── W4_realtime_voice_agent_BLANK.py  # Exercise version (5 TODOs)
├── W4_on_premise_LLMs.ipynb          # Running local LLMs with LM Studio
└── requirements.txt                  # Voice-specific dependencies
```

---

## Exercises

Both apps have BLANK versions with TODOs for hands-on learning:

### W4_voice_chat_app_BLANK.py (5 TODOs)
| TODO | Topic | What to implement |
|------|-------|-------------------|
| 1 | Hashing | Compute MD5 hash of audio bytes |
| 2 | LLM | Get AI response from chatbot |
| 3 | TTS | Generate speech from AI response |
| 4 | State | Add AI message to chat history |
| 5 | STT | Transcribe audio with Whisper |

### W4_realtime_voice_agent_BLANK.py (5 TODOs)
| TODO | Topic | What to implement |
|------|-------|-------------------|
| 1 | Auth | WebSocket headers (Authorization, OpenAI-Beta) |
| 2 | Config | Session configuration (modalities, VAD, voice) |
| 3 | Send | Encode audio to base64 and send to API |
| 4 | Receive | Decode incoming audio chunks from API |
| 5 | Playback | Convert bytes to numpy array and play |

---

## Approach 1: STT → LLM → TTS Pipeline

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ st.audio_    │───▶│   Whisper    │───▶│   GPT-4o     │  │
│  │ input()      │    │   (STT)      │    │   (Chat)     │  │
│  │ [Record]     │    │              │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                 │           │
│  ┌──────────────┐    ┌──────────────┐          │           │
│  │ st.audio()   │◀───│   TTS-1      │◀─────────┘           │
│  │ [Playback]   │    │   (TTS)      │                      │
│  └──────────────┘    └──────────────┘                      │
├─────────────────────────────────────────────────────────────┤
│              W3_chat_with_memory.py (reused)                │
└─────────────────────────────────────────────────────────────┘
```

### OpenAI Models Used
| Stage | Model | Purpose |
|-------|-------|---------|
| STT | `whisper-1` | Convert speech to text |
| LLM | `gpt-4o` | Generate response (from W3) |
| TTS | `tts-1` | Convert text to speech |

### How to Run
```bash
cd notebooks/bonus
streamlit run W4_voice_chat_app.py
```

### Features
- Voice input via microphone (native `st.audio_input`)
- Text input fallback
- **Language selection** for transcription (English, Polish, German, Spanish, French, Auto-detect)
- Multiple AI voice options (nova, alloy, echo, etc.)
- Conversation memory (reuses W3 backend)
- **Auto-play** audio responses (configurable in sidebar)

---

## Approach 2: OpenAI Realtime API

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                  Terminal / Python Script                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐         WebSocket          ┌───────────┐ │
│  │  Microphone  │◀──────────────────────────▶│  OpenAI   │ │
│  │  (sounddevice)│   wss://api.openai.com    │  Realtime │ │
│  └──────────────┘    /v1/realtime            │    API    │ │
│         │                                          │        │
│         ▼                                          ▼        │
│  ┌──────────────┐                            ┌───────────┐ │
│  │   Speaker    │◀───── Audio Deltas ────────│ gpt-4o-   │ │
│  │  (sounddevice)│                           │ realtime- │ │
│  └──────────────┘                            │ preview   │ │
└─────────────────────────────────────────────────────────────┘
```

### OpenAI Models Used
| Component | Model | Purpose |
|-----------|-------|---------|
| Realtime | `gpt-4o-realtime-preview` | Direct speech-to-speech |

### How to Run
```bash
# Install additional dependencies
pip install websockets sounddevice numpy

# Run from project root
python notebooks/bonus/W4_realtime_voice_agent.py
```

### Features
- Real-time bidirectional audio
- Server-side Voice Activity Detection (VAD)
- Automatic turn-taking
- Streaming audio output
- Input transcription (for debugging)

### Controls
- Speak naturally - AI detects when you stop
- Press `Ctrl+C` to exit

---

## Prerequisites

### 1. Install Dependencies

```bash
# Install all W4 voice dependencies
cd notebooks/bonus
pip install -r requirements.txt
```

Or install manually:
```bash
pip install openai streamlit python-dotenv websockets sounddevice numpy
```

### 2. API Keys

Ensure your `.env` file (in project root) contains:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Audio Devices

- Working microphone
- Working speakers/headphones
- Grant browser microphone permission (for Streamlit)

---

## Voice Options

Available TTS voices for `W4_voice_chat_app.py`:

| Voice | Description |
|-------|-------------|
| `alloy` | Neutral, balanced |
| `ash` | Neutral |
| `coral` | Warm female |
| `echo` | Male |
| `fable` | British accent |
| `onyx` | Deep male |
| `nova` | Friendly female (recommended) |
| `sage` | Neutral |
| `shimmer` | Expressive female |

---

## Comparison

| Feature | STT→LLM→TTS | Realtime API |
|---------|-------------|--------------|
| Latency | ~3-5 seconds | ~200-500ms |
| Flexibility | High (swap components) | Low (integrated) |
| Complexity | Lower | Higher |
| UI | Streamlit (web) | Terminal |
| Interruptions | Not supported | Supported |
| Language Selection | Yes (sidebar) | Server-side detection |
| Auto-play Audio | Yes (configurable) | Automatic |
| Cost | Separate API calls | Single API |

---

## Troubleshooting

### Microphone not working (Streamlit)
- Check browser permissions
- Ensure HTTPS or localhost
- Try a different browser

### No audio output (Realtime)
- Check `sounddevice` can detect your speakers:
  ```python
  import sounddevice as sd
  print(sd.query_devices())
  ```

### WebSocket connection failed
- Verify `OPENAI_API_KEY` is set
- Check internet connection
- Ensure API key has Realtime API access

---

## API Cost Estimates

| API | Cost |
|-----|------|
| Whisper (STT) | $0.006 per minute |
| GPT-4o (Chat) | $2.50/1M input, $10/1M output |
| TTS-1 | $15 per 1M characters |
| Realtime API | $5/1M input, $20/1M output (audio) |

---

## Summary

| File | Command | Notes |
|------|---------|-------|
| `W4_voice_chat_app.py` | `streamlit run W4_voice_chat_app.py` | Run from `notebooks/bonus/` |
| `W4_realtime_voice_agent.py` | `python W4_realtime_voice_agent.py` | Run from project root |
| `W4_voice_utils.py` | (imported) | Helper functions |
