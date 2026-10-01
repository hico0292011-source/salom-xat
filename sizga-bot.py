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

# Sizning Telegram ID'ingiz admin sifatida o'rnatildi
ADMIN_ID = int(os.environ.get("ADMIN_ID", 8715668931))

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

# Turfa xil mavzudagi xabarlar ro'yxati
RANDOM_MESSAGES = [
    "Bilasizmi? Dunyodagi eng qisqa urush 1896-yilda Angliya va Zanzibar o'rtasida bo'lgan. U atigi 38 daqiqa davom etgan! ⏱",
    "Muvaffaqiyat - bu yiqilishdan qo'rqmaslik, balki har yiqilganda qayta turishdir. Hech qachon taslim bo'lmang! 🚀",
    "Hazil vaqti: Dasturchining hayoti – 10% kod yozish, 90% esa o'sha yozgan kodi nega ishlamayotganini tushunishga sarflanadi. 💻😅",
    "Vaqt — bu bizda mavjud bo'lgan eng qimmatli, ammo eng tez tugaydigan resurs. Uni to'g'ri sarflang! ⏳",
    "Qiziqarli fakt: Inson miyasi tunda, uxlashga yotganda, kunduzgisidan ko'ra ancha faolroq ishlaydi. 🧠✨",
    "Baxtli bo'lish uchun hamma narsaga ega bo'lish shart emas, shunchaki boriga shukr qilish va uni qadrlash yetarli. 🌸",
    "Kosmos haqida: Agar fazoda ikkita bir xil metal bo'lagi bir-biriga tegib ketsa, ular butunlay birlashib ketadi (sovuq payvandlash deb ataladi). 🌌",
    "O'zingizga eslatma: Suv ichishni unutmang! Salomatlik hamma narsadan muhim. 💧",
    "Oktapuslarning (sakkizoyoq) naqd uchta yuragi bor! Biri butun tanaga, qolgan ikkitasi esa jabralarga qon haydaydi. 🐙",
    "Katta maqsadlarga birdaniga emas, har kungi kichik qadamlar orqali erishiladi. Bugun o'z maqsadingiz sari bitta kichik qadam tashlang! 🚶‍♂️",
    "Tabassum qiling! Bu nafaqat kayfiyatingizni ko'taradi, balki immunitetingizni ham mustahkamlaydi. 😊",
    "Tarixiy fakt: Birinchi kompyuter sichqonchasi 1964-yilda yog'ochdan yasalgan bo'lgan. 🖱🪵",
    "Hayotiy haqiqat: Agar siz hech qachon xato qilmayotgan bo'lsangiz, demak, hech qanday yangi narsa o'rganmayapsiz. 📈"
]

# /start buyrug'i
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.chat.id
    user_ids.add(user_id)
    save_users(user_ids)
    
    await message.answer(
        "Xush kelibsiz! 👋\n\n"
        "Men sizga har 12 soatda turli xil qiziqarli ma'lumotlar, faktlar, hazillar va motivatsion xabarlar yuborib turaman! 🎲"
    )

# FAQAT ADMIN UCHUN BUYRUQ: /users
@dp.message(Command("users"))
async def admin_users_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda bu buyruqdan foydalanish huquqi yo'q! ❌")
        return
    
    count = len(user_ids)
    if count == 0:
        await message.answer("Hozircha botdan hech kim foydalanmayapti.")
        return
    
    text = f"📊 **Botdan foydalanuvchilar soni:** {count} ta\n\n**Foydalanuvchilar ID ro'yxati:**\n"
    for i, uid in enumerate(list(user_ids), 1):
        text += f"{i}. `{uid}`\n"
    
    await message.answer(text, parse_mode="Markdown")

# Har 12 soatda ishlaydigan funksiya
async def send_periodic_messages():
    if not user_ids:
        return
    
    message_text = random.choice(RANDOM_MESSAGES)
    logger.info("Davriy xabarlar yuborilmoqda...")
    
    for uid in list(user_ids):
        try:
            await bot.send_message(chat_id=uid, text=message_text)
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik ({uid}): {e}")

async def main():
    logger.info("Bot ishga tushmoqda...")

    # Render porti uchun mini web-server
    async def handle(request):
        return web.Response(text="Bot har 12 soatda ishlamoqda!")

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # O'zbekiston vaqti bilan taymer o'rnatish
    tashkent_tz = pytz.timezone("Asia/Tashkent")
    scheduler = AsyncIOScheduler(timezone=tashkent_tz)
    scheduler.add_job(send_periodic_messages, 'interval', hours=12)
    scheduler.start()

    # Bot Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
