"""
OpenAI Realtime API Voice Agent - Terminal Application (EXERCISE VERSION).

This script demonstrates real-time voice conversation with OpenAI's Realtime API.
It provides direct speech-to-speech interaction without intermediate text processing.

EXERCISE: Complete the TODOs to make the voice agent work.

Requirements:
    pip install websockets sounddevice numpy

Usage:
    python W4_realtime_voice_agent_BLANK.py

Press Ctrl+C to exit.
"""

import os
import sys
import json
import base64
import asyncio
import argparse
import numpy as np
from pathlib import Path

try:
    import websockets
    import sounddevice as sd
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install websockets sounddevice numpy")
    sys.exit(1)

from dotenv import load_dotenv
# Load .env from project root (two levels up from bonus/)
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REALTIME_MODEL = "gpt-4o-realtime-preview"
REALTIME_URL = f"wss://api.openai.com/v1/realtime?model={REALTIME_MODEL}"

# Audio settings (OpenAI Realtime API requirements)
SAMPLE_RATE = 24000  # 24kHz required by OpenAI
CHANNELS = 1         # Mono
DTYPE = np.int16     # PCM16
CHUNK_SIZE = 2400    # 100ms chunks at 24kHz

# Voice options: alloy, ash, ballad, coral, echo, sage, shimmer, verse
VOICE = "alloy"

# System prompt for the assistant
SYSTEM_INSTRUCTIONS = """You are a helpful, friendly voice assistant.
Keep your responses concise and conversational since this is a voice interaction.
If you don't understand something, ask for clarification.
Be natural and engaging in your responses."""


