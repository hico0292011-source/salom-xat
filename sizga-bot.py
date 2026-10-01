import os
import asyncio
import logging
import random
import json
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, TelegramObject

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# BOT SOZLAMALARI
# ==========================================
BOT_TOKEN = "8772192229:AAFBipQYj8Z8zGpg3zXxZ-yzlUQ_dHu-rQU"
ADMIN_ID = 8715668931

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==========================================
# FOYDALANUVCHILAR BAZASI (users.json)
# ==========================================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Faylga saqlashda xatolik: {e}")

users_db = load_users()

# Barcha foydalanuvchilarni avtomatik ro'yxatga olish middleware-i
class UserTrackerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        if user:
            uid = str(user.id)
            if uid not in users_db:
                users_db[uid] = {
                    "name": user.full_name or "Foydalanuvchi",
                    "username": f"@{user.username}" if user.username else "yo'q"
                }
                save_users(users_db)
            else:
                users_db[uid]["name"] = user.full_name or "Foydalanuvchi"
                users_db[uid]["username"] = f"@{user.username}" if user.username else "yo'q"
                save_users(users_db)
        return await handler(event, data)

dp.message.outer_middleware(UserTrackerMiddleware())

# ==========================================
# 200 TA KAYFIYATNI KO'TARUVCHI JUMLA
# ==========================================
MOOD_MESSAGES = [
    f"{i+1}. " + msg for i, msg in enumerate([
        "Bugun seni ajoyib kun kutmoqda! Tassavvur qilganingdan ham yaxshiroq bo'ladi. ✨",
        "Tabassum qil! Sening kulgushing dunyoni go'zalroq qiladi. 😊",
        "Kichik qadamlar ham katta muvaffaqiyatlarga olib keladi. Davom et! 🚀",
        "O'zingga ishon, sen har qanday qiyinchilikdan kuchlisan! 💪",
        "Bugungi kuning xushkayfiyat va omadga to'la bo'lsin! 🌟",
        "Charchadingmi? Biroz dam ol va yana olg'a intil. Sen uddalaysan! ☕",
        "Hozirgi lahzadan zavqlan, hayot jilmayishing uchun sabablarga to'la! 🌈",
        "Har bir yangi kun — bu yangi imkoniyat. Uni boy berma! ☀️",
        "Sening mehnatlaring albatta o'z mevasini beradi. Sabrli bo'l! 🍎",
        "Dunyoda sen kabi inson borligi uchun atrof go'zalroq! ⭐",
        "Niyatlaring xolis bo'lsa, yo'llaring har doim ochiq bo'ladi. ✨",
        "Xatolardan qo'rqma, ular seni yanada tajribali va kuchli qiladi. 📚",
        "Bugun o'zing uchun kichik bo'lsa ham yoqimli narsa qil! 🎁",
        "Har doim yodda tut: Eng yaxshi kunlaring hali oldinda! 🌄",
        "Sening energiyang va ishtiyoqing boshqalarga ham ilhom beradi. 🔥",
        "O'z imkoniyatlaringga shubha qilma, sen o'ylaganingdan ham iqtidorlisan! 💎",
        "Yaxshi kayfiyat — bu sening eng yaxshi quroling! 😊",
        "Bugun hech bo'lmaganda bir kishiga tabassum ulash! 🌸",
        "Orzularing sari intilishdan hech qachon to'xtama. 🦅",
        "Bugun sen kutgan xushxabar keladi! ✉️",
        "O'zingizni boshqalar bilan solishtirmang, siz o'zgachasiz! ✨",
        "Hayot xuddi ko'zgu kabidir: unga jilmayib qarasang, u ham senga jilmayadi. 🪞",
        "Har bir qiyinchilik ketidan albatta yengillik keladi. 🌅",
        "Bugun yangi narsani o'rganish uchun ajoyib kun! 📖",
        "O'zingga g'amxo'rlik qilishni unutma. Sen eng muhimsan! 💖",
        "Katta natijalar kichik odatlardan boshlanadi. 🎯",
        "Yuzingda tabassum bo'lsin, muammolar o'zi chekinadi! 🙂",
        "Ajoyib g'oyalaringni amalga oshirish vaqti keldi! 💡",
        "Eski sahifalarni yopib, yangi va yorqin sahifa och! 📖✨",
        "Sening samimiyliging — eng katta boyliging. 💎",
        "Bugungi kuning quvonchli voqealarga boy bo'lsin! 🎈",
        "O'zingga bo'lgan ishonchni yoqib qo'y, u seni yoritadi! 💡",
        "Yiqilish — bu mag'lubiyat emas, qayta turmaslik mag'lubiyatdir. 🚀",
        "Seni oldinda juda ko mehr va baxt kutmoqda. ❤️",
        "Hamma narsa o'z vaqti va soatida go'zal bo'ladi. ⏳",
        "Sen bugun ham juda ko'p narsaga erisha olasan! 🔥",
        "Bugungi mehnat kelajakdagi erkinligingdir. 🏆",
        "Ijobiy fikrla, ijobiy natijalarga erish! 🧠✨",
        "Yana bir kun, yangi imkoniyat va yangi zafarlar! 🌤️",
        "O'zingni qadrla, sen takrorlanmas insonsan! 👑",
        "Bugun o'zing yoqtirgan musiqani tingla va zavqlan! 🎵",
        "Sening tabassuming kimningdir kunini yoritishi mumkin. ☀️️",
        "Qadam tashlashdan qo'rqma, omad jasurlarga kulib boqadi! 🦁",
        "Bugungi kuning omad va baraka bilan to'lsin! 🍀",
        "Muammolarga yechim sifatida qara, g'ov sifatida emas. 🔑",
        "Ertangi kun bugungi harakatlaringga bog'liq. 🏃‍♂️",
        "Har doim o'z qadriyatlaringga sodiq qol. 💎",
        "Dunyoga ezgulik urug'ini soch, u albatta unib chiqadi. 🌱",
        "Bugun o'zingga 'Men uddalayman' deb ayt! 💪",
        "Atrofdagi go'zalliklarni payqashni o'rgan. 🌸",
        "Orzularing chegarasiz, demak imkoniyatlaring ham shunday! 🌌",
        "Bugun ko'proq kulishga harakat qil! 😆",
        "Har bir erishilgan kichik g'alabani nishonla! 🎉",
        "Sening ichki dunyong juda boy va go'zal. 🎨",
        "O'z maqsadlaring sari dadil odimla! 👣",
        "Niyating posak bo'lsin, yo'ling ravon bo'ladi. 🛣️",
        "Yaxshi kayfiyat ulashish — bu eng yaxshi sovg'a! 🎁",
        "Sen har qanday murakkab vaziyatdan chiqib keta olasan. 🧗",
        "Bugungi kundan unumli foydalanib qol! ⏱️",
        "Senga bo'lgan ishonchim komil, olg'a! 🚀",
        "Muvaffaqiyat kaliti — matonatda! 🔑",
        "Har bir kunda quvonch uchun kamida bitta sabab bor. 🌻",
        "Ozgina harakat ham umuman harakat qilmaslikdan yaxshi. 🚶‍♂️",
        "Sening mehnating besamar ketmaydi. 🏆",
        "Bugungi kunda yangi va foydali bilim ol! 🧠",
        "Dunyoga ochiq ko'z va ijobiy kayfiyat bilan boq. 🌍",
        "Atrofdagilarga yaxshilik qil, u senga karra ko'payib qaytadi. 🔄",
        "Sen har doim eng yaxshisiga loyiqsan! 💖",
        "Bugun o'zingni xursand qiladigan narsa bilan mashg'ul bo'l! 🎨",
        "Hayot — bu sayohat, har bir lahzasidan zavqlan! 🧳",
        "G'oyalaringni shakllantir va harakatni boshla! ⚡",
        "O'zingni asra, sen atrofingdagilar uchun muhimsan! 🛡️",
        "Xatolaring — bu sening tajribang, ulardan sabak ol. 📝",
        "Har qanday vaziyatda ham optimizm bilan yondash. ☀️",
        "Sening qobiliyating juda yuqori, uni namoyon et! 🌟",
        "Bugungi kun salomatlik va xotirjamlik keltirsin! 🧘‍♂️",
        "Doimo rivojlanishda bo'l, to'xtab qolma! 📈",
        "Sening samimiy kulguting eng yaxshi dori! 💊😊",
        "Jasur bo'l, xavf-xatarlardan qo'rqma! 🦅",
        "O'z hayoting muallifi o'zingsan! ✍️",
        "Bugun do'stlaringga shirin so'zlar ayt! 🗣️❤️",
        "Muvaffaqiyat — bu har kungi kichik intilishlar yig'indisi. 🧱",
        "Kayfiyatingni tushirma, hammasi yaxshi bo'ladi! 🕊️",
        "Senga omad har qadamda hamroh bo'lsin! 🍀",
        "Kutgan narsang albatta ro'yobga chiqadi! 🌠",
        "Bugun yangi imkoniyatlar eshigi ochiladi! 🚪✨",
        "Qalbingda har doim bahor havolasi bo'lsin! 🌸",
        "O'zingizni seving va hurmat qiling! 💝",
        "Murakkabliklar seni yanada mukammal qiladi. 💎",
        "Bugun orzularingizga bir qadam yaqinlashdingiz! 🐾",
        "Tabassum — bu eng go'zal bezak! 😃",
        "Atrofingizdagi insonlarga quvonch ulashing! 🎈",
        "Har doim yaxshilikka ishoning! 🕊️",
        "Mehnat va sabr har qanday to'siqni yengadi. ⛏️",
        "Bugungi kun yorqin xotiralar bilan muhrlansin! 📸",
        "Sizning kelajagingiz porloq! 🔮",
        "Har bir lahza — bu yangi boshlanish! 🌅",
        "O'z maqsadingizdan chalg'imang! 🎯",
        "Bugun o'zingizga maqtov ayting! 👏",
        "Hayot go'zal va u kutilmagan sovg'alarga to'la! 🎊",
        "Ezgulik har doim g'alaba qozonadi! ⚔️❤️",
        "O'z fikrlaringizni tartibga soling va olg'a boring! 🧠",
        "Sizda katta potensial bor! ⚡",
        "Bugun yangi marralarni zabt etish kuni! 🏔️",
        "Insoniyat uchun foydali inson bo'ling! 🌍",
        "Quvonch va shodlik doimiy hamrohingiz bo'lsin! 😄",
        "O'z tuyg'ularingizni ifoda etishdan tortinmang! 🗣️",
        "Bugungi kuningiz baxtli daqiqalarga boy bo'lsin! ⏳💓",
        "Hammasi o'z qo'lingizda, aslo taslim bo'lmang! 🤲",
        "Doimo oldinga qarab harakat qiling! 🏃‍♀️",
        "Siz har doim eng yaxshi yechimni topa olasiz! 🧩",
        "Atrofingizdagilarga mehr va e'tibor bering! 🤗",
        "Bugun o'zingiz xohlagan ishni bajaring! 🎯",
        "Sizning matonatingizga tasanno! 👏",
        "Kutmagan joyingizdan omad kulib boqadi! 🎰",
        "Hayotdagi har bir sinov — bu tajriba! 📖",
        "O'z maqsadingiz yo'lida charchamang! 🚴‍♂️",
        "Sizga cheksiz energiya va kuch tilayman! ⚡",
        "Bugun ajoyib hodisalar sodir bo'ladi! 🎆",
        "Qalbingiz tinch va xotirjam bo'lsin! 🕊️",
        "Har bir kundan hikmat izlang! 🦉",
        "O'zingizga va kuchingizga ishoning! 💪",
        "Yorqin kelajak sizni kutmoqda! 🚀",
        "Siz dunyodagi eng baxtli insonlardan birisiz! 🌈",
        "O'z imkoniyatlaringizni kengaytiring! 🌐",
        "Bugungi kun unumli va natijali bo'lsin! 📊",
        "Hech qachon tushkunlikka tushmang! ☀️️",
        "Siz har doim eng to'g'ri yo'lni tanlaysiz! 🧭",
        "Bugun yangi do'stlar orttirishingiz mumkin! 🤝",
        "O'zingizga bo'lgan ishonchni asrang! 🛡️",
        "Orzularingiz tomon dadil qadam tashlang! 🚶‍♀️",
        "Sizning g'oyangiz dunyoni o'zgartirishi mumkin! 💡",
        "Bugun atrofga ijobiy energiya tarating! 📡",
        "Qiyinchiliklar o'tib ketadi, g'alaba qoladi! 🏆",
        "O'zingiz yoqtirgan mashg'ulot bilan shug'ullaning! 🎸",
        "Hayot har bir soniyasida go'zaldir! ⏱️",
        "Sizning mehnatingiz yuqori baholanadi! 🥇",
        "Bugun yangi zafarlar kuni! 🚩",
        "Tabassum qilishni aslo unutmang! 😊",
        "O'z prinsiplaringizga sodiq bo'ling! 🏛️",
        "G'alaba har doim mehnatkashlar tomonda! 🚜",
        "Sizning xarakteringiz juda kuchli! 🗿",
        "Bugun qalbingiz quvonchga to'lsin! 💖",
        "O'z orzularingizni reallikka aylantiring! 🪄",
        "Siz bilan muloqot qilish juda yoqimli! 💬",
        "Har qanday vaziyatda ham umidni uzmang! ⚓",
        "Bugun ajoyib uchrashuvlar kuni bo'lishi mumkin! ☕",
        "Siz har qanday cho'qqini zabt eta olasiz! 🧗‍♀️",
        "O'zingizga imkoniyat bering va harakat qiling! 🎬",
        "Hayotingiz go'zal xotiralarga to'la bo'lsin! 📚",
        "Sizning samimiyligingiz hammaga yoqadi! 🌟",
        "Bugun yangi rejalarni tuzing! 📝",
        "Omad doimo siz tomonda bo'lsin! 🎲",
        "O'z baxtingiz yaratuvchisi o'zingizsiz! 🏗️",
        "Tinchlik va totuvlik hamrohingiz bo'lsin! 🕊️",
        "Siz juda sabrli va matonatlisiz! 🧘",
        "Bugun yangi marralar sari yo'l oling! ⛵",
        "Har bir kunda yangi mo'jiza bor! 🦄",
        "Sizning iqtidoringizga ko'z tegmasin! 🎨",
        "O'z hayotingizni yorqin ranglarga boyiting! 🖌️",
        "Bugungi kun unutilmas bo'lsin! 🌟",
        "Siz doimo yaxshilikka intilasiz! 💖",
        "O'zingizga va kelajagingizga ishoning! 🚀",
        "Bugun siz kutgan mo'jiza sodir bo'lishi mumkin! ✨",
        "Xursandchilik va kulgu hamrohingiz bo'lsin! 😂",
        "Sizning matonatingiz va irodangiz tahsinga loyiq! 🛡️",
        "Har doim yuqori kayfiyatda bo'ling! 🎈",
        "Bugun maqsadlaringiz sari yana bir qadam tashlang! 👣",
        "Siz har doim eng to'g'ri qarorni qabul qilasiz! ⚖️",
        "G'alabalar silsilasi davom etsin! 🏆",
        "Bugun yangi ufqlarni kashf eting! 🌅",
        "Sizning tabassumingiz atrofni yoritadi! 💡",
        "O'z kuchingizni to'g'ri yo'naltiring! 🎯",
        "Hayot go'zal, undan to'liq bahra oling! 🍷",
        "Siz har doim mukammallikka intilasiz! 💎",
        "Bugungi kuningiz unumli va fayzli bo'lsin! 🥐",
        "Sizning kelajagingiz juda buyuk! 🏰",
        "O'z maqsadingizdan hech qachon chekinmang! 🛡️",
        "Bugun atrofidagilarga xushkayfiyat ulashing! 🎁",
        "Siz har qanday qiyinchilikni yenga olasiz! 💥",
        "Ezgulik va mehr doimo qalbingizda bo'lsin! ❤️",
        "O'zingizni asrang va doimo jilmayib yuring! 😊",
        "Bugungi kun faqat va faqat quvonch keltirsin! 🎉"
    ])
]

