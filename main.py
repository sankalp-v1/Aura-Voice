import sys
import os
import asyncio
import traceback
import importlib
from openai import OpenAI

# This adds the TTS-Engine folder to our Python path so it can find the 'voice' module
engine_path = os.path.join(os.getcwd(), 'TTS-Engine')
sys.path.append(engine_path)

async def main():
    print("🔥 Aura Voice Initializing...")
    
    # --- CONFIGURATION ---
    PROMPT = "In one short sentence, what is the weather like in Pune right now?"
    
    # A mapping of the provider filename to the class name inside that file
    PROVIDER_CLASS_MAP = {
        "edge_tts": "EdgeTTSProvider",
        "speechify": "SpeechifyTTSProvider",
        "tiktok_tts": "TikTokTTSProvider",
        "hearling": "HearlingTTSProvider",
    }
    
    # Pick a provider from the keys in the map above
    PROVIDER_TO_USE = "edge_tts" # Changed default to tiktok_tts
    
    OUTPUT_FOLDER = "output"
    # ---------------------

    try:
        # --- PHASE 1: THE BRAIN ---
        print("🧠 Accessing the GitHub AI Brain (GPT-4o)...")
        
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("API_TOKEN")
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
        
        provider_module = importlib.import_module(f"voice.text_to_speech.providers.{PROVIDER_TO_USE}")
        ProviderClass = getattr(provider_module, PROVIDER_CLASS_MAP[PROVIDER_TO_USE])
        active_provider = ProviderClass()
        
        print(f"🎤 Using voice provider: {PROVIDER_TO_USE}")

        available_voices = active_provider.list_available_voices()
        chosen_voice = None

        if available_voices:
            voice_list = list(available_voices.keys()) if isinstance(available_voices, dict) else available_voices
            
            print("\nAvailable Voices:")
            for i, voice in enumerate(voice_list):
                print(f"  {i + 1}: {voice}")
            
            while True:
                try:
                    choice = int(input("\n➡️  Enter the number of the voice you want to use: "))
                    if 1 <= choice <= len(voice_list):
                        chosen_voice = voice_list[choice - 1]
                        print(f"👍 You selected: {chosen_voice}")
                        break
                    else:
                        print("💀 Invalid number, please try again.")
                except ValueError:
                    print("💀 Please enter a valid number.")

        output_filename = f"{PROVIDER_TO_USE}_{chosen_voice or 'default'}_final_audio.mp3"
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        audio_path = active_provider.generate_speech(ai_response_text, voice=chosen_voice, output_path=output_path)
        
        print(f"\n✅✅✅ SUCCESS! Full AI response saved to: {audio_path}")

    except Exception as e:
        print(f"\n💀💀💀 An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())