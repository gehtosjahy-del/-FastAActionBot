import os
import sys
import logging
import tempfile
import hashlib
import base64
import urllib.parse
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import requests
from PIL import Image

# ============================================
# LOGGING SETUP (do this first)
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "default_secret_here")
RAILWAY_URL = os.environ.get("RAILWAY_URL", "https://your-app.up.railway.app")
PORT = int(os.environ.get("PORT", 5000))

# Log configuration status
logger.info("=" * 50)
logger.info("🚀 FastAActionBot Starting...")
logger.info(f"🤖 Bot enabled: {bool(TOKEN)}")
logger.info(f"🔑 Token configured: {bool(TOKEN)}")
logger.info(f"🌐 PORT: {PORT}")
logger.info("=" * 50)

# ============================================
# FLASK APP (MUST BE GLOBAL FOR GUNICORN)
# ============================================

flask_app = Flask(__name__)

# ============================================
# TELEGRAM BOT (initialize if enabled)
# ============================================

bot_app = None
BOT_ENABLED = False

if TOKEN:
    try:
        bot_app = Application.builder().token(TOKEN).build()
        BOT_ENABLED = True
        logger.info("✅ Telegram bot initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        bot_app = None
        BOT_ENABLED = False
else:
    logger.warning("⚠️ TELEGRAM_BOT_TOKEN not set. Bot will not respond to messages.")
    logger.info("💡 Add TELEGRAM_BOT_TOKEN environment variable to enable bot features")

# ============================================
# UTILITY FUNCTIONS
# ============================================

async def create_short_url(long_url: str) -> str:
    """Create a shortened URL using TinyURL API with fallback"""
    try:
        response = requests.get(
            f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}",
            timeout=5
        )
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
    except Exception as e:
        logger.warning(f"TinyURL API failed: {e}")
    
    # Fallback: Generate custom short code
    hash_bytes = hashlib.md5(long_url.encode()).digest()
    short_code = base64.urlsafe_b64encode(hash_bytes[:6]).decode().rstrip("=")
    return f"{RAILWAY_URL}/s/{short_code}"

