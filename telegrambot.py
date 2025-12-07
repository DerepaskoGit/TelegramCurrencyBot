import os
import requests
import asyncio
from xml.etree import ElementTree
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'
WEBHOOK_PATH = f"/webhook/{API_TOKEN}" # путь webhook
WEBHOOK_URL = f"https://bot_1763228205_2653_shecn.bothost.ru{WEBHOOK_PATH}" # укажи свой домен или субдомен

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Пороговые значения ---
THRESHOLDS = {
    "RUB": 0.05,   # 5 копеек
    "USD": 5       # 5 тенге
}

# Последние значения курсов
last_rates = {
    "RUB": None,
    "USD": None
}

# Пользователи, которым включены авто-уведомления
auto_users = set()


# --- Получение курса из НБК ---
def get_exchange_rate(currency_code="RUB"):
    url = "https://nationalbank.kz/rss/rates_all.xml"
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)
    for item in tree.findall(".//item"):
        title = item.find("title").text
        if title == currency_code:
            rate = item.find("description").text
            return float(rate.replace(",", "."))


# --- Хендлеры ---
@dp.message(Command("start"))
async def welcome(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Рубль к тенге', callback_data='show_kztrub')],
            [InlineKeyboardButton(text='Доллар к тенге', callback_data='show_kztusd')],
            [InlineKeyboardButton(text='Включить авто-уведомления', callback_data='enable_auto')]
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


@dp.callback_query(lambda c: c.data == 'enable_auto')
async def enable_auto(call: types.CallbackQuery):
    auto_users.add(call.from_user.id)
    await call.answer("Авто-уведомления включены!")
    await call.message.answer("Теперь бот будет присылать уведомления при резких изменениях курса.")


@dp.message(Command("auto_off"))
async def auto_off(message: types.Message):
    auto_users.discard(message.from_user.id)
    await message.answer("Авто-уведомления отключены.")


@dp.message(lambda message: True)
async def echo_message(message: types.Message):
    await message.answer(message.text)


# --- Проверка изменения курса ---
async def check_currency_changes():
    while True:
        try:
            for curr in ["RUB", "USD"]:
                new_rate = get_exchange_rate(curr)
                old_rate = last_rates[curr]

                # Первое значение запоминаем, но не сравниваем
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
            print("Ошибка в авто-проверке:", e)

        await asyncio.sleep(3600)  # проверка каждые 3600 секунд (Час)


# --- Webhook ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(check_currency_changes())  # запускаем проверку


async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()


# --- Aiohttp сервер ---
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

# --- Запуск ---
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
