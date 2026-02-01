import os
import sqlite3
import asyncio
import re

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

GROUP_ID = int(os.getenv("GROUP_ID"))  # например -1003770135976
TOPIC_ID = int(os.getenv("TOPIC_ID"))  # например 8

DB_NAME = "participants.db"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ====== БАЗА ======
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS participants (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    nickname TEXT,
    power TEXT
)
""")
conn.commit()

# ====== FSM ======
class Register(StatesGroup):
    nickname = State()
    power = State()

class AdminDelete(StatesGroup):
    waiting_nickname = State()

# ====== INLINE КНОПКИ ======
menu_kb_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Зарегистрироваться на рейд", callback_data="reg_raid")],
        [InlineKeyboardButton(text="Посмотреть участников", callback_data="show_participants")],
        [InlineKeyboardButton(text="Админ панель", callback_data="admin_panel")]
    ]
)

admin_kb_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Удалить участника", callback_data="del_one")],
        [InlineKeyboardButton(text="Удалить всех участников", callback_data="del_all")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ]
)

# ====== START ======
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать 👋", reply_markup=menu_kb_inline)

# ====== CALLBACK QUERY ======
@dp.callback_query(F.data == "reg_raid")
async def reg_raid_callback(call: CallbackQuery, state: FSMContext):
    msg = await call.message.answer("Введите никнейм из игры:")
    await state.update_data(prompt_message_id=msg.message_id)
    await state.set_state(Register.nickname)

@dp.callback_query(F.data == "show_participants")
async def show_participants_callback(call: CallbackQuery):
    cur.execute("SELECT username, nickname, power FROM participants ORDER BY CAST(power AS REAL) DESC")
    rows = cur.fetchall()
    if not rows:
        await call.message.answer("Список пуст")
        return
    text = ""
    for r in rows:
        text += f"@{r[0]} | {r[1]} | {r[2]}\n"
    await call.message.answer(text)

@dp.callback_query(F.data == "admin_panel")
async def admin_panel_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if call.from_user.id != ADMIN_ID:
        await call.message.answer("⛔ Нет доступа")
        return
    await call.message.answer("Админ панель", reply_markup=admin_kb_inline)

@dp.callback_query(F.data == "del_all")
async def del_all_callback(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    cur.execute("DELETE FROM participants")
    conn.commit()
    await call.message.answer("🗑 Все участники удалены", reply_markup=admin_kb_inline)

@dp.callback_query(F.data == "del_one")
async def del_one_prompt_callback(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    msg = await call.message.answer("Введите никнейм участника:")
    await state.update_data(prompt_message_id=msg.message_id)
    await state.set_state(AdminDelete.waiting_nickname)

@dp.callback_query(F.data == "back")
async def back_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Главное меню", reply_markup=menu_kb_inline)

# ====== РЕГИСТРАЦИЯ ======
@dp.message(Register.nickname)
async def reg_nickname(message: Message, state: FSMContext):
    data = await state.get_data()
    # удаляем подсказку
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("prompt_message_id"))
    except:
        pass
    await state.update_data(nickname=message.text)
    msg = await message.answer("Введите БМ отряда (только цифры и точка):")
    await state.update_data(prompt_message_id=msg.message_id)
    await state.set_state(Register.power)

@dp.message(Register.power)
async def reg_power(message: Message, state: FSMContext):
    data = await state.get_data()

    # Удаляем старую подсказку "Введите БМ"
    if data.get("prompt_message_id"):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=data["prompt_message_id"])
        except:
            pass

    # Удаляем старое предупреждение ❌ если было
    if data.get("warning_msg_id"):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=data["warning_msg_id"])
        except:
            pass

    # Проверка БМ: только цифры и точка
    if not re.fullmatch(r"[\d.]+", message.text):
        warning_msg = await message.answer('❌ Только цифры и знак "."')
        await state.update_data(warning_msg_id=warning_msg.message_id)
        return

    # сохраняем участника
    cur.execute("""
    INSERT OR REPLACE INTO participants (user_id, username, nickname, power)
    VALUES (?, ?, ?, ?)
    """, (
        message.from_user.id,
        message.from_user.username,
        data["nickname"],
        message.text
    ))
    conn.commit()

    # 🔔 Публикация в тему группы
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_ID,
            text=(
                "🆕 Новый участник рейда:\n"
                f"👤 Ник: {data['nickname']}\n"
                f"⚔️ БМ: {message.text}\n"
                f"📎 TG: @{message.from_user.username}"
            )
        )
    except Exception as e:
        print("Ошибка отправки в группу:", e)

    await message.answer("✅ Спасибо за регистрацию!", reply_markup=menu_kb_inline)
    await state.clear()

# ====== УДАЛЕНИЕ УЧАСТНИКА ======
@dp.message(AdminDelete.waiting_nickname)
async def del_one(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("prompt_message_id"))
    except:
        pass
    cur.execute("DELETE FROM participants WHERE nickname = ?", (message.text,))
    conn.commit()
    await message.answer("✅ Участник удалён", reply_markup=admin_kb_inline)
    await state.clear()

# ====== RUN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