def cleanup_file(file_path: str):
    """Safely delete temporary file"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup {file_path}: {e}")

# ============================================
# TELEGRAM COMMAND HANDLERS
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with all options"""
    keyboard = [
        [InlineKeyboardButton("🖼️ Compress Image", callback_data="compress")],
        [InlineKeyboardButton("🔗 Shorten URL", callback_data="shorten")],
        [InlineKeyboardButton("📱 Generate QR Code", callback_data="qr")],
        [InlineKeyboardButton("🔄 Convert Image Format", callback_data="convert")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚡ **Welcome to FastAActionBot!** ⚡\n\n"
        "Your all-in-one utility bot for:\n"
        "• 🖼️ Compress images (save space)\n"
        "• 🔗 Shorten long URLs\n"
        "• 📱 Generate QR codes from text/URLs\n"
        "• 🔄 Convert image formats (JPG↔PNG↔WebP)\n\n"
        "Send me a file or choose an option below:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    await update.message.reply_text(
        "📖 **How to use FastAActionBot:**\n\n"
        "**🖼️ Image Compression:**\n"
        "• Send any image and I'll compress it\n"
        "• Use /compress to get started\n\n"
        "**🔗 URL Shortening:**\n"
        "• Send any URL (http:// or https://)\n"
        "• Use /shorten to get started\n\n"
        "**📱 QR Code Generation:**\n"
        "• Send /qr followed by text or URL\n"
        "• Example: `/qr https://example.com`\n\n"
        "**🔄 Image Format Conversion:**\n"
        "• Send /convert with your image\n"
        "• Choose the format you want\n\n"
        "Use /start to see all options",
        parse_mode='Markdown'
    )

async def compress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guide user to send an image for compression"""
    await update.message.reply_text(
        "📤 **Send me an image** and I'll compress it!\n\n"
        "I support JPG, PNG, and WebP formats.\n"
        "I'll reduce the file size while keeping quality good.",
        parse_mode='Markdown'
    )

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guide user to send a URL for shortening"""
    await update.message.reply_text(
        "🔗 **Send me a URL** to shorten it!\n\n"
        "Example: `https://very-long-url.example.com/some/path`\n\n"
        "Just paste any link and I'll make it shorter.",
        parse_mode='Markdown'
    )

async def qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR code from text or URL"""
    try:
        text = update.message.text.replace('/qr', '').strip()
        
        if not text:
            await update.message.reply_text(
                "❌ Please provide text or a URL for the QR code.\n\n"
                "Example: `/qr https://example.com`\n"
                "Or: `/qr Hello World`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📱 Generating QR code...")
        
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(text)}"
        
        await update.message.reply_photo(
            photo=qr_url,
            caption=f"✅ **QR Code Generated!**\n\n📝 Content: {text[:50]}..."
        )
        
    except Exception as e:
        logger.error(f"QR generation error: {e}")
        await update.message.reply_text("❌ Failed to generate QR code. Please try again.")

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guide user for image format conversion"""
    await update.message.reply_text(
        "🔄 **Send me an image** to convert its format!\n\n"
        "I can convert between JPG, PNG, and WebP formats.\n"
        "After sending, you can choose the output format.",
        parse_mode='Markdown'
    )

# ============================================
# MESSAGE HANDLERS
# ============================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    msg = update.message
    
    if not msg:
        return
    
    # Handle URL shortening
    if msg.text and ("http://" in msg.text or "https://" in msg.text):
        await handle_url_shortening(update, context)
        return
    
    # Handle images
    if msg.photo or (msg.document and msg.document.mime_type and msg.document.mime_type.startswith('image/')):
        await handle_image_processing(update, context)
        return
    
    # Default response
    if msg.text:
        await msg.reply_text(
            "🤔 I'm not sure what to do with that.\n\n"
            "• Send me an image to compress/convert\n"
            "• Send me a URL to shorten\n"
            "• Use /start for all options\n"
            "• Use /help for guidance"
        )

async def handle_url_shortening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process URL shortening"""
    msg = update.message
    text = msg.text
    
    await msg.reply_text("🔗 Shortening your URL...")
    
    try:
        words = text.split()
        url = next((word for word in words if word.startswith(("http://", "https://"))), None)
        
        if url:
            short_url = await create_short_url(url)
            
            await msg.reply_text(
                f"✅ **URL Shortened!**\n\n"
                f"🔗 **Shortened:** {short_url}\n"
                f"📎 **Original:** {url[:60]}...\n\n"
                f"💡 Click the link above to visit the page.",
                parse_mode='Markdown'
            )
        else:
            await msg.reply_text("❌ No valid URL found in your message.")
            
    except Exception as e:
        logger.error(f"URL shortening error: {e}")
        await msg.reply_text("❌ Failed to shorten URL. Please try again.")

async def handle_image_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process images for compression or conversion"""
    msg = update.message
    
    try:
        await msg.reply_text("🔄 Uploading your image...")
        
        # Get file
        if msg.photo:
            file_id = msg.photo[-1].file_id
        else:
            file_id = msg.document.file_id
        
        file = await context.bot.get_file(file_id)
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        
        # Download image
        await file.download_to_drive(temp_input.name)
        context.user_data['image_path'] = temp_input.name
        
        # Create keyboard for options
        keyboard = [
            [InlineKeyboardButton("📸 JPG", callback_data="format_jpg")],
            [InlineKeyboardButton("🖼️ PNG", callback_data="format_png")],
            [InlineKeyboardButton("🌐 WebP", callback_data="format_webp")],
            [InlineKeyboardButton("⬇️ Compress Only", callback_data="compress_only")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await msg.reply_text(
            "✅ Image uploaded! Choose what you want to do:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        await msg.reply_text("❌ Failed to process image. Please try again.")

# ============================================
# CALLBACK HANDLERS
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "compress":
        await query.edit_message_text(
            "📤 **Send me an image** and I'll compress it!\n\n"
            "I'll reduce the file size while keeping it looking good!",
            parse_mode='Markdown'
        )
    
    elif query.data == "shorten":
        await query.edit_message_text(
            "🔗 **Send me a URL** and I'll shorten it!\n\n"
            "Just paste or type a link and I'll make it shorter!",
            parse_mode='Markdown'
        )
    
    elif query.data == "qr":
        await query.edit_message_text(
            "📱 **Send me text or a URL** to generate a QR code!\n\n"
            "Use: `/qr https://example.com`\n"
            "Or: `/qr Hello World`",
            parse_mode='Markdown'
        )
    
    elif query.data == "convert":
        await query.edit_message_text(
            "🔄 **Send me an image** to convert its format!\n\n"
            "I can convert between JPG, PNG, and WebP formats.",
            parse_mode='Markdown'
        )
    
    elif query.data.startswith("format_"):
        output_format = query.data.replace("format_", "")
        await process_image_conversion(query, context, output_format)
    
    elif query.data == "compress_only":
        await process_image_compression(query, context)

# ============================================
# IMAGE PROCESSING FUNCTIONS
# ============================================

async def process_image_conversion(query, context, output_format):
    """Convert image to specified format"""
    image_path = context.user_data.get('image_path')
    
    if not image_path or not os.path.exists(image_path):
        await query.edit_message_text("❌ No image found. Please send a new image.")
        return
    
    try:
        await query.edit_message_text(f"🔄 Converting to {output_format.upper()}...")
        
        with Image.open(image_path) as img:
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format.lower()}")
            
            # Handle format-specific settings
            if output_format.upper() == "JPG":
                img = img.convert("RGB")
                img.save(temp_output.name, "JPEG", quality=85)
            elif output_format.upper() == "PNG":
                img.save(temp_output.name, "PNG")
            elif output_format.upper() == "WEBP":
                img.save(temp_output.name, "WEBP", quality=85)
            
            file_size = os.path.getsize(temp_output.name) / (1024 * 1024)
            
            with open(temp_output.name, "rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"converted.{output_format.lower()}",
                    caption=f"✅ **Image converted to {output_format.upper()}!**\n\n"
                            f"📦 Size: {file_size:.2f} MB\n"
                            f"🔄 Format: {output_format.upper()}"
                )
            
            cleanup_file(temp_output.name)
            
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        await query.edit_message_text("❌ Failed to convert image. Please try again.")
    finally:
        cleanup_file(image_path)
        context.user_data.pop('image_path', None)

async def process_image_compression(query, context):
    """Compress image with reduced quality"""
    image_path = context.user_data.get('image_path')
    
    if not image_path or not os.path.exists(image_path):
        await query.edit_message_text("❌ No image found. Please send a new image.")
        return
    
    try:
        await query.edit_message_text("🔄 Compressing image...")
        
        with Image.open(image_path) as img:
            original_size = os.path.getsize(image_path) / (1024 * 1024)
            
            # Resize if too large
            max_size = 1200
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            img.save(temp_output.name, "JPEG", quality=50, optimize=True)
            
            compressed_size = os.path.getsize(temp_output.name) / (1024 * 1024)
            saved = original_size - compressed_size
            reduction = (saved / original_size * 100) if original_size > 0 else 0
            
            with open(temp_output.name, "rb") as f:
                await query.message.reply_photo(
                    photo=f,
                    caption=f"✅ **Image Compressed!**\n\n"
                            f"📦 Original: {original_size:.2f} MB\n"
                            f"📦 Compressed: {compressed_size:.2f} MB\n"
                            f"💾 Saved: {saved:.2f} MB\n"
                            f"📊 Reduction: {reduction:.1f}%"
                )
            
            cleanup_file(temp_output.name)
            
    except Exception as e:
        logger.error(f"Compression error: {e}")
        await query.edit_message_text("❌ Failed to compress image. Please try again.")
    finally:
        cleanup_file(image_path)
        context.user_data.pop('image_path', None)

# ============================================
# FLASK ROUTES
# ============================================

@flask_app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "running",
        "bot": "FastAActionBot",
        "version": "2.0.0",
        "bot_enabled": BOT_ENABLED,
        "port": PORT
    })

@flask_app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "bot_enabled": BOT_ENABLED,
        "token_configured": bool(TOKEN)
    }), 200

