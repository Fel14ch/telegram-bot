from aiogram import Router
from aiogram.types import Message, CallbackQuery
from keyboards import main_kb
from ui_manager import ui

router = Router()

@router.message(commands=["start"])
async def start_cmd(message: Message, bot):
    await ui.clear(bot, message.chat.id)
    await ui.send(bot, message.chat.id, "👋 Добро пожаловать!", reply_markup=main_kb)

@router.callback_query(lambda c: c.data == "back")
async def back(call: CallbackQuery, bot):
    await ui.clear(bot, call.message.chat.id)
    await ui.send(bot, call.message.chat.id, "Главное меню", reply_markup=main_kb)
