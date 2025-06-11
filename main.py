import os
import logging
import pandas as pd
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Загрузка переменных из .env
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not API_TOKEN:
    raise ValueError("Ошибка: TELEGRAM_API_TOKEN не найден в .env")
if not ADMIN_ID:
    raise ValueError("Ошибка: ADMIN_ID не найден в .env")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

EXCEL_FILE = "applications.xlsx"

class ApplicationForm(StatesGroup):
    name = State()
    position = State()
    company = State()
    email = State()
    phone = State()
    comment = State()

def save_application(data):
    df_new = pd.DataFrame([data])
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_excel(EXCEL_FILE, index=False)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("ℹ️ Портфолио", "📘 Наставничество", "📋 Оставить заявку")
    await message.answer("👋 Добро пожаловать в бот наставничества HRUsacheva!\nПожалуйста, выберите пункт меню.", reply_markup=keyboard)

@dp.message_handler(Text(equals="ℹ️ Портфолио", ignore_case=True))
async def send_portfolio(message: types.Message):
    text = (
        "👤 *Оксана Усачёва* — эксперт №1 в России по эффективности человеческого актива.\n"
        "25 лет опыта в нормировании, управлении ФОТ, оптимизации численности.\n"
        "Работала в пищевке, металлургии, госсекторе и производстве."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(Text(equals="📘 Наставничество", ignore_case=True))
async def send_nastavnichestvo(message: types.Message):
    text = (
        "🎓 *Программа Наставничества по Нормированию Труда 2025*\n"
        "\n"
        "Автор и ведущая — Оксана Усачёва.\n"
        "\n"
        "📘 *Формат:*\n"
        "• 6+1 онлайн-сессий по 2 часа\n"
        "• Индивидуальный аудит\n"
        "• Excel-модели, шаблоны, BI-визуализации\n"
        "• Поддержка в Telegram-группе\n"
        "\n"
        "📅 *Темы:*\n"
        "1. Производство: нормы, хронометраж, Lean\n"
        "2. Офис: FTE, workload, документооборот\n"
        "3. АУП: управляемость, ZBHP, функции\n"
        "4. Инструменты: KPI, Power BI, ABC/XYZ\n"
        "5. Аудит численности + обратная связь\n"
        "6. Построение системы под ключ\n"
        "\n"
        "💰 *Стоимость:* 75 000 ₽\n"
        "📆 Старт: 1 июля 2025\n"
        "\n"
        "🎁 *Бонус:*\n"
        "Когнитивные навыки руководителя и обзор ИИ-инструментов для HR\n"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(Text(equals="📋 Оставить заявку", ignore_case=True), state="*")
async def start_application(message: types.Message):
    await message.answer("📋 Введите ваше имя:")
    await ApplicationForm.name.set()

@dp.message_handler(state=ApplicationForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🏢 Введите вашу должность:")
    await ApplicationForm.position.set()

@dp.message_handler(state=ApplicationForm.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("🏭 Введите название вашей компании:")
    await ApplicationForm.company.set()

@dp.message_handler(state=ApplicationForm.company)
async def process_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer("📧 Введите ваш email:")
    await ApplicationForm.email.set()

@dp.message_handler(state=ApplicationForm.email)
async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("📞 Введите ваш телефон:")
    await ApplicationForm.phone.set()

@dp.message_handler(state=ApplicationForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("💬 Добавьте комментарий (или введите «-»):")
    await ApplicationForm.comment.set()

@dp.message_handler(state=ApplicationForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["comment"] = message.text if message.text != "-" else ""

    save_application(data)

    admin_text = (
        f"📥 Новая заявка от {data['name']}\n"
        f"Должность: {data['position']}\n"
        f"Компания: {data['company']}\n"
        f"Email: {data['email']}\n"
        f"Телефон: {data['phone']}\n"
        f"Комментарий: {data['comment']}"
    )
    try:
        await bot.send_message(chat_id=int(ADMIN_ID), text=admin_text)
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")

    await message.answer("✅ Заявка отправлена. Мы свяжемся с вами.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


