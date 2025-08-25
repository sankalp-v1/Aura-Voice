import sys
import os
import asyncio
import traceback
import importlib
from openai import OpenAI

# This adds the TTS-Engine folder to our Python path so we can import from it
engine_path = os.path.join(os.getcwd(), 'TTS-Engine')
sys.path.append(engine_path)

async def main():
    print("🔥 Aura Voice Initializing...")
    
    # --- CONFIGURATION ---
    PROMPT = "In one short sentence, what is the weather like in Pune right now?"
    
    # A mapping of the provider filename to the class name inside that file
    PROVIDER_CLASS_MAP = {
        "deepgram": "DeepgramTTSProvider",
        "edge_tts": "EdgeTTSProvider",
        "speechify": "SpeechifyTTSProvider",
        "tiktok_tts": "TikTokTTSProvider",
        "hurling": "HurlingTTSProvider",
    }
    
    # Pick a provider from the keys in the map above
    PROVIDER_TO_USE = "deepgram"
    
    OUTPUT_FOLDER = "output"
    # ---------------------

    try:
        # --- PHASE 1: THE BRAIN (GitHub AI Edition) ---
        print("🧠 Accessing the GitHub AI Brain (GPT-4o)...")
        
        token = os.environ.get("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")
        endpoint = "https://models.github.ai/inference"
        model_name = "openai/gpt-4o"

        client = OpenAI(base_url=endpoint, api_key=token)

        print(f"➡️  Asking the brain: '{PROMPT}'")
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": PROMPT}],
            model=model_name
        )
        
        ai_response_text = response.choices[0].message.content
        print(f"✅ Brain responded: '{ai_response_text}'")

        # --- PHASE 2: THE VOICE ---
        print("\n🗣️ Accessing the TTS-Engine Voice...")
        
        # Dynamically import the correct provider module
        provider_module = importlib.import_module(f"voice.text_to_speech.providers.{PROVIDER_TO_USE}")
        ProviderClass = getattr(provider_module, PROVIDER_CLASS_MAP[PROVIDER_TO_USE])
        active_provider = ProviderClass()
        
        print(f"🎤 Using voice provider: {PROVIDER_TO_USE}")
        
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        output_filename = "final_audio.mp3"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        audio_path = active_provider.generate_speech(ai_response_text, output_path=output_path)
        
        print(f"\n✅✅✅ SUCCESS! Full AI response saved to: {audio_path}")
        print(f"You should find the audio file in the '{OUTPUT_FOLDER}' folder.")

    except Exception as e:
        print(f"\n💀💀💀 An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())