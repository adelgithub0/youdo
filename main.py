from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام لینک یوتوب رو برام بفرست")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("در حال دانلود... لطفا صبر کنید")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"خطا در دانلود: {e}")

app = ApplicationBuilder().token("7719610421:AAE8sovwJZp4WH62S7Z8Wl14CS6pHwSLNGE").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
