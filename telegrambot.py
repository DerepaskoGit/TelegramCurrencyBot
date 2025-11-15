from aiogram import Bot
import asyncio

API_TOKEN = '7763028058:AAGg_wZm0xDJXEI9i42Qlc6cm9tVqwdkjGY'

async def delete_webhook():
    bot = Bot(token=API_TOKEN)
    # Удаляем webhook полностью и сбрасываем все pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook успешно удалён. Теперь можно запускать polling.")
    await bot.session.close()

asyncio.run(delete_webhook())