class RealtimeVoiceAgent:
    """Real-time voice agent using OpenAI's Realtime API."""

    def __init__(self):
        self.websocket = None
        self.is_running = False
        self.audio_queue = asyncio.Queue()
        self.playback_queue = asyncio.Queue()
        self.is_speaking = False

    async def connect(self):
        """Establish WebSocket connection to OpenAI Realtime API."""

        # =================================================================
        # TODO 1: Create the headers dict for WebSocket authentication
        # =================================================================
        # The OpenAI Realtime API requires two headers:
        # - "Authorization": Bearer token with your API key
        # - "OpenAI-Beta": Set to "realtime=v1" to enable the beta API
        #
        # Hint: Use f-string to include OPENAI_API_KEY in the Bearer token
        # =================================================================
        headers = {
            # YOUR CODE HERE
            # "Authorization": ...,
            # "OpenAI-Beta": ...
        }

        print(f"Connecting to OpenAI Realtime API...")
        self.websocket = await websockets.connect(
            REALTIME_URL,
            additional_headers=headers,
            ping_interval=20,
            ping_timeout=20
        )
        print("Connected!")

        # Configure the session
        await self.configure_session()

    async def configure_session(self):
        """Send session configuration to OpenAI."""

        # =================================================================
        # TODO 2: Complete the session configuration
        # =================================================================
        # Configure the realtime session with:
        # - modalities: List containing "text" and "audio"
        # - instructions: The system prompt (use SYSTEM_INSTRUCTIONS)
        # - voice: The voice to use (use VOICE constant)
        # - input_audio_format: "pcm16"
        # - output_audio_format: "pcm16"
        # - input_audio_transcription: {"model": "whisper-1"}
        # - turn_detection: Server VAD with threshold 0.5,
        #   prefix_padding_ms 300, silence_duration_ms 500
        #
        # Docs: https://platform.openai.com/docs/api-reference/realtime
        # =================================================================
        config = {
            "type": "session.update",
            "session": {
                # YOUR CODE HERE
                # "modalities": [...],
                # "instructions": ...,
                # "voice": ...,
                # "input_audio_format": ...,
                # "output_audio_format": ...,
                # "input_audio_transcription": {...},
                # "turn_detection": {...}
            }
        }

        await self.websocket.send(json.dumps(config))
        print(f"Session configured with voice: {VOICE}")

    async def send_audio(self):
        """Capture audio from microphone and send to API."""
        print("Microphone ready. Start speaking...")

        def audio_callback(indata, frames, time, status):
            """Callback for audio input stream."""
            if status:
                print(f"Audio input status: {status}")
            # Put audio data in queue for async processing
            audio_bytes = indata.tobytes()
            try:
                self.audio_queue.put_nowait(audio_bytes)
            except asyncio.QueueFull:
                pass  # Drop frame if queue is full

        # Start audio input stream
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=CHUNK_SIZE,
            callback=audio_callback
        )

        with stream:
            while self.is_running:
                try:
                    # Get audio from queue
                    audio_bytes = await asyncio.wait_for(
                        self.audio_queue.get(),
                        timeout=0.1
                    )

                    # =================================================================
                    # TODO 3: Encode audio and create message to send to API
                    # =================================================================
                    # Steps:
                    # 1. Encode audio_bytes to base64 string using base64.b64encode()
                    #    then decode to UTF-8 string
                    # 2. Create a message dict with:
                    #    - "type": "input_audio_buffer.append"
                    #    - "audio": the base64 encoded audio string
                    # 3. Send the message as JSON through the websocket
                    #
                    # Hint: Use json.dumps() to convert dict to JSON string
                    # =================================================================

                    # YOUR CODE HERE
                    # audio_base64 = ...
                    # message = {...}
                    # await self.websocket.send(...)

                    pass  # Remove this when you add your code

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    if self.is_running:
                        print(f"Send error: {e}")

    async def receive_messages(self):
        """Receive and process messages from the API."""
        audio_buffer = []

        while self.is_running:
            try:
                message = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=0.1
                )
                event = json.loads(message)
                event_type = event.get("type", "")

                # Handle different event types
                if event_type == "session.created":
                    print("Session created successfully")

                elif event_type == "session.updated":
                    print("Session updated")

                elif event_type == "input_audio_buffer.speech_started":
                    print("Listening...")
                    self.is_speaking = False

                elif event_type == "input_audio_buffer.speech_stopped":
                    print("Processing...")

                elif event_type == "conversation.item.input_audio_transcription.completed":
                    # User's speech transcription
                    transcript = event.get("transcript", "")
                    if transcript:
                        print(f"You: {transcript}")

                elif event_type == "response.audio_transcript.delta":
                    # Partial AI response text
                    delta = event.get("delta", "")
                    print(delta, end="", flush=True)

                elif event_type == "response.audio_transcript.done":
                    # AI response complete
                    print()  # New line

                elif event_type == "response.audio.delta":
                    # =================================================================
                    # TODO 4: Handle incoming audio chunk from AI
                    # =================================================================
                    # Steps:
                    # 1. Set self.is_speaking = True
                    # 2. Get the base64 audio from event.get("delta", "")
                    # 3. If there's audio data, decode it from base64 using
                    #    base64.b64decode() and append to audio_buffer list
                    #
                    # Note: Audio comes in chunks that we accumulate in audio_buffer
                    # =================================================================

                    # YOUR CODE HERE
                    pass  # Remove this when you add your code

                elif event_type == "response.audio.done":
                    # Play accumulated audio
                    if audio_buffer:
                        await self.play_audio(b''.join(audio_buffer))
                        audio_buffer = []
                    self.is_speaking = False

                elif event_type == "response.done":
                    print("Response complete")

                elif event_type == "error":
                    error = event.get("error", {})
                    print(f"Error: {error.get('message', 'Unknown error')}")

            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break
            except Exception as e:
                if self.is_running:
                    print(f"Receive error: {e}")

    async def play_audio(self, audio_bytes: bytes):
        """Play audio through speakers."""
        try:
            # =================================================================
            # TODO 5: Convert audio bytes to numpy array and play
            # =================================================================
            # Steps:
            # 1. Convert audio_bytes to numpy array using np.frombuffer()
            #    with dtype=DTYPE (which is np.int16)
            # 2. Play the audio using sd.play(array, samplerate=SAMPLE_RATE)
            # 3. Wait for playback to complete using sd.wait()
            #
            # Hint: np.frombuffer(audio_bytes, dtype=DTYPE)
            # =================================================================

            # YOUR CODE HERE
            # audio_array = ...
            # sd.play(...)
            # sd.wait()

            pass  # Remove this when you add your code

        except Exception as e:
            print(f"Playback error: {e}")

    async def run(self):
        """Main run loop."""
        if not OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY not found in environment")
            print("   Set it in your .env file or export it")
            return

        try:
            await self.connect()
            self.is_running = True

            print("\n" + "=" * 50)
            print("  VOICE AGENT READY")
            print("=" * 50)
            print("Speak naturally - the AI will respond with voice.")
            print("Press Ctrl+C to exit.\n")

            # Run send and receive concurrently
            await asyncio.gather(
                self.send_audio(),
                self.receive_messages()
            )

        except KeyboardInterrupt:
            print("\n\nShutting down...")
        except Exception as e:
            print(f"Fatal error: {e}")
        finally:
            self.is_running = False
            if self.websocket:
                await self.websocket.close()
            print("Disconnected")


def check_audio_devices():
    """Check and display available audio devices."""
    print("\nAudio Devices:")
    print("-" * 40)

    try:
        devices = sd.query_devices()
        default_input = sd.query_devices(kind='input')
        default_output = sd.query_devices(kind='output')

        print(f"Input:  {default_input['name']}")
        print(f"Output: {default_output['name']}")
        print("-" * 40)
        return True
    except Exception as e:
        print(f"Audio device error: {e}")
        return False


def main():
    """Entry point."""
    print("\n" + "=" * 50)
    print("   OpenAI Realtime Voice Agent (EXERCISE)")
    print("=" * 50)

    # Check audio devices
    if not check_audio_devices():
        print("Please check your audio configuration.")
        sys.exit(1)

    # Create and run agent
    agent = RealtimeVoiceAgent()
    asyncio.run(agent.run())


if __name__ == "__main__":
    main()
