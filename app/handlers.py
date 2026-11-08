import asyncio

from aiogram import F,Router,Bot
from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery,ChatMemberOwner, ChatMemberAdministrator
from aiogram.fsm.state import StatesGroup,State
from aiogram.exceptions import TelegramBadRequest
from asyncio import gather,sleep
from datetime import datetime as dt,timedelta

from info.config import my_contact
from .useful_functions import *
import app.keyboards as kb


router = Router()

class SelectGroups(StatesGroup):
    selected_groups_for_specific_user=State()
    all_groups=State()
    distribution=State()
    distribution_set_time_and_check_data=State()
    distribution_set_message_and_check_time=State()
    find_out_the_time_zone=State()

@router.message(CommandStart())
async def cmd_start(message:Message):
    await message.answer('hi!',reply_markup=kb.start_info)

@router.message(Command('help'))
async def get_help(message:Message):
    await message.answer(':D',reply_markup=kb.start_info)

@router.message(SelectGroups.find_out_the_time_zone)
async def find_out_the_time_zone(message:Message, state:FSMContext):
    if message.text is None:
        await message.answer("Время некорректно, напишите корректное время(Формат ЧЧ[24 часовая система])")
        return
    else:
        try:
            dt.strptime(message.text.strip(), "%H")
            await calculate_time_zone_difference(message.text)
            await state.update_data(time_zone_relative_to_the_server=await calculate_time_zone_difference(message.text))
            await message.answer("Введите сообщение(по желанию с фото/видео)")
            await state.set_state(SelectGroups.distribution)
            return
        except ValueError:
            await message.answer("Время некорректно, напишите корректное время(Формат ЧЧ[24 часовая система])")
@router.callback_query(F.data=="set_distribution_data")
async def set_distribution_data(callback_query_:CallbackQuery,state: FSMContext):
    await callback_query_.answer("zxc")
    if callback_query_.message:
        await callback_query_.message.answer("Напишите дату, в которую хотите отправить сообщение(Формат ДД:ММ:ГГГГ)")
    else:
        await callback_query_.answer("Напишите дату, в которую хотите отправить сообщение(Формат ДД:ММ:ГГГГ)")
    await state.set_state(SelectGroups.distribution_set_time_and_check_data)


@router.message(SelectGroups.distribution_set_time_and_check_data)
async def distribution_set_time_and_check_data(message:Message,state: FSMContext):
    if message.text is None:
        await message.answer("Дата некорректна, напишите корректную дату(Формат ДД:ММ:ГГГГ)")
        return
    else:
        try:
            dt.strptime(message.text, "%d:%m:%Y")
            await state.update_data(distribution_data=message.text)
            await message.answer("Введите время, в которую хотите отправить сообщение(Формат ЧЧ:ММ:СС)")
            await state.set_state(SelectGroups.distribution_set_message_and_check_time)
            return
        except ValueError:
            await message.answer("Дата некорректна, напишите корректную дату(Формат ДД:ММ:ГГГГ)")

@router.message(SelectGroups.distribution_set_message_and_check_time)
async def distribution_set_message_and_check_time(message:Message,state: FSMContext):
    data=await state.get_data()
    if message.text is None:
        await message.answer("Время некорректно, напишите корректное время(Формат ЧЧ:ММ:СС)")
        return
    else:
        try:
            dt.strptime(message.text, "%H:%M:%S")
            await state.update_data(distribution_time=message.text)
            await message.answer("Введите полное количество часов на ваших часах без учета минут для определения часового пояса(Формат ЧЧ[24 часовая система])")
            if data.get("time_zone_relative_to_the_server",'')=='':
                await state.set_state(SelectGroups.find_out_the_time_zone)
            else:
                await state.set_state(SelectGroups.distribution)
            return
        except ValueError:
            await message.answer("Время некорректно, напишите корректное время(Формат ЧЧ:ММ:СС)")

