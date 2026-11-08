import asyncio
import logging
import os

from aiogram import Bot,Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from dotenv import load_dotenv
from app.handlers import router

load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN")
logging.getLogger("aiogram.dispatcher").setLevel(logging.DEBUG)
logging.getLogger("aiogram.event").setLevel(logging.DEBUG)

bot=Bot(token=BOT_TOKEN)
dp=Dispatcher(fsm_strategy=FSMStrategy.GLOBAL_USER)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__=='__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
