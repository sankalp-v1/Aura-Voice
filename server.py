import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI

# This creates our web server
app = Flask(__name__)

# --- The main function that runs when a call starts ---
@app.route("/voice", methods=['POST'])
def voice():
    # Start a TwiML response
    resp = VoiceResponse()

    # Use <Gather> to listen for the user's speech
    gather = Gather(input='speech', action='/handle-speech', speech_timeout='auto')
    gather.say("Hello, you've reached Aura Voice. How can I help you today?")
    resp.append(gather)

    # If the user doesn't say anything, hang up
    resp.say("I didn't hear anything. Goodbye.")
    resp.hangup()

    return str(resp)

# --- This function runs AFTER the user speaks ---
@app.route("/handle-speech", methods=['POST'])
def handle_speech():
    # Get the text from what the user said
    user_speech = request.values.get('SpeechResult', '')
    print(f"➡️  User said: '{user_speech}'")

    # --- BRAIN LOGIC ---
    print("🧠 Accessing the GitHub AI Brain...")
    ai_response_text = "I'm sorry, I had a problem thinking of a response."
    try:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("API_TOKEN")
        endpoint = "https://models.github.ai/inference"
        model_name = "openai/gpt-4o"
        client = OpenAI(base_url=endpoint, api_key=token)
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_speech}],
            model=model_name
        )
        ai_response_text = response.choices[0].message.content
        print(f"✅ Brain responded: '{ai_response_text}'")
    except Exception as e:
        print(f"💀 Brain Error: {e}")

    # --- VOICE LOGIC ---
    resp = VoiceResponse()
    # Use Twilio's high-quality voice to speak the AI's response
    resp.say(ai_response_text, voice='alice')
    resp.hangup()

    return str(resp)

if __name__ == "__main__":
    # This runs the server
    app.run(debug=True, host='0.0.0.0', port=5000)