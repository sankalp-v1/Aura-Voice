# 🚀 Vercel Deployment Guide for Aura Voice

This guide will help you deploy Aura Voice to Vercel for production use with Twilio phone integration.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Twilio Account**: Get your Account SID and Auth Token from [twilio.com](https://twilio.com)
3. **GitHub Token**: Get a Personal Access Token for GitHub Models API

## 🔧 Environment Variables

Set these environment variables in your Vercel project settings:

```bash
GITHUB_TOKEN=your_github_personal_access_token
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

## 🚀 Quick Deploy

### Option 1: Deploy from GitHub

1. Push this repository to GitHub
2. Connect your GitHub repo to Vercel
3. Vercel will automatically detect the Flask app and deploy it
4. Set your environment variables in Vercel dashboard
5. Your app will be available at `https://your-project.vercel.app`

### Option 2: Deploy with Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project directory
vercel

# Set environment variables
vercel env add GITHUB_TOKEN
vercel env add TWILIO_ACCOUNT_SID
vercel env add TWILIO_AUTH_TOKEN

# Redeploy with environment variables
vercel --prod
```

## 📞 Twilio Configuration

1. **Get a Phone Number**: Purchase or get a trial number from Twilio
2. **Configure Webhook**: In your Twilio console:
   - Go to Phone Numbers → Manage → Active numbers
   - Click on your phone number
   - In the "Voice & Fax" section:
     - Set "A call comes in" to **Webhook**
     - URL: `https://your-project.vercel.app/voice`
     - Method: **HTTP POST**
   - Save the configuration

## 🧪 Testing Your Deployment

### Test the API endpoints:
- **Health check**: `GET https://your-project.vercel.app/health`
- **Index**: `GET https://your-project.vercel.app/`
- **Voice webhook**: `POST https://your-project.vercel.app/voice` (used by Twilio)

### Test the phone integration:
1. Call your Twilio phone number
2. You should hear the greeting: "Hello! You've reached Aura Voice..."
3. Speak your message after the beep
4. The AI will respond using Twilio's text-to-speech

## 📁 Project Structure

```
Aura-Voice/
├── api/
│   ├── __init__.py
│   └── voice.py          # Main Flask application
├── TTS-Engine/           # Voice synthesis engine (submodule)
├── desktop_app.py        # Original desktop application
├── index.py              # Vercel entry point
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## 🔧 Advanced Configuration

### Custom TTS Integration

The current deployment uses Twilio's built-in TTS as a fallback. To enable custom voice synthesis:

1. Implement audio file hosting (e.g., AWS S3, Cloudinary)
2. Modify `generate_speech_url()` function in `api/voice.py`
3. Return public URLs for generated audio files

### Speech-to-Text Integration

To add advanced speech recognition:

1. Integrate with services like Google Speech-to-Text or Azure Speech
2. Process the `RecordingUrl` from Twilio webhooks
3. Update the voice handler to transcribe audio before sending to AI

## 🐛 Troubleshooting

### Common Issues:

1. **Environment Variables Not Set**: Check Vercel dashboard
2. **Twilio Webhook Errors**: Verify the webhook URL in Twilio console
3. **Import Errors**: Ensure all dependencies are in `requirements.txt`
4. **Timeout Issues**: Check Vercel function timeout settings

### Debugging:

- Check Vercel function logs in the dashboard
- Test endpoints using curl or Postman
- Verify Twilio webhook delivery in Twilio console

## 📈 Monitoring & Scaling

- Monitor function execution time in Vercel dashboard
- Set up alerts for errors or high usage
- Consider upgrading Vercel plan for higher limits
- Monitor Twilio usage and costs

## 🎉 Success!

Once deployed, your Aura Voice AI will be available 24/7 for phone conversations powered by GitHub's AI models!

Call your Twilio number and start chatting with your AI assistant! 🤖📞