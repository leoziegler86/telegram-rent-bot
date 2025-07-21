from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio
import logging
from datetime import datetime, timedelta

# ================= CONFIG ===================
API_TOKEN = "7841964593:AAHT1goKJJaHEaxiXVOiF5foaf8onEsx5B0"
ADMIN_ID = 5893418742

# ================= SETUP ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ============== FSM STATES ==================
class Reservation(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_long_term = State()

# ============== STORAGE =====================
cars = [
    {"name": "Hyundai Ioniq", "price": "55 AZN", "image_url": "https://i.postimg.cc/FszTZKq9/ioniq.jpg"},
    {"name": "BYD Destroyer 05", "price": "50 AZN", "image_url": "https://i.postimg.cc/zBkxdH8f/byd-destroyer.jpg"}
]

user_language = {}
user_selected_car = {}

lang_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🇦🇿 AZ"), KeyboardButton(text="🇷🇺 RU"), KeyboardButton(text="🇬🇧 EN")]],
    resize_keyboard=True
)

LANG = {
    'az': {
        'welcome': "Salam! Botumuza xoş gəlmisiniz. Menyudan seçim edin:",
        'menu': ["🚗 Avtomobillər", "🗕️ Rezerv Et", "📞 Əlaqə"],
        'contact': "📞 Əlaqə: +99450 275 07 70\n👤 Admin: @Leoziegler",
        'thanks': "Təşəkkürlər! Rezervasiya qeydə alındı.",
        'choose_car': "Avtomobil seçin:",
        'enter_name': "Ad və soyadınızı daxil edin:",
        'enter_phone': "Əlaqə nömrənizi daxil edin:",
        'start_date': "Avtomobili alma tarixi:",
        'end_date': "Avtomobili təslim etmə tarixi:",
        'ask_long_term': "Uzunmüddətli icarə istəyirsiniz? (Bəli / Xeyr)",
        'confirm': "Rezervasiya qeydiyyata alındı.\n\n📌 Uzunmüddətli icarə üçün zəhmət olmasa birbaşa əlaqə saxlayın: +99450 275 07 70"
    },
    'ru': {
        'welcome': "Здравствуйте! Добро пожаловать в наш бот. Пожалуйста, выберите из меню:",
        'menu': ["🚗 Автомобили", "🗕️ Бронирование", "📞 Контакты"],
        'contact': "📞 Контакт: +99450 275 07 70\n👤 Админ: @Leoziegler",
        'thanks': "Спасибо! Бронирование зарегистрировано.",
        'choose_car': "Выберите автомобиль:",
        'enter_name': "Введите ваше имя и фамилию:",
        'enter_phone': "Введите номер телефона:",
        'start_date': "Дата получения автомобиля:",
        'end_date': "Дата возврата автомобиля:",
        'ask_long_term': "Хотите длительную аренду? (Да / Нет)",
        'confirm': "Бронирование зарегистрировано.\n\n📌 Для долгосрочной аренды свяжитесь напрямую: +99450 275 07 70"
    },
    'en': {
        'welcome': "Hello! Welcome to our bot. Please choose from the menu:",
        'menu': ["🚗 Cars", "🗕️ Reserve", "📞 Contact"],
        'contact': "📞 Contact: +99450 275 07 70\n👤 Admin: @Leoziegler",
        'thanks': "Thank you! Reservation registered.",
        'choose_car': "Choose a car:",
        'enter_name': "Enter your full name:",
        'enter_phone': "Enter your phone number:",
        'start_date': "Pick-up date:",
        'end_date': "Return date:",
        'ask_long_term': "Do you want a long-term rental? (Yes / No)",
        'confirm': "Reservation registered.\n\n📌 For long-term rental, please contact directly: +99450 275 07 70"
    }
}

# ============= INLINE CALENDAR ==============
def generate_calendar(callback_prefix):
    builder = InlineKeyboardBuilder()
    today = datetime.today()
    for i in range(30):
        date = today + timedelta(days=i)
        builder.row(
            InlineKeyboardButton(
                text=date.strftime("%d.%m.%Y"),
                callback_data=f"{callback_prefix}_{date.strftime('%d.%m.%Y')}"
            )
        )
    return builder.as_markup()

