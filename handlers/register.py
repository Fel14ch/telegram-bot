from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import RaidReg
from validators import is_valid_bm
from google_sheets import upsert_participant
from ui_manager import ui

router = Router()

@router.callback_query(lambda c: c.data == "reg")
async def start_reg(call: CallbackQuery, state: FSMContext, bot):
    await ui.clear(bot, call.message.chat.id)
    await ui.send(bot, call.message.chat.id, "Введите никнейм:")
    await state.set_state(RaidReg.nickname)

@router.message(RaidReg.nickname)
async def nick(message: Message, state: FSMContext, bot):
    await state.update_data(nickname=message.text)
    await ui.auto_delete(bot, message.chat.id, message.message_id, 30)
    await ui.send(bot, message.chat.id, "Введите ОБЩИЙ БМ:")
    await state.set_state(RaidReg.total_bm)

@router.message(RaidReg.total_bm)
async def total_bm(message: Message, state: FSMContext, bot):
    if not is_valid_bm(message.text):
        warn = await ui.send(bot, message.chat.id, "❌ Только цифры и знак \".\"")
        await ui.auto_delete(bot, message.chat.id, warn.message_id, 5)
        return

    await state.update_data(total_bm=message.text)
    await ui.auto_delete(bot, message.chat.id, message.message_id, 30)
    await ui.send(bot, message.chat.id, "Введите БМ 1 отряда:")
    await state.set_state(RaidReg.squad_bm)

@router.message(RaidReg.squad_bm)
async def finish(message: Message, state: FSMContext, bot):
    if not is_valid_bm(message.text):
        warn = await ui.send(bot, message.chat.id, "❌ Только цифры и знак \".\"")
        await ui.auto_delete(bot, message.chat.id, warn.message_id, 5)
        return

    data = await state.get_data()
    username = f"@{message.from_user.username}" if message.from_user.username else "—"

    upsert_participant(
        username,
        data["nickname"],
        data["total_bm"],
        message.text
    )

    msg = await ui.send(
        bot,
        message.chat.id,
        f"🆕 Новый участник рейда:\n"
        f"{username} | {data['nickname']} | {data['total_bm']}"
    )

    await ui.auto_delete(bot, message.chat.id, msg.message_id, 60)
    await state.clear()
