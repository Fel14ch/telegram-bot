import os
import sqlite3
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# 🔽 ВОТ СЮДА ВСТАВЛЯЕШЬ ДАННЫЕ ГРУППЫ
GROUP_ID = int(os.getenv("GROUP_ID"))     # например -1001234567890
TOPIC_ID = int(os.getenv("TOPIC_ID"))     # например 42

DB_NAME = "participants.db"
# ======================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ====== БАЗА ======
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS participants (
    user_id INTEGER PRIMARY KEY,
    tg_name TEXT,
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

# ====== КНОПКИ ======
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зарегистрироваться на рейд")],
        [KeyboardButton(text="Посмотреть участников")],
        [KeyboardButton(text="Админ панель")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Удалить участника")],
        [KeyboardButton(text="Удалить всех участников")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

# ====== START ======
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать 👋", reply_markup=menu_kb)

# ====== РЕГИСТРАЦИЯ ======
@dp.message(F.text == "Зарегистрироваться на рейд")
async def reg_start(message: Message, state: FSMContext):
    await message.answer("Введите никнейм из игры:")
    await state.set_state(Register.nickname)

@dp.message(Register.nickname)
async def reg_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer("Введите БМ отряда:")
    await state.set_state(Register.power)

@dp.message(Register.power)
async def reg_power(message: Message, state: FSMContext):
    data = await state.get_data()

    cur.execute("""
    INSERT OR REPLACE INTO participants
    VALUES (?, ?, ?, ?, ?)
    """, (
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
        data["nickname"],
        message.text
    ))
    conn.commit()

    # 🔔 ПУБЛИКАЦИЯ В ТЕМУ ГРУППЫ
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

    await message.answer("✅ Спасибо за регистрацию!", reply_markup=menu_kb)
    await state.clear()

# ====== ПРОСМОТР ======
@dp.message(F.text == "Посмотреть участников")
async def show_participants(message: Message):
    cur.execute("SELECT tg_name, username, nickname, power FROM participants")
    rows = cur.fetchall()

    if not rows:
        await message.answer("Список пуст")
        return

    text = ""
    for r in rows:
        text += f"{r[0]} | @{r[1]} | {r[2]} | {r[3]}\n"

    await message.answer(text)

# ====== АДМИН ПАНЕЛЬ ======
@dp.message(F.text == "Админ панель")
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return

    await message.answer("Админ панель", reply_markup=admin_kb)

# ====== УДАЛЕНИЕ ======
@dp.message(F.text == "Удалить всех участников")
async def delete_all(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cur.execute("DELETE FROM participants")
    conn.commit()
    await message.answer("🗑 Все участники удалены", reply_markup=admin_kb)

@dp.message(F.text == "Удалить участника")
async def delete_one_prompt(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Введите никнейм участника:")
    await state.set_state(AdminDelete.waiting_nickname)

@dp.message(AdminDelete.waiting_nickname)
async def delete_one(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    cur.execute("DELETE FROM participants WHERE nickname = ?", (message.text,))
    conn.commit()

    await message.answer("✅ Участник удалён", reply_markup=admin_kb)
    await state.clear()

# ====== НАЗАД ======
@dp.message(F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=menu_kb)

# ====== RUN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