# ============= COMMANDS ======================
@dp.message(lambda msg: msg.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Zəhmət olmasa dil seçin:", reply_markup=lang_kb)

@dp.message(lambda msg: msg.text in ["🇦🇿 AZ", "🇷🇺 RU", "🇬🇧 EN"])
async def set_lang(message: types.Message):
    lang_code = {'🇦🇿 AZ': 'az', '🇷🇺 RU': 'ru', '🇬🇧 EN': 'en'}[message.text]
    user_language[message.from_user.id] = lang_code
    await message.answer(
        LANG[lang_code]['welcome'],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=btn)] for btn in LANG[lang_code]['menu']],
            resize_keyboard=True))

@dp.message(lambda msg: any(msg.text in LANG[lang]['menu'] for lang in LANG))
async def menu_handler(message: types.Message, state: FSMContext):
    lang = user_language.get(message.from_user.id, 'az')
    if message.text == LANG[lang]['menu'][0]:  # Avtomobillər
        for car in cars:
            await message.answer_photo(photo=car['image_url'], caption=f"🚘 {car['name']}\n💵 {car['price']}")
    elif message.text == LANG[lang]['menu'][1]:  # Rezerv Et
        await message.answer(LANG[lang]['choose_car'])
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=car['name'])] for car in cars],
            resize_keyboard=True)
        await message.answer("Avtomobil seçin:", reply_markup=kb)
    elif message.text == LANG[lang]['menu'][2]:  # Əlaqə
        await message.answer(LANG[lang]['contact'])

@dp.message(lambda msg: any(car['name'] == msg.text for car in cars))
async def selected_car(message: types.Message, state: FSMContext):
    user_selected_car[message.from_user.id] = message.text
    lang = user_language.get(message.from_user.id, 'az')
    await message.answer(LANG[lang]['enter_name'])
    await state.set_state(Reservation.waiting_for_name)

@dp.message(Reservation.waiting_for_name)
async def reserve_name(message: types.Message, state: FSMContext):
    lang = user_language.get(message.from_user.id, 'az')
    await state.update_data(name=message.text)
    await message.answer(LANG[lang]['enter_phone'])
    await state.set_state(Reservation.waiting_for_phone)

@dp.message(Reservation.waiting_for_phone)
async def reserve_phone(message: types.Message, state: FSMContext):
    lang = user_language.get(message.from_user.id, 'az')
    await state.update_data(phone=message.text)
    await message.answer(LANG[lang]['start_date'], reply_markup=generate_calendar("START"))
    await state.set_state(Reservation.waiting_for_start_date)

@dp.callback_query(lambda c: c.data.startswith("START_"))
async def select_start(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    await state.update_data(start_date=date)
    lang = user_language.get(callback.from_user.id, 'az')
    await callback.message.answer(LANG[lang]['end_date'], reply_markup=generate_calendar("END"))
    await state.set_state(Reservation.waiting_for_end_date)

@dp.callback_query(lambda c: c.data.startswith("END_"))
async def select_end(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    await state.update_data(end_date=date)
    lang = user_language.get(callback.from_user.id, 'az')
    await callback.message.answer(LANG[lang]['ask_long_term'])
    await state.set_state(Reservation.waiting_for_long_term)

@dp.message(Reservation.waiting_for_long_term)
async def reserve_long_term(message: types.Message, state: FSMContext):
    lang = user_language.get(message.from_user.id, 'az')
    data = await state.get_data()
    car = user_selected_car.get(message.from_user.id, "")
    response = message.text.strip().lower()
    is_long = response in ["bəli", "bele", "beli", "hə", "he", "yes", "да"]

    status = {
        'az': "✅ Bəli" if is_long else "❌ Xeyr",
        'ru': "✅ Да" if is_long else "❌ Нет",
        'en': "✅ Yes" if is_long else "❌ No"
    }[lang]

    admin_msg = (
        f"Yeni rezervasiya:\n"
        f"🚘 Avtomobil: {car}\n"
        f"👤 Ad: {data['name']}\n"
        f"📞 Nömrə: {data['phone']}\n"
        f"📅 Tarix: {data['start_date']} - {data['end_date']}\n"
        f"📌 Uzunmüddətli icarə: {status}"
    )
    await bot.send_message(ADMIN_ID, admin_msg)
    await message.answer(LANG[lang]['confirm'])
    await state.clear()

# ============ BOT START =====================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
