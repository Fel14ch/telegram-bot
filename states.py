from aiogram.fsm.state import StatesGroup, State

class RaidReg(StatesGroup):
    nickname = State()
    total_bm = State()
    squad_bm = State()