@router.message(SelectGroups.distribution)
async def send_messages(message: Message, state: FSMContext, bot:Bot):
    data=await state.get_data()
    if message.from_user is None:
        await message.answer("Не удалось определить id user-а,возможно это сообщение из канала, от анонимного админа или системное.")
        return
    distribution_group_ids=await gather(*(get_choice_from_name(g) for g in data.get("selected_groups_for_specific_user",[])))
    distribution_data=data.get("distribution_data",False)
    distribution_time=data.get("distribution_time",False)
    time_zone_relative_to_the_server=data.get("time_zone_relative_to_the_server",False)
    if not(distribution_data and distribution_time and time_zone_relative_to_the_server):
        await message.answer("Произошла ошибка,попробуйте позднее",reply_markup=kb.start_info)
        return
    now=dt.now()
    target = dt.combine(dt.strptime(distribution_data,"%d:%m:%Y",).date(),
                        dt.strptime(distribution_time,"%H:%M:%S",).time())
    target -= timedelta(hours=int(time_zone_relative_to_the_server))
    delay = (target - now).total_seconds()
    await message.answer(f"Сообщение будет отправлено в {distribution_time},{distribution_data.split(':')[0]} числа {distribution_data.split(':')[1]} месяца {distribution_data.split(':')[2]} года")
    if delay > 0:
        await asyncio.sleep(delay)
    for group_id in distribution_group_ids:
        try:
            member = await bot.get_chat_member(chat_id=group_id, user_id=message.from_user.id)
            if isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
                await message.send_copy(chat_id=group_id)
                await message.answer("Сообщение успешно отправлено")
            else:
                await message.answer(f"Вы не администратор группы {group_id}")
        except TelegramBadRequest:
            await message.answer(f"Ошибка TelegramBadRequest, попробуйте подождать 15 минут или написать мне в tg:{my_contact}")
    await state.clear()
@router.message(SelectGroups.selected_groups_for_specific_user,~F.text.startswith("/"))
async def handle_choice(message: Message, state: FSMContext):
    if message.text!=stop_button_text:
        await state.update_data(selected_groups_for_specific_user=await data_extension(await state.get_data(),message.text,"selected_groups_for_specific_user",0))
        await message.answer(f"Добавлена группа {message.text or "почему то не добавлена группа"}!")
    else:
        data= await state.get_data()
        await message.answer("Группы выбраны")
        await message.answer(" ".join(str(g) for g in data.get("selected_groups_for_specific_user", [])) if data.get("selected_groups_for_specific_user", []) else "Список групп пуст",reply_markup=kb.start_info)

@router.callback_query(F.data=="choose_channels")
async def choose_channels(callback_query_:CallbackQuery,state: FSMContext):
    await callback_query_.answer(text="Success")
    data = await state.get_data()
    await state.update_data(selected_groups_for_specific_user='')
    if callback_query_.message:await callback_query_.message.answer("Выберите канал:",reply_markup=await kb.get_choose_channels_keyboard(data.get("all_groups",[])))
    else: await callback_query_.answer(text="callbackQueryProblem")
    await state.set_state(SelectGroups.selected_groups_for_specific_user)

@router.message(Command('add_channel'))
async def add_channel(message:Message,state:FSMContext):
    data = await state.get_data()
    all_groups = data.get("all_groups", [])
    if f"{message.chat.id}|{message.chat.title or ''}" not in all_groups:
        all_groups = await data_extension(data, f"{message.chat.id}|{message.chat.title or ''}","all_groups",0)
        await state.update_data(all_groups=all_groups)
        await message.answer(f"Добавлен чат ID:{message.chat.id} TITLE:{message.chat.title or "Неизвестно"}")
    else: await message.answer("Вы пытаетесь добавить один и тот же чат в базу данных несколько раз")

@router.message(Command('remove_channel'))
async def remove_channel(message:Message,state: FSMContext):
    data = await state.get_data()
    all_groups = data.get("all_groups", [])
    if f"{message.chat.id}|{message.chat.title or ''}" in all_groups:
        all_groups = await data_extension(data, f"{message.chat.id}|{message.chat.title or ''}","all_groups",1)
        await state.update_data(all_groups=all_groups)
        await message.answer(f"Удален чат ID:{message.chat.id} TITLE:{message.chat.title or "Неизвестно"}")
    else: await message.answer("В базе данных этой группы нет")