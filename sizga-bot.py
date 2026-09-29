import os
import asyncio
import logging
import random
import json
import pytz
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Botingizning API Tokeni
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8772192229:AAGP_TiLNzROuCW2n_CvDcDTeTVieSSiwxs")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Foydalanuvchilar ID larini saqlash uchun fayl
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                return set(json.load(f))
            except Exception:
                return set()
    return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

user_ids = load_users()

# Ertalabki komplimentlar va motivatsion xabarlar ro'yxati
COMPLIMENTS = [
    "Xayrli tong! ☀️ Bugungi kuningiz omadli va quvonchli o'tsin! Siz har qanday maqsadga erisha olasiz! ✨",
    "Ertalabki tabassum kuningizni yoritadi. Bugun siz uchun ajoyib imkoniyatlar kuni bo'ladi! 😊",
    "Xayrli tong! O'zingizga ishoning, siz juda kuchli va iqtidorlisiz! 💪",
    "Bugungi yangi kun yangi muvaffaqiyatlar olib kelsin! Kuningiz maroqli o'tsin! 🌟",
    "Xayrli tong! Bugun ham atrofingizdagilarga nur va yaxshilik ulashing! Yuzingizdan tabassum arimasin! 🌸",
    "Yangi kun muborak! Bugun o'zingiz orzu qilgan biron ajoyib ishni amalga oshiring! 🚀",
    "Xayrli tong! Siz bugun juda ham g'ayratlisiz, harakatdan to'xtamang! ⭐"
]

# /start buyrug'i
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.chat.id
    user_ids.add(user_id)
    save_users(user_ids)
    
    await message.answer(
        "Xush kelibsiz! 👋\n\n"
        "Men sizga har kuni ertalab soat 07:00 da kayfiyatni ko'taruvchi "
        "maxsus kompliment va motivatsion xabarlar yuborib turaman! ☀️"
    )

# Har kuni 07:00 da ishlaydigan funksiya
async def send_morning_messages():
    if not user_ids:
        return
    
    message_text = random.choice(COMPLIMENTS)
    logger.info("Ertalabki xabarlar yuborilmoqda...")
    
    for uid in list(user_ids):
        try:
            await bot.send_message(chat_id=uid, text=message_text)
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik ({uid}): {e}")

async def main():
    logger.info("Bot ishga tushmoqda...")

    # 1. Render porti uchun mini web-server
    async def handle(request):
        return web.Response(text="Sizga Morning Bot is running!")

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # 2. O'zbekiston vaqti (Asia/Tashkent) bo'yicha soat 07:00 ga taymer o'rnatish
    tashkent_tz = pytz.timezone("Asia/Tashkent")
    scheduler = AsyncIOScheduler(timezone=tashkent_tz)
    scheduler.add_job(send_morning_messages, 'cron', hour=7, minute=0)
    scheduler.start()

    # 3. Bot Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
