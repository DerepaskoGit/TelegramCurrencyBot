import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"  
WEBHOOK_URL = f"https://bot_1763228205_2653_shecn.bothost.ru{WEBHOOK_PATH}" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

# --- Кортежи с курсами ---
# Рубль: 3.00 до 10.00 с шагом 0.05
RUB_VALUES = tuple(round(x * 0.01, 2) for x in range(60, 201))  # 60*0.05=3.0, 200*0.05=10.0

# Доллар: 300 до 1000 с шагом 3
USD_VALUES = tuple(x for x in range(300, 1001, 1))  # 300, 303, 306, ..., 999, 1000

# --- Функция получения курса (выбираем случайное значение) ---
def get_exchange_rate(currency_code="RUB"):
    if currency_code == "RUB":
        return random.choice(RUB_VALUES)
    elif currency_code == "USD":
        return random.choice(USD_VALUES)
    else:
        return None

# --- Хендлеры ---
@dp.message(Command("start"))
async def welcome(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Рубль к тенге', callback_data='show_kztrub')],
            [InlineKeyboardButton(text='Доллар к тенге', callback_data='show_kztusd')]
        ]
    )
    await message.answer("Получить курс:", reply_markup=markup)

@dp.callback_query(lambda c: c.data == 'show_kztrub')
async def show_rub(call: types.CallbackQuery):
    await call.answer()
    rate_rub = get_exchange_rate("RUB")
    await call.message.answer(f"Курс рубля к тенге: {rate_rub}")

@dp.callback_query(lambda c: c.data == 'show_kztusd')
async def show_usd(call: types.CallbackQuery):
    await call.answer()
    rate_usd = get_exchange_rate("USD")
    await call.message.answer(f"Курс доллара к тенге: {rate_usd}")

@dp.message(lambda message: True)
async def echo_message(message: types.Message):
    await message.answer(message.text)

# --- Webhook ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

# --- Создаем сервер aiohttp ---
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

# --- Запуск ---
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
