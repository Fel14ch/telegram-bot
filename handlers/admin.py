from aiogram import Router
from aiogram.types import CallbackQuery
from config import ADMINS
from google_sheets import delete_participant
from ui_manager import ui
from keyboards import back_kb

router = Router()

@router.callback_query(lambda c: c.data.startswith("del_"))
async def delete_user(call: CallbackQuery, bot):
    if call.from_user.id not in ADMINS:
        return

    username = call.data.replace("del_", "")
    delete_participant(username)

    await ui.clear(bot, call.message.chat.id)
    await ui.send(bot, call.message.chat.id, f"{username} удалён", reply_markup=back_kb)
