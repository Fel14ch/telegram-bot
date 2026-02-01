from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="reg")],
    [InlineKeyboardButton(text="👥 Посмотреть участников", callback_data="members")],
    [InlineKeyboardButton(text="⚙ Админ панель", callback_data="admin")]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
])
