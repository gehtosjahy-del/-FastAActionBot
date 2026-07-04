# FastAActionBot 🚀

A powerful Telegram utility bot with multiple features.

## Features

- 🖼️ **Image Compression** - Reduce image size by up to 90%
- 🔗 **URL Shortening** - Shorten long URLs instantly
- 📱 **QR Code Generation** - Create QR codes from text
- 🔄 **Format Conversion** - Convert JPG↔PNG↔WebP

## Commands

- `/start` - Show main menu
- `/help` - Show help
- `/compress` - Compress an image
- `/shorten` - Shorten a URL
- `/qr [text]` - Generate QR code
- `/convert` - Convert image format

## Environment Variables

| Variable | Description |
|----------|-------------|
| TELEGRAM_BOT_TOKEN | Bot token from @BotFather |
| WEBHOOK_SECRET | Secret key for webhook |
| RAILWAY_URL | Your Railway app URL |

## Deployment on Railway

1. Create bot via @BotFather
2. Push this code to GitHub
3. Deploy on Railway from GitHub
4. Add environment variables
5. Test with /start command

## Local Development

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=your_token
export WEBHOOK_SECRET=your_secret
export RAILWAY_URL=http://localhost:5000
python app.py
