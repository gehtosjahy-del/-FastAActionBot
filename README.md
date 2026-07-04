# FastAActionBot 🚀

A powerful Telegram utility bot for image compression, URL shortening, QR codes, and format conversion.

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🖼️ Image Compression | Reduce image size by up to 90% |
| 🔗 URL Shortening | Shorten long URLs instantly |
| 📱 QR Code Generation | Create QR codes from text |
| 🔄 Format Conversion | Convert JPG↔PNG↔WebP |

## 🚀 Quick Deploy

1. Create bot via @BotFather on Telegram
2. Fork this repository to GitHub
3. Deploy on Railway (github/railway)
4. Add environment variables

## 📦 Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `WEBHOOK_SECRET` | Random secret for webhook |
| `RAILWAY_URL` | Your Railway app URL |

## 💻 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export WEBHOOK_SECRET=your_secret
export RAILWAY_URL=http://localhost:5000

# Run the bot
python app.py
