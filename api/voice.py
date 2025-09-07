from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
import sys
import tempfile
import requests
from openai import OpenAI
import importlib.util

# Add TTS-Engine to path
engine_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TTS-Engine')
sys.path.append(engine_path)

app = Flask(__name__)

# Configuration
TTS_PROVIDER_TO_USE = "edge_tts"
PROVIDER_CLASS_MAP = {
    "edge_tts": "EdgeTTSProvider",
    "speechify": "SpeechifyTTSProvider", 
    "tiktok_tts": "TikTokTTSProvider",
    "hearling": "HearlingTTSProvider",
}

def get_ai_response(user_text):
    """Get AI response from GitHub Models API"""
    try:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("API_TOKEN")
        if not token:
            return "Sorry, I'm having trouble accessing my AI brain right now."
        
        endpoint = "https://models.github.ai/inference"
        model_name = "openai/gpt-4o-mini"
        client = OpenAI(base_url=endpoint, api_key=token)
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are Aura Voice, a helpful AI assistant. Keep responses conversational and under 200 words for voice calls."},
                {"role": "user", "content": user_text}
            ], 
            model=model_name,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "I'm sorry, I'm having trouble processing that right now."

def generate_speech_url(text):
    """Generate speech using TTS-Engine and return a public URL"""
    try:
        # Dynamic import of TTS provider
        provider_module = importlib.import_module(f"voice.text_to_speech.providers.{TTS_PROVIDER_TO_USE}")
        ProviderClass = getattr(provider_module, PROVIDER_CLASS_MAP[TTS_PROVIDER_TO_USE])
        active_provider = ProviderClass()
        
        # Generate speech
        audio_path = active_provider.generate_speech(text)
        
        # For Vercel deployment, we'd need to upload to a CDN or return the audio directly
        # For now, let's return None and use Twilio's built-in TTS
        return None
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

@app.route('/voice', methods=['POST'])
def handle_voice_call():
    """Handle incoming voice calls from Twilio"""
    response = VoiceResponse()
    
    # Check if this is a recording callback
    if 'RecordingUrl' in request.form:
        recording_url = request.form['RecordingUrl']
        
        # Download and process the recording
        try:
            # Download the recording
            audio_response = requests.get(recording_url)
            
            # For now, we'll use a simple text response since we don't have
            # speech-to-text set up for web deployment yet
            user_text = "Hello, I called your Aura Voice system"
            
            # Get AI response
            ai_response = get_ai_response(user_text)
            
            # Try to generate speech, fallback to Twilio TTS
            speech_url = generate_speech_url(ai_response)
            
            if speech_url:
                response.play(speech_url)
            else:
                # Use Twilio's built-in TTS as fallback
                response.say(ai_response, voice='alice')
            
            # Allow for follow-up
            response.redirect('/voice')
            
        except Exception as e:
            print(f"Processing error: {e}")
            response.say("I'm sorry, I had trouble processing your message.", voice='alice')
            response.hangup()
    
    else:
        # Initial call - greet and start recording
        response.say("Hello! You've reached Aura Voice, your AI conversation partner. Please speak your message after the beep.", voice='alice')
        response.record(
            max_length=30,
            timeout=5,
            transcribe=False,
            action='/voice',
            method='POST'
        )
    
    return Response(str(response), mimetype='text/xml')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Aura Voice API"}

@app.route('/', methods=['GET'])
def index():
    """Index route"""
    return {
        "message": "Welcome to Aura Voice API",
        "endpoints": {
            "/voice": "Twilio webhook for voice calls",
            "/health": "Health check"
        }
    }

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)