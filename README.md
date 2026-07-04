# FastAActionBot 🚀

A powerful Telegram utility bot with multiple features.

## Features

- 🖼️ Image Compression
- 🔗 URL Shortening  
- 📱 QR Code Generation
- 🔄 Image Format Conversion (JPG/PNG/WebP)

## Quick Deploy to Railway

1. Fork this repository to GitHub
2. Create bot via @BotFather on Telegram
3. Deploy on Railway from GitHub
4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `WEBHOOK_SECRET`
   - `RAILWAY_URL`

## Environment Variables

| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | Bot token from @BotFather |
| WEBHOOK_SECRET | Secret key for webhook |
| RAILWAY_URL | Your Railway app URL |

## Local Development

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=your_token
export WEBHOOK_SECRET=your_secret
export RAILWAY_URL=http://localhost:5000
python app.py