@flask_app.route('/signal', methods=['POST'])
async def webhook():
    """Receive updates from Telegram via webhook"""
    if not BOT_ENABLED or bot_app is None:
        return jsonify({"error": "Bot not configured"}), 500
    
    try:
        secret = request.headers.get('X-Webhook-Secret')
        if secret != WEBHOOK_SECRET:
            return jsonify({"error": "Invalid secret"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        
        update = Update.de_json(data, bot_app.bot)
        await bot_app.process_update(update)
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/signal', methods=['GET'])
def webhook_info():
    """Get webhook info"""
    if not BOT_ENABLED or bot_app is None:
        return jsonify({"error": "Bot not configured"}), 500
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# SETUP TELEGRAM HANDLERS
# ============================================

def setup_telegram_handlers():
    """Set up all telegram handlers"""
    if BOT_ENABLED and bot_app:
        bot_app.add_handler(CommandHandler("start", start_command))
        bot_app.add_handler(CommandHandler("help", help_command))
        bot_app.add_handler(CommandHandler("compress", compress_command))
        bot_app.add_handler(CommandHandler("shorten", shorten_command))
        bot_app.add_handler(CommandHandler("qr", qr_command))
        bot_app.add_handler(CommandHandler("convert", convert_command))
        bot_app.add_handler(CallbackQueryHandler(button_callback))
        bot_app.add_handler(MessageHandler(
            filters.TEXT | filters.PHOTO | filters.Document.IMAGE,
            handle_message
        ))
        logger.info("✅ Telegram handlers registered")
        return True
    return False

def set_webhook():
    """Set the webhook URL for the bot"""
    if not BOT_ENABLED or bot_app is None:
        logger.warning("⚠️ Bot not configured, skipping webhook setup")
        return None
    
    webhook_url = f"{RAILWAY_URL}/signal"
    logger.info(f"🔗 Setting webhook to: {webhook_url}")
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={
                "url": webhook_url,
                "secret_token": WEBHOOK_SECRET
            }
        )
        result = response.json()
        logger.info(f"📡 Webhook response: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")
        return None

# ============================================
# AUTO-SETUP ON STARTUP (for gunicorn)
# ============================================

# This runs automatically when gunicorn starts
if BOT_ENABLED and bot_app:
    setup_telegram_handlers()
    set_webhook()
else:
    logger.info("ℹ️ Bot is disabled. Add TELEGRAM_BOT_TOKEN to enable.")

logger.info("✅ FastAActionBot is ready!")

# ============================================
# MAIN ENTRY POINT (for local development)
# ============================================

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🚀 Starting FastAActionBot in development mode...")
    logger.info("=" * 50)
    
    # Start Flask server
    logger.info(f"🌐 Starting Flask server on 0.0.0.0:{PORT}")
    flask_app.run(host="0.0.0.0", port=PORT, debug=False)
