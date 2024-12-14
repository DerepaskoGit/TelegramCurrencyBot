# 7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY


import requests
from xml.etree import ElementTree

def get_exchange_rate(currency_code="RUB"):
    url = "https://nationalbank.kz/rss/rates_all.xml"
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)

    for item in tree.findall(".//item"):
        title = item.find("title").text
        if title == currency_code:
            rate = item.find("description").text
            return float(rate.replace(",", "."))


rate_rub = get_exchange_rate("RUB")
rate_usd = get_exchange_rate("USD")



# Bot

import telebot
from telebot.types import *

API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def welkome(message):
    markup = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton(text='Рубль к тенге', callback_data='show_kztrub')
    button_2 = InlineKeyboardButton(text='Доллар к тенге', callback_data='show_kztusd')

    markup.add(button_1)
    markup.add(button_2)

    bot.send_message(message.chat.id, 'Получить курс:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'show_kztrub')
def callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, rate_rub)

@bot.callback_query_handler(func=lambda call: call.data == 'show_kztusd')
def callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, rate_usd)

@bot.message_handler(func=lambda message: True)
def echo_message(message): 
    bot.send_message(message.chat.id, message.text)

bot.infinity_polling()