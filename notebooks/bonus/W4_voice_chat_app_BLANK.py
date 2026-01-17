"""
Voice-Enabled Chat Application using Streamlit (EXERCISE VERSION).

This app wraps the existing W3_chat_with_memory.py chatbot with voice capabilities:
- Speech-to-Text (STT) using OpenAI Whisper
- Text-to-Speech (TTS) using OpenAI TTS API

Architecture: STT (Whisper) -> LLM (GPT-4o) -> TTS (tts-1)

EXERCISE: Complete the TODOs to make the voice chat work.

Run from the bonus directory:
    cd notebooks/bonus
    streamlit run W4_voice_chat_app_BLANK.py
"""

import streamlit as st
import sys
import hashlib
from pathlib import Path

# Add parent directory to path to import W3 modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from W3_chat_with_memory import chatbot_response
from W4_voice_utils import transcribe_audio, text_to_speech, AVAILABLE_VOICES

# Page configuration
st.set_page_config(
    page_title="Voice Chat Assistant",
    page_icon="🎙️",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .user-message {
        background-color: #e3f2fd;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 85%;
        float: right;
        clear: both;
    }
    .ai-message {
        background-color: #f5f5f5;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        float: left;
        clear: both;
    }
    .message-container {
        width: 100%;
        overflow: hidden;
        margin-bottom: 12px;
    }
    .voice-indicator {
        color: #1976d2;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "nova"

if "auto_play" not in st.session_state:
    st.session_state.auto_play = True

if "transcription_language" not in st.session_state:
    st.session_state.transcription_language = "en"

if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None

if "audio_input_key" not in st.session_state:
    st.session_state.audio_input_key = 0

if "input_mode" not in st.session_state:
    st.session_state.input_mode = "voice"

# Language options for Whisper
LANGUAGE_OPTIONS = {
    "English": "en",
    "Polish": "pl",
    "German": "de",
    "Spanish": "es",
    "French": "fr",
    "Auto-detect": None
}

# App header
st.title("🎙️ Voice Chat Assistant")
st.markdown("*Talk to an AI that remembers your conversation*")

# Sidebar settings
with st.sidebar:
    st.header("Settings")

    # Voice settings
    st.subheader("Voice Settings")
    st.session_state.voice_enabled = st.toggle("Enable Voice Output", value=st.session_state.voice_enabled)

    if st.session_state.voice_enabled:
        st.session_state.selected_voice = st.selectbox(
            "AI Voice",
            AVAILABLE_VOICES,
            index=AVAILABLE_VOICES.index(st.session_state.selected_voice),
            help="Choose the voice for AI responses"
        )
        st.session_state.auto_play = st.toggle("Auto-play responses", value=st.session_state.auto_play)

    st.divider()

    # Transcription settings
    st.subheader("Transcription Settings")
    selected_lang_name = st.selectbox(
        "Input Language",
        list(LANGUAGE_OPTIONS.keys()),
        index=list(LANGUAGE_OPTIONS.keys()).index(
            next((k for k, v in LANGUAGE_OPTIONS.items() if v == st.session_state.transcription_language), "English")
        ),
        help="Language for speech recognition."
    )
    st.session_state.transcription_language = LANGUAGE_OPTIONS[selected_lang_name]

    st.divider()

    if st.button("New Conversation", use_container_width=True):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.processed_audio_hash = None
        st.session_state.audio_input_key += 1
        st.rerun()

# Display chat history
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    content = message["content"]

    with st.container():
        if role == "human":
            voice_tag = ' <span class="voice-indicator">🎤</span>' if message.get("from_voice") else ""
            st.markdown(
                f'<div class="message-container"><div class="user-message">{content}{voice_tag}</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="message-container"><div class="ai-message">{content}</div></div>',
                unsafe_allow_html=True
            )
            # Show audio player for AI messages if available
            if message.get("audio") and st.session_state.voice_enabled:
                is_latest = (idx == len(st.session_state.messages) - 1)
                should_autoplay = st.session_state.auto_play and is_latest and message.get("just_generated", False)
                st.audio(message["audio"], format="audio/mp3", autoplay=should_autoplay)
                if should_autoplay:
                    message["just_generated"] = False

# Input section
st.divider()

# Input mode toggle
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button(
            "🎤 Voice",
            use_container_width=True,
            type="primary" if st.session_state.input_mode == "voice" else "secondary"
        ):
            st.session_state.input_mode = "voice"
            st.rerun()
    with mode_col2:
        if st.button(
            "⌨️ Text",
            use_container_width=True,
            type="primary" if st.session_state.input_mode == "text" else "secondary"
        ):
            st.session_state.input_mode = "text"
            st.rerun()

# Show selected input mode
audio_input = None
text_input = None

if st.session_state.input_mode == "voice":
    lang_hint = f"({selected_lang_name})" if st.session_state.transcription_language else "(Auto)"
    audio_input = st.audio_input(
        f"Record your message {lang_hint}",
        key=f"voice_recorder_{st.session_state.audio_input_key}",
        help="Click to record, click again to stop"
    )
else:
    text_input = st.chat_input("Type your message here...")


def compute_audio_hash(audio_bytes: bytes) -> str:
    """Compute hash of audio bytes to detect duplicates."""
    # =================================================================
    # TODO 1: Compute MD5 hash of audio bytes
    # =================================================================
    # Use hashlib.md5() to create a hash of the audio_bytes,
    # then return the hexdigest() string.
    #
    # This is used to detect if we've already processed this audio
    # (prevents duplicate processing on Streamlit reruns).
    #
    # Hint: hashlib.md5(audio_bytes).hexdigest()
    # =================================================================

    # YOUR CODE HERE
    pass  # Replace with: return hashlib.md5(...).hexdigest()


def process_user_input(user_text: str, from_voice: bool = False):
    """Process user input and generate AI response."""
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "human",
        "content": user_text,
        "from_voice": from_voice
    })

    # =================================================================
    # TODO 2: Get AI response from the chatbot
    # =================================================================
    # Call chatbot_response() with:
    # - user_text: the user's message
    # - st.session_state.conversation_id: the current conversation ID
    #
    # The function returns a dict with:
    # - "conversation_id": store this in st.session_state.conversation_id
    # - "response": the AI's text response
    #
    # Hint: response = chatbot_response(user_text, conversation_id)
    # =================================================================
    with st.spinner("Thinking..."):
        # YOUR CODE HERE
        # response = chatbot_response(...)
        # st.session_state.conversation_id = response[...]
        # ai_text = response[...]

        ai_text = "TODO: Implement chatbot response"  # Remove this placeholder

    # =================================================================
    # TODO 3: Generate TTS audio if voice is enabled
    # =================================================================
    # If st.session_state.voice_enabled is True:
    # - Call text_to_speech() with:
    #   - ai_text: the text to convert
    #   - voice: st.session_state.selected_voice
    # - Store the result in audio_data
    #
    # Otherwise set audio_data = None
    #
    # Hint: audio_data = text_to_speech(text, voice=voice)
    # =================================================================
    audio_data = None
    if st.session_state.voice_enabled:
        with st.spinner("Generating voice response..."):
            # YOUR CODE HERE
            # audio_data = text_to_speech(...)
            pass  # Remove this when you add your code

    # =================================================================
    # TODO 4: Add AI response to messages with audio
    # =================================================================
    # Append a new message dict to st.session_state.messages with:
    # - "role": "ai"
    # - "content": ai_text
    # - "audio": audio_data (the TTS audio bytes, or None)
    # - "just_generated": True (used for auto-play)
    # =================================================================

    # YOUR CODE HERE
    # st.session_state.messages.append({...})
    pass  # Remove this when you add your code


