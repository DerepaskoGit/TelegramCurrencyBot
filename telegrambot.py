# 7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY


import requests
from xml.etree import ElementTree
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram import F
import asyncio

API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'

async def delete_webhook():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook()
    print("Webhook удален")
    await bot.session.close()

asyncio.run(delete_webhook())




