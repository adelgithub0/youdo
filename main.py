
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp, os, subprocess, datetime

TOKEN = "7719610421:AAE8sovwJZp4WH62S7Z8Wl14CS6pHwSLNGE"
VIP_FILE = "users.json"
USERS_LOG_FILE = "users_log.txt"
GUEST_LIMIT = 7
GUEST_USAGE = {}


def load_vip_users():
    if os.path.exists(VIP_FILE):
        with open(VIP_FILE, 'r') as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    return set()

def is_vip(user_id, vip_users):
    return user_id in vip_users

def can_guest_use(user_id):
    today = datetime.date.today()
    key = (user_id, today)
    return GUEST_USAGE.get(key, 0) < GUEST_LIMIT

def register_guest_usage(user_id):
    today = datetime.date.today()
    key = (user_id, today)
    GUEST_USAGE[key] = GUEST_USAGE.get(key, 0) + 1

def log_user_extended(user, user_type):
    user_id = user.id
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = user.username or ""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_lines = []
    updated = False

    if not os.path.exists(USERS_LOG_FILE):
        open(USERS_LOG_FILE, "w").close()

    with open(USERS_LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    for line in lines:
        parts = line.split(",")
        if parts[0] == str(user_id):
            count = int(parts[4]) + 1
            log_lines.append(f"{user_id},{full_name},{username},{user_type},{count},{now}")
            updated = True
        else:
            log_lines.append(line)

    if not updated:
        log_lines.append(f"{user_id},{full_name},{username},{user_type},1,{now}")

    with open(USERS_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vip_users = load_vip_users()
    user_type = "VIP" if is_vip(update.message.from_user.id, vip_users) else "Guest"
    log_user_extended(update.message.from_user, user_type)
    await update.message.reply_text("سلام! لینک یوتیوب رو بفرست 🎬")

async def process_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text
    vip_users = load_vip_users()
    user_type = "VIP" if is_vip(user_id, vip_users) else "Guest"
    log_user_extended(update.message.from_user, user_type)

    if is_vip(user_id, vip_users):
        quality_buttons = [
            [InlineKeyboardButton("MP3 🎵", callback_data=f"mp3|{url}")],
            [InlineKeyboardButton("MP4 360p", callback_data=f"360|{url}"),
             InlineKeyboardButton("MP4 720p", callback_data=f"720|{url}")]
        ]
    elif can_guest_use(user_id):
        register_guest_usage(user_id)
        quality_buttons = [
            [InlineKeyboardButton("MP3 🎵", callback_data=f"mp3|{url}")],
            [InlineKeyboardButton("MP4 360p", callback_data=f"360|{url}")]
        ]
    else:
        await update.message.reply_text("❌ تعداد استفاده روزانه‌ات تموم شده. فردا دوباره امتحان کن یا با مدیر تماس بگیر.")
        return

    reply_markup = InlineKeyboardMarkup(quality_buttons)
    await update.message.reply_text("چه فرمتی می‌خوای؟", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice, url = query.data.split("|")
    user_id = query.from_user.id

    video_file = "video.mp4"
    audio_file = "audio.mp3"

    await query.edit_message_text("🔄 در حال دانلود و تبدیل... لطفاً صبر کن.")

    try:
        if choice == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': video_file,
                'quiet': True,
                'cookiesfrombrowser': ('chrome',)
            }
        else:
            ydl_opts = {
                'format': f'bestvideo[height<={choice}]+bestaudio/best',
                'outtmpl': video_file,
                'merge_output_format': 'mp4',
                'quiet': True,
                'cookiesfrombrowser': ('chrome',)
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if choice == "mp3":
            command = ["ffmpeg", "-i", video_file, "-q:a", "0", "-map", "a", audio_file]
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(audio_file, 'rb') as f:
                await query.message.reply_audio(f)
        else:
            with open(video_file, 'rb') as f:
                await query.message.reply_video(f)

    except Exception as e:
        await query.message.reply_text(f"❌ خطا در دانلود: {str(e)}")

    finally:
        for f in [video_file, audio_file]:
            if os.path.exists(f):
                os.remove(f)

app = ApplicationBuilder().token(7719610421:AAE8sovwJZp4WH62S7Z8Wl14CS6pHwSLNGE).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
