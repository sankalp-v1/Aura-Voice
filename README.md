<p align="center">
  <h1>Aura Voice ✨ - Your AI Co-Pilot for Conversations</h1>
  <a href="https://freeimage.host/i/K2auZAu">
    <img src="https://iili.io/K2auZAu.png" alt="Aura Voice Logo" width="500">
  </a>
</p>

---
## What's the Hype? 🔥

Tired of clunky chatbots and generic interactions? **Aura Voice** isn't just an AI; it's your brand's ultimate conversational co-pilot! 🚀 This project brings an AI-powered agent to life, capable of handling real-time voice calls with a personality that's all yours. Forget old-school, this is next-level customer engagement.

---
## Key Features 🔥

* 📞 **Real Talk, Real Time:** Connects to actual phone lines via Twilio for seamless, live conversations. No more "press 1 for..." BS.
* 🧠 **Brain on Fire:** Powered by state-of-the-art Large Language Models like GPT-4o via the GitHub Models API. It actually understands, it doesn't just guess.
* 🗣️ **Custom Voice Engine:** Integrated with our own `TTS-Engine`, allowing you to switch between different high-quality voices (Deepgram, TikTok, and more) to perfectly match your brand's aesthetic.
* ☁️ **Built for the Cloud:** Optimized for smooth sailing in cloud dev environments like GitHub Codespaces. Easy setup, maximum impact.

---
## Live Demo Action 🎬

<p align="center">
  *Your lit live demo GIF will drop here! Show off that real-time magic! Call this number +1 (831) 618-0462 to try out Aura-Voice.*
</p>

---
## Under the Hood: The Tech Stack 🛠️

It's simple, powerful, and ready to scale:

`Call Incoming 📞` ➡️ `Twilio (Ears)` ➡️ `Your Python Server` ➡️ `GitHub AI (Brain)` ➡️ `Your Python Server` ➡️ `TTS-Engine (Voice)` ➡️ `Twilio (Mouth)` ➡️ `User Gets Their Mind Blown 🤯`

---
## 🚀 Get Started – It's Easier Than You Think!

Ready to launch your own AI co-pilot? Follow these steps:

### 1. Clone the Repo (and all its cool bits)
Grab this project, including our custom `TTS-Engine` submodule:
```sh
git clone --recurse-submodules [YOUR_REPO_URL_HERE]
cd Aura-Voice
````

### 2\. Install the Essentials

First, let's get those system-level heroes and Python power-ups:

```sh
sudo apt-get update && sudo apt-get install -y portaudio19-dev ffmpeg
```

Then, all the Python packages you'll need:

```sh
pip install -r TTS-Engine/requirements.txt
pip install twilio flask openai
```

### 3\. Secure Your Keys 🔑

Keep your secrets safe\! Store these in your GitHub Codespaces Secrets (the 🔒 icon):

  * `GITHUB_TOKEN`: Your Personal Access Token for the GitHub AI Brain.
  * `TWILIO_ACCOUNT_SID`: Your Account SID from your Twilio dashboard.
  * `TWILIO_AUTH_TOKEN`: Your Auth Token from your Twilio dashboard.

### 4\. Plug into Twilio 🌐

1.  **Get a Phone Number:** Snag a trial phone number from your Twilio dashboard.
2.  **Fire Up the Server:** Get your Aura-Voice server running locally: `python server.py`.
3.  **Grab the Public URL:** In your Codespaces **PORTS** tab, find and copy the public URL for **port 5000**.
4.  **Configure the Webhook:** On your Twilio number's config page (under "Voice & Fax"), set **"A CALL COMES IN"** to `Webhook`. Paste your public URL (ending with `/voice`), and set the method to `HTTP POST`.

### 5\. Dial and Vibe with Your AI\! 📞👾

Call your shiny new Twilio number from your real phone\! Your `server.py` script will answer, and you'll be chatting with your very own AI co-pilot. Experience the future\!

---
## Setup (recommended)

There's a helper script to create a reproducible environment using pyenv + Python 3.11 and install all dependencies (including torch).

Run from the repo root (zsh):

```bash
./scripts/setup_env.sh
source .venv/bin/activate
```

If you prefer not to use pyenv, create a Python 3.11 venv and run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Troubleshooting notes:
- If installation fails on `torch`, use the appropriate wheel from https://pytorch.org/get-started/locally/ (select macOS/CPU or macOS/MPS).
- If pip refuses to install system-wide packages, you're on an "externally-managed" Python (Homebrew). Use the script above to create and activate a venv.
- If `whisper` fails to build from source, try installing `torch` first as per the PyTorch instructions.

-----

## Wanna Level Up? Contribute\! 🚀

Got fresh ideas? Spotted a glitch in the matrix? Pull requests are always welcome\! Let's build the future together.

-----

## Big Ups\! 🙏

Huge props to the brilliant minds behind [Jarvis 4.0](https://github.com/SreejanPersonal/Jarvis-4.0)\! Their incredible `TTS-Engine` code is the beating heart of Aura Voice's custom sound. You guys rock\!
