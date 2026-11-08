from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def build_back_keyboard(callback_data: str, text: str = "Назад") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    return builder.as_markup()