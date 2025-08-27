import streamlit as st
import os
import sys
import asyncio
import traceback
import numpy as np
from openai import OpenAI
from pydub import AudioSegment
import av
import vosk
import whisper
import json
import importlib
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# --- PATH SETUP ---
# This adds the TTS-Engine folder to our Python path
engine_path = os.path.join(os.getcwd(), 'TTS-Engine')
sys.path.append(engine_path)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Aura Voice Demo", page_icon="🗣️")
st.title("🗣️ Aura Voice Live Demo")

# --- CONFIGURATION ---
STT_PROVIDER_TO_USE = "whisper"  # Change this to "vosk" or "whisper"
TTS_PROVIDER_TO_USE = "tiktok_tts" # Change the default voice here

# A mapping of the provider filename to the class name inside that file
PROVIDER_CLASS_MAP = {
    "edge_tts": "EdgeTTSProvider",
    "speechify": "SpeechifyTTSProvider",
    "tiktok_tts": "TikTokTTSProvider",
    "hearling": "HearlingTTSProvider",
}

# --- MODEL LOADING (Done only once) ---
@st.cache_resource
def load_models():
    vosk_model = None
    if os.path.exists(os.path.join(engine_path, "voice/voices/assets/models/vosk/vosk-model-small-en-us-0.15")):
        vosk_model = vosk.Model(os.path.join(engine_path, "voice/voices/assets/models/vosk/vosk-model-small-en-us-0.15"))
    
    whisper_model = whisper.load_model("base")
    return vosk_model, whisper_model

with st.spinner("Loading AI models... (This can take a moment on first run)"):
    vosk_model, whisper_model = load_models()
st.success("AI models loaded!")

# --- SESSION STATE ---
if "text" not in st.session_state:
    st.session_state.text = "Click 'Start' to speak, then 'Stop' when you're done."

# --- AUDIO PROCESSING CLASS ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = np.array([], dtype=np.int16)

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio_data = frame.to_ndarray(format='s16')
        self.audio_buffer = np.append(self.audio_buffer, audio_data)
        return frame

    def on_ended(self):
        st.session_state.text = "🎤 Processing audio..."
        
        if self.audio_buffer.size == 0:
            st.session_state.text = "No audio received. Please try again."
            return

        if STT_PROVIDER_TO_USE == "whisper" and whisper_model:
            result = whisper_model.transcribe(self.audio_buffer, fp16=False)
            st.session_state.text = result["text"]
        elif STT_PROVIDER_TO_USE == "vosk" and vosk_model:
            rec = vosk.KaldiRecognizer(vosk_model, 16000)
            rec.AcceptWaveform(self.audio_buffer.tobytes())
            result = json.loads(rec.FinalResult())
            st.session_state.text = result["text"]
        else:
            st.session_state.text = f"Error: {STT_PROVIDER_TO_USE} model not loaded."
        
        self.audio_buffer = np.array([], dtype=np.int16) # Clear buffer

# --- STREAMLIT UI ---
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

st.write("---")

if st.session_state.text and "Click 'Start'" not in st.session_state.text and "Processing" not in st.session_state.text:
    st.subheader("👂 You Said:")
    st.write(st.session_state.text)
    
    with st.spinner("🧠 Accessing the Brain..."):
        try:
            token = os.environ.get("GITHUB_TOKEN") or os.environ.get("API_TOKEN")
            endpoint = "https://models.github.ai/inference"
            model_name = "openai/gpt-4o"
            client = OpenAI(base_url=endpoint, api_key=token)
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": st.session_state.text}], model=model_name
            )
            ai_response_text = response.choices[0].message.content

            st.subheader("🤖 AI Responded:")
            st.write(ai_response_text)
            
            with st.spinner("🗣️ Accessing the Voice..."):
                try:
                    # Dynamically import the correct provider module
                    provider_module = importlib.import_module(f"voice.text_to_speech.providers.{TTS_PROVIDER_TO_USE}")
                    ProviderClass = getattr(provider_module, PROVIDER_CLASS_MAP[TTS_PROVIDER_TO_USE])
                    active_provider = ProviderClass()
                    
                    audio_path = active_provider.generate_speech(ai_response_text)
                    st.audio(audio_path, autoplay=True)
                except Exception as e:
                    st.error(f"Voice Error: {e}")
        except Exception as e:
            st.error(f"Brain Error: {e}")

    # Clear state for next turn
    st.session_state.text = "Click 'Start' to speak, then 'Stop' when you're done."

else:
    st.info(st.session_state.text)