from aiogram import Router
from aiogram.types import CallbackQuery
from google_sheets import get_all_participants
from ui_manager import ui
from keyboards import back_kb

router = Router()

@router.callback_query(lambda c: c.data == "members")
async def members(call: CallbackQuery, bot):
    await ui.clear(bot, call.message.chat.id)

    rows = get_all_participants()
    if not rows:
        await ui.send(bot, call.message.chat.id, "Список пуст", reply_markup=back_kb)
        return

    text = "\n".join(
        f"{r[0]} | {r[1]} | {r[2]}"
        for r in sorted(rows, key=lambda x: float(x[2]), reverse=True)
    )

    await ui.send(bot, call.message.chat.id, text, reply_markup=back_kb)
