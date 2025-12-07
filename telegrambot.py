import os
import requests
import asyncio
import logging
from xml.etree import ElementTree
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# --- Логи ---
logging.basicConfig(level=logging.INFO)

# --- Токен бота ---
API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Пороговые значения ---
THRESHOLDS = {
    "RUB": 0.05,
    "USD": 5
}

# Последние значения курсов
last_rates = {
    "RUB": None,
    "USD": None
}

# Пользователи с включенными авто-уведомлениями
auto_users = set()

# --- Получение курса ---
def get_exchange_rate(currency_code="RUB"):
    try:
        url = "https://nationalbank.kz/rss/rates_all.xml"
        response = requests.get(url)
        tree = ElementTree.fromstring(response.content)
        for item in tree.findall(".//item"):
            title = item.find("title").text
            if title == currency_code:
                rate = item.find("description").text
                return float(rate.replace(",", "."))
    except Exception as e:
        logging.error(f"Ошибка при получении курса {currency_code}: {e}")
        return None

# --- Хендлеры ---
@dp.message(Command("start"))
async def welcome(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Рубль к тенге', callback_data='show_kztrub')],
            [InlineKeyboardButton(text='Доллар к тенге', callback_data='show_kztusd')],
            [InlineKeyboardButton(text='Включить авто-уведомления', callback_data='enable_auto')],
            [InlineKeyboardButton(text='Выключить авто-уведомления', callback_data='disable_auto')]
        ]
    )
    await message.answer("Получить курс:", reply_markup=markup)

@dp.callback_query(lambda c: c.data == 'show_kztrub')
async def show_rub(call: types.CallbackQuery):
    await call.answer()
    rate = get_exchange_rate("RUB")
    if rate:
        await call.message.answer(f"Курс рубля к тенге: {rate}")
    else:
        await call.message.answer("Ошибка получения курса рубля.")

@dp.callback_query(lambda c: c.data == 'show_kztusd')
async def show_usd(call: types.CallbackQuery):
    await call.answer()
    rate = get_exchange_rate("USD")
    if rate:
        await call.message.answer(f"Курс доллара к тенге: {rate}")
    else:
        await call.message.answer("Ошибка получения курса доллара.")

@dp.callback_query(lambda c: c.data == 'enable_auto')
async def enable_auto(call: types.CallbackQuery):
    auto_users.add(call.from_user.id)
    await call.answer("Авто-уведомления включены!")
    await call.message.answer("Теперь бот будет присылать уведомления при резких изменениях курса.")

@dp.callback_query(lambda c: c.data == 'disable_auto')
async def disable_auto(call: types.CallbackQuery):
    auto_users.discard(call.from_user.id)
    await call.answer("Авто-уведомления отключены!")
    await call.message.answer("Авто-уведомления отключены.")

@dp.message(lambda message: True)
async def echo_message(message: types.Message):
    await message.answer(message.text)

# --- Фоновая задача проверки курса ---
async def check_currency_changes():
    logging.info("Авто-проверка курса запущена.")
    while True:
        try:
            for curr in ["RUB", "USD"]:
                new_rate = get_exchange_rate(curr)
                old_rate = last_rates[curr]

                if new_rate is None:
                    continue

                if old_rate is None:
                    last_rates[curr] = new_rate
                    continue

                diff = abs(new_rate - old_rate)
                if diff >= THRESHOLDS[curr]:
                    for user_id in auto_users:
                        await bot.send_message(
                            user_id,
                            f"⚠️ Курс {curr} резко изменился!\n"
                            f"Было: {old_rate}\nСтало: {new_rate}\nРазница: {diff}"
                        )

                last_rates[curr] = new_rate

        except Exception as e:
            logging.error(f"Ошибка в авто-проверке: {e}")

        await asyncio.sleep(3600)  # проверка каждый час

# --- Запуск бота через long polling ---
async def main():
    # Запуск фоновой задачи
    asyncio.create_task(check_currency_changes())
    # Запуск polling без executor
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
