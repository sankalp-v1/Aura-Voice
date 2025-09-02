import os
import sys
import whisper
import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
import importlib
import warnings

# --- PATH SETUP ---
# This adds the TTS-Engine folder to our Python path, allowing us to import from it
engine_path = os.path.join(os.getcwd(), 'TTS-Engine')
sys.path.append(engine_path)

# --- CONFIGURATION ---
TTS_PROVIDER_TO_USE = "edge_tts"  # Now you can set "tiktok_tts" as a provider
MODEL_SIZE = "base"
SAMPLE_RATE = 16000
CHANNELS = 1

# A mapping of the provider folder name to the class name inside that provider's code
PROVIDER_CLASS_MAP = {
    "edge_tts": "EdgeTTSProvider",
    "speechify": "SpeechifyTTSProvider",
    "tiktok_tts": "TikTokTTSProvider",
    "hearling": "HearlingTTSProvider",
    "vibevoice": "VibeVoiceProvider", # VibeVoice is now a standard provider
}

# --- MODEL LOADING ---
print("🔥 Loading AI models...")
warnings.filterwarnings("ignore", category=UserWarning, module='whisper.transcribing', lineno=114)
whisper_model = whisper.load_model(MODEL_SIZE)
print("✅ AI models loaded!")

# --- MAIN CHAT LOGIC ---
def main():
    print("\n🚀 Aura Voice is ready. Press Enter to start speaking, and Enter again when you're done.")
    while True:
        input("Press Enter to start recording...")
        print("🎤 Recording... Press Enter again to stop.")

        recorded_frames = []

        def audio_callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            recorded_frames.append(indata.copy())

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32', callback=audio_callback):
            input()

        print("✅ Recording finished.")

        if not recorded_frames:
            print("No audio recorded. Try again.")
            continue

        audio_data = np.concatenate(recorded_frames, axis=0)
        audio_filepath = "temp_recording.wav"
        sf.write(audio_filepath, audio_data, SAMPLE_RATE)

        print("🤫 Transcribing audio...")
        result = whisper_model.transcribe(audio_filepath, fp16=False)
        user_text = result["text"].strip()
        print(f"👂 You said: {user_text}")

        if not user_text:
            print("No speech detected. Try again.")
            os.remove(audio_filepath)
            continue

        print("🧠 Accessing the Brain...")
        try:
            token = os.environ.get("GITHUB_TOKEN") or os.environ.get("API_TOKEN")
            if not token:
                print("💀 Error: GITHUB_TOKEN or API_TOKEN not found in environment variables.")
                continue

            endpoint = "https://models.github.ai/inference"
            model_name = "openai/gpt-4o"
            client = OpenAI(base_url=endpoint, api_key=token)

            response = client.chat.completions.create(
                messages=[{"role": "user", "content": user_text}], model=model_name
            )
            ai_response_text = response.choices[0].message.content
            print(f"🤖 AI responded: {ai_response_text}")

            print("🗣️ Accessing the Voice...")
            try:
                # This dynamic import will now find 'vibevoice' inside the TTS-Engine providers folder
                provider_module = importlib.import_module(f"voice.text_to_speech.providers.{TTS_PROVIDER_TO_USE}")
                ProviderClass = getattr(provider_module, PROVIDER_CLASS_MAP[TTS_PROVIDER_TO_USE])
                active_provider = ProviderClass()

                audio_path = active_provider.generate_speech(ai_response_text)
                data, fs = sf.read(audio_path, dtype='float32')
                sd.play(data, fs)
                sd.wait()

            except Exception as e:
                print(f"💀 Voice Error: {e}")

        except Exception as e:
            print(f"💀 Brain Error: {e}")

        os.remove(audio_filepath)
        print("\n-----------------------------------\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting Aura Voice. Peace out! ✌️")
        sys.exit(0)