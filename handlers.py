from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher
import pandas as pd
import os

from main import bot, ADMIN_ID

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

def register_application_handlers(dp: Dispatcher):

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

        # Отправка админу
        text = (
            f"📥 *Новая заявка:*\n"
            f"👤 Имя: {data['name']}\n"
            f"🏢 Должность: {data['position']}\n"
            f"🏭 Компания: {data['company']}\n"
            f"📧 Email: {data['email']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"💬 Комментарий: {data['comment'] or '—'}"
        )

        buttons = InlineKeyboardMarkup()
        buttons.add(
            InlineKeyboardButton("✅ Принять", callback_data="approve"),
            InlineKeyboardButton("❌ Отклонить", callback_data="decline")
        )

        await bot.send_message(chat_id=int(ADMIN_ID), text=text, reply_markup=buttons, parse_mode="Markdown")

        await message.answer("✅ Заявка отправлена. Мы свяжемся с вами.")
        await state.finish()

    @dp.callback_query_handler(Text(equals=["approve", "decline"]))
    async def process_admin_decision(call: types.CallbackQuery):
        action = "✅ Принята" if call.data == "approve" else "❌ Отклонена"
        await call.message.edit_reply_markup()
        await call.message.reply(f"Заявка {action}.")
        await call.answer("Готово")

