from aiogram.types import (ReplyKeyboardMarkup,KeyboardButton,
                           InlineKeyboardMarkup,InlineKeyboardButton)


start_info=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Настроить рассылку",callback_data="set_distribution_data"),
                                                  InlineKeyboardButton(text="Выбрать каналы",callback_data="choose_channels")]])

settings=InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='YouTube',url='https://www.youtube.com/c/YouTube'),
     InlineKeyboardButton(text='VK',url='https://vk.com/@VK')]
])