# Process voice input
if audio_input is not None:
    # Read audio bytes from the recorded input
    audio_bytes = audio_input.read()

    # Compute hash to check if this audio was already processed
    audio_hash = compute_audio_hash(audio_bytes)

    # Only process if this is new audio (not already processed)
    if audio_hash != st.session_state.processed_audio_hash:
        with st.spinner("Transcribing your voice..."):
            try:
                # =================================================================
                # TODO 5: Transcribe audio using Whisper
                # =================================================================
                # Call transcribe_audio() with:
                # - audio_bytes: the recorded audio data
                # - language: st.session_state.transcription_language
                #   (this helps Whisper be more accurate)
                #
                # Store the result in transcript variable.
                #
                # Hint: transcript = transcribe_audio(audio_bytes, language=...)
                # =================================================================

                # YOUR CODE HERE
                # transcript = transcribe_audio(...)

                transcript = ""  # Remove this placeholder

                if transcript:
                    # Mark this audio as processed BEFORE rerun
                    st.session_state.processed_audio_hash = audio_hash

                    # Increment key to reset audio input widget
                    st.session_state.audio_input_key += 1

                    # Process the transcribed text
                    process_user_input(transcript, from_voice=True)

                    # Rerun to update display
                    st.rerun()
                else:
                    st.warning("Could not transcribe audio. Please try again.")

            except Exception as e:
                st.error(f"Error processing voice: {str(e)}")

# Process text input
if text_input:
    process_user_input(text_input, from_voice=False)
    st.rerun()

# Footer
st.divider()
st.caption("Complete the TODOs to make voice chat work!")
