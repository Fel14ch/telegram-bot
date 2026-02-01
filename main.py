import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, register, members, admin

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(register.router)
    dp.include_router(members.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
