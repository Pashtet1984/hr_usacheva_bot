from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("📌 Портфолио"))
main_menu.add(KeyboardButton("🎓 Наставничество"))
main_menu.add(KeyboardButton("📋 Оставить заявку"))
main_menu.add(KeyboardButton("💳 Оплатить"))
