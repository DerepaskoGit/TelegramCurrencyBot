import requests
from xml.etree import ElementTree
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F
import asyncio

API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для получения курса
def get_exchange_rate(currency_code="RUB"):
    url = "https://nationalbank.kz/rss/rates_all.xml"
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)

    for item in tree.findall(".//item"):
        title = item.find("title").text
        if title == currency_code:
            rate = item.find("description").text
            return float(rate.replace(",", "."))

# /start
@dp.message(Command("start"))
async def welcome(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Рубль к тенге', callback_data='show_kztrub')],
            [InlineKeyboardButton(text='Доллар к тенге', callback_data='show_kztusd')]
        ]
    )
    await message.answer("Получить курс:", reply_markup=markup)

# Кнопки
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

# Эхо
@dp.message(F.text)
async def echo_message(message: types.Message):
    await message.answer(message.text)

# Запуск бота
if __name__ == "__main__":
    async def main():
        # Удаляем webhook перед polling
        await bot.delete_webhook(drop_pending_updates=True)
        # Небольшая пауза, чтобы сервер Telegram успел обработать удаление
        await asyncio.sleep(1)
        # Запуск polling
        await dp.start_polling(bot)

    asyncio.run(main())