# ==========================================
# TUGMALAR (REPLY KEYBOARD)
# ==========================================
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="🎲 Kayfiyatni ko'tarish")],
        [KeyboardButton(text="📊 Statistika")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ==========================================
# HANDLERLAR
# ==========================================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    text = (
        f"Assalomu alaykum, **{message.from_user.first_name}**! 👋\n\n"
        f"Ushbu bot sizga har kuni ajoyib kayfiyat va motivatsiya ulashadi ✨\n"
        f"Tugmalardan birini tanlang va foydalaning 👇"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@dp.message(F.text == "🎲 Kayfiyatni ko'tarish")
async def send_mood_quote(message: types.Message):
    quote = random.choice(MOOD_MESSAGES)
    await message.answer(f"✨ **Siz uchun maxsus:**\n\n{quote}", parse_mode="Markdown")

@dp.message(F.text == "📊 Statistika")
async def send_stats(message: types.Message):
    count = len(users_db)
    await message.answer(f"📊 **Bot foydalanuvchilari soni:** {count} ta", parse_mode="Markdown")

@dp.message(Command("users"))
async def admin_users_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda bu buyruqni ishlatish huquqi yo'q ❌")
        return

    count = len(users_db)
    text = f"📊 **Umumiy foydalanuvchilar:** {count} ta\n\n**Songi foydalanuvchilar:**\n"
    for i, (uid, uinfo) in enumerate(list(users_db.items())[-20:], 1):
        name = uinfo.get("name", "Noma'lum")
        uname = uinfo.get("username", "yo'q")
        text += f"{i}. {name} ({uname}) | ID: `{uid}`\n"

    await message.answer(text, parse_mode="Markdown")

# ==========================================
# RENDER SERVER VA MAIN LOOP
# ==========================================
async def main():
    logger.info("Bot ishga tushmoqda...")

    # Render server portini band qilish uchun oddiy aiohttp server
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
