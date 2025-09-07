import os
import sys
import pvleopard
import pvporcupine  # <-- ADD: Import Porcupine
import struct      # <-- ADD: Needed for audio processing
import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
import importlib

# --- CONFIGURATION ---
TTS_PROVIDER_TO_USE = "edge_tts"
PICOVOICE_ACCESS_KEY = "NCfIRXMaIPkBpxb+x+VLvd0p8ppkxIoiFC7YoTNKHJDTxP4C/uSOaQ==" # <-- Your Picovoice key
# --- ADD: Wake Word Configuration ---
WAKE_WORD = "jarvis" # Options: computer, jarvis, hey siri, etc.
# --- END ADD ---
SAMPLE_RATE = 16000
CHANNELS = 1

# --- PATH SETUP ---
engine_path = os.path.join(os.getcwd(), 'TTS-Engine')
sys.path.append(engine_path)

PROVIDER_CLASS_MAP = {
    "edge_tts": "EdgeTTSProvider",
    "speechify": "SpeechifyTTSProvider",
    "tiktok_tts": "TikTokTTSProvider",
    "hearling": "HearlingTTSProvider",
}

# --- MODEL LOADING ---
print("🔥 Loading AI models...")
try:
    leopard = pvleopard.create(access_key=PICOVOICE_ACCESS_KEY)
    # --- ADD: Load Porcupine Wake Word Engine ---
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keywords=[WAKE_WORD]
    )
    # --- END ADD ---
    print("✅ Picovoice Leopard & Porcupine loaded!")
except Exception as e:
    print(f"💀 Error loading Picovoice: {e}")
    sys.exit(1)


def main():
    # --- CHANGE: Main logic is now a continuous listen/record/respond loop ---
    
    # --- WAKE WORD LISTENING LOOP ---
    print(f"\n🚀 Aura Voice is listening for the wake word '{WAKE_WORD}'...")
    
    audio_stream = sd.InputStream(
        samplerate=porcupine.sample_rate,
        channels=1,
        dtype='int16',
        blocksize=porcupine.frame_length
    )
    audio_stream.start()

    while True:
        pcm = audio_stream.read(porcupine.frame_length)[0]
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print(f"🎤 Wake word '{WAKE_WORD}' detected!")
            audio_stream.stop() # Stop listening for wake word

            # --- RECORDING AFTER WAKE WORD ---
            print("🔴 Recording... Speak your command.")
            recorded_frames = []

            def audio_callback(indata, frames, time, status):
                recorded_frames.append(indata.copy())

            # Start a new stream for recording the actual command
            record_stream = sd.InputStream(
                samplerate=SAMPLE_RATE, 
                channels=CHANNELS, 
                dtype='float32', 
                callback=audio_callback
            )
            
            # This part is still a bit manual. A better version would have automatic silence detection.
            # For now, we'll use a manual stop after a few seconds of recording.
            with record_stream:
                print("Listening for your command... (Press Enter to stop for now)")
                input() # We'll replace this with silence detection later

            print("✅ Recording finished.")
            
            if not recorded_frames:
                print("No audio recorded.")
                audio_stream.start() # Restart wake word listening
                continue

            # --- PROCESSING AND RESPONDING (Same as before) ---
            audio_data = np.concatenate(recorded_frames, axis=0)
            audio_filepath = "temp_recording.wav"
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            sf.write(audio_filepath, audio_data_int16, SAMPLE_RATE)

            print("🤫 Transcribing audio...")
            try:
                transcript, words = leopard.process_file(audio_filepath)
                user_text = transcript.strip()
                print(f"👂 You said: {user_text}")
            except Exception as e:
                print(f"💀 Picovoice Error: {e}")
                os.remove(audio_filepath)
                audio_stream.start()
                continue
            
            if not user_text:
                print("No speech detected.")
                os.remove(audio_filepath)
                audio_stream.start()
                continue

            print("🧠 Accessing the Brain...")
            try:
                token = os.environ.get("GITHUB_TOKEN") or os.environ.get("API_TOKEN")
                if not token:
                    print("💀 Error: GITHUB_TOKEN or API_TOKEN not found in environment variables.")
                    audio_stream.start()
                    continue

                endpoint = "https://models.github.ai/inference"
                model_name = "openai/gpt-5-nano"
                client = OpenAI(base_url=endpoint, api_key=token)

                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_text}], model=model_name
                )
                ai_response_text = response.choices[0].message.content
                print(f"🤖 AI responded: {ai_response_text}")

                print("🗣️ Accessing the Voice...")
                try:
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
            print("\n-----------------------------------")
            print(f"👂 Listening for '{WAKE_WORD}' again...")
            audio_stream.start() # Restart listening for the wake word

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting Aura Voice. Peace out! ✌️")