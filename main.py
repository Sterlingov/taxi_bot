import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from random_car import random_car
from aiogram.dispatcher import FSMContext
import sqlite3
bot = Bot("5508971823:AAGRUPwVbkiEEu_BSl-mzTN0IPTpf8S59iM")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

con = sqlite3.connect("database.db")
cur = con.cursor()


class UserId:
    id = None


class UpdateForm(StatesGroup):
    name = State()
    number_of_phone = State()
    location = State()
    comment = State()
    admin_comment = State()


class Form(StatesGroup):
    number_of_phone = State()
    name = State()


async def menu(m: types.Message):
    btn1 = InlineKeyboardButton('Личный кабинет', callback_data='button_1')
    btn2 = InlineKeyboardButton('Бонусная программа', callback_data='button_2')
    btn3 = InlineKeyboardButton('Заказать такси', callback_data='button_3')
    kb1 = InlineKeyboardMarkup(resize_keyboard=True).add(btn3).row(btn1, btn2)
    await bot.send_message(m.from_user.id, "Выберите кнопку", reply_markup=kb1)


@dp.message_handler(state=Form.number_of_phone)
async def number_of_phone_func(m: types.Message, state: FSMContext):
    if len(m.text) != 11 or not m.text.isnumeric() or m.text[0] != "7":
        await bot.send_message(m.from_user.id, "Введите номер по примеру: 79437893421")
        return
    await state.update_data(number_of_phone=m.text)
    data = await state.get_data()
    await bot.send_message(m.from_user.id, f"Регистрация завершена! \nНомер телефона"
                                           f" - {data['number_of_phone']}\nИмя - {data['name']}")
    cur.execute(f"""INSERT INTO user VALUES ('{m.from_user.id}', '{data['name']}', '{int(data['number_of_phone'])}', 
    '0')""")
    await state.finish()
    con.commit()
    await menu(m)


@dp.message_handler(state=Form.name)
async def name_func(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await bot.send_message(m.from_user.id, "Отлично! Теперь напиши свой номер телефона. Пример номера - 79437893421")
    await Form.number_of_phone.set()


@dp.message_handler(commands=["start"])
async def start(m: types.Message):
    info = cur.execute('SELECT * FROM user WHERE userid=?', (m.from_user.id,))
    info_from_bd = info.fetchall()
    if len(info_from_bd) == 0:
        await bot.send_message(m.from_user.id, "Привет, я бот сервиса 'Такси, сир'. С помощью меня ты"
                                               " сможешь вызвать такси"
                                               " в любую точку России прямо из Телеграмм")
        await bot.send_message(m.from_user.id, "Напиши мне, как к тебе обращаться?")
        await Form.name.set()
    else:
        await bot.send_message(m.from_user.id, f"Приветствую тебя, {info_from_bd[0][1]}!")
        await menu(m)


@dp.callback_query_handler(text="go_back")
async def go_back(m: types.Message):
    await menu(m)


@dp.callback_query_handler(text="button_1")
async def new_data(m: types.Message):
    info = cur.execute('SELECT * FROM user WHERE userid=?', (m.from_user.id,))
    info_from_bd = info.fetchall()
    btn1 = types.InlineKeyboardButton("Изменить имя", callback_data="new_name")
    btn2 = types.InlineKeyboardButton("Изменить номер телефона", callback_data="new_phone_number")
    btn3 = types.InlineKeyboardButton("Назад", callback_data="go_back")
    kb = types.InlineKeyboardMarkup(resize_keyboard=True).row(btn1, btn2).add(btn3)
    await bot.send_message(m.from_user.id, f"Ваше имя: {info_from_bd[0][1]}\nВаш номер телефона: {info_from_bd[0][2]}"
                                           f"\nКоличество поездок: {info_from_bd[0][3]}", reply_markup=kb)


@dp.callback_query_handler(text="new_name")
async def new_name(m: types.Message):
    await bot.send_message(m.from_user.id, "Введите новое имя!")
    await UpdateForm.name.set()


@dp.message_handler(state=UpdateForm.name)
async def new_name_set(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    data = await state.get_data()
    cur.execute(f"""
    UPDATE user
    SET name = '{data['name']}'
    WHERE userid = '{m.from_user.id}'
    """)
    con.commit()
    await state.finish()
    await bot.send_message(m.from_user.id, "Имя успешно изменено!")
    await menu(m)


@dp.callback_query_handler(text="new_phone_number")
async def new_phone_number(m: types.Message):
    await bot.send_message(m.from_user.id, "Введите новый номер телефона!")
    await UpdateForm.number_of_phone.set()


@dp.message_handler(state=UpdateForm.number_of_phone)
async def new_name_set(m: types.Message, state: FSMContext):
    if len(m.text) != 11 or not m.text.isnumeric() or m.text[0] != "7":
        await bot.send_message(m.from_user.id, "Введите номер по примеру: 79437893421")
        return
    await state.update_data(number_of_phone=m.text)
    data = await state.get_data()
    cur.execute(f"""
    UPDATE user
    SET phone_number = '{data['number_of_phone']}'
    WHERE userid = '{m.from_user.id}'
    """)
    con.commit()
    await state.finish()
    await bot.send_message(m.from_user.id, "Номер телефона успешно изменен!")
    await menu(m)


@dp.callback_query_handler(text="button_2")
async def bonus(m: types.Message):
    info = cur.execute('SELECT * FROM user WHERE userid=?', (m.from_user.id,))
    info_from_bd = info.fetchall()
    btn = types.InlineKeyboardButton("Назад", callback_data="go_back")
    kb = InlineKeyboardMarkup().add(btn)
    await bot.send_message(m.from_user.id, f"Количество поездок: {info_from_bd[0][3]}\n\nПри накоплении 5 поездок будет"
                                           f" автоматически применен бонус - скидкa в 30% на заказ такси",
                           reply_markup=kb)


@dp.callback_query_handler(text="button_3")
async def get_taxi(m: types.Message):
    btn = KeyboardButton("(Без комментария)")
    await bot.send_message(m.from_user.id, "Оставьте комментарий к запросу или нажмите на кнопку",
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(btn))
    await UpdateForm.comment.set()


@dp.message_handler(state=UpdateForm.comment)
async def comment(m: types.Message, state: FSMContext):
    await state.update_data(comment=m.text)
    await bot.send_message(m.from_user.id, "Введите свое местоположение. Например: Пушкинская, 7, к3",
                           reply_markup=ReplyKeyboardRemove())
    await UpdateForm.location.set()


@dp.message_handler(state=UpdateForm.location)
async def get_location(m: types.Message, state: FSMContext):
    info = cur.execute('SELECT * FROM user WHERE userid=?', (m.from_user.id,))
    info_from_bd = info.fetchall()
    await state.update_data(location=m.text)
    data = await state.get_data()
    await bot.send_message(m.from_user.id, "Ваш запрос проверяется Администратором!")
    btn1 = types.InlineKeyboardButton("Принять", callback_data="accept_order")
    btn2 = types.InlineKeyboardButton("Отклонить", callback_data="deny_order")
    kb = types.InlineKeyboardMarkup().row(btn1, btn2)
    UserId.id = m.from_user.id
    await bot.send_message(1963719858, f"Заказ от {info_from_bd[0][1]}!\n\nНомер телефона: {info_from_bd[0][2]}\n\n"
                                       f"Адрес: {data['location']}\n\nПоездок: {info_from_bd[0][3]}\n\nКомментарий: "
                                       f"{data['comment']}", reply_markup=kb)
    await state.finish()


@dp.callback_query_handler(text="accept_order")
async def accept_order(c: types.CallbackQuery):
    await bot.send_message(UserId.id, "Ваш запрос приняли!")
    btn = types.InlineKeyboardButton("Назад", callback_data="go_back")
    kb = InlineKeyboardMarkup().add(btn)
    await bot.send_message(UserId.id, f"Машина: {random_car()}", reply_markup=kb)
    await bot.send_message(c.from_user.id, "Вы одобрили заказ!", reply_markup=ReplyKeyboardRemove())
    cur.execute(f"""
        UPDATE user
        SET travels = travels + 1
        WHERE userid = '{UserId.id}'
        """)
    con.commit()
    await c.message.delete()


@dp.callback_query_handler(text="deny_order")
async def deny_order_comment(c: types.CallbackQuery):
    await bot.send_message(c.from_user.id, "Напишите причину отклонения заказа")
    await UpdateForm.admin_comment.set()
    await c.message.delete()


@dp.message_handler(state=UpdateForm.admin_comment)
async def deny_order(m: types.Message, state: FSMContext):
    await state.update_data(admin_comment=m.text)
    data = await state.get_data()
    btn = types.InlineKeyboardButton("Назад", callback_data="go_back")
    kb = InlineKeyboardMarkup().add(btn)
    await bot.send_message(m.from_user.id, f"Вы отменили заказ по причине: {data['admin_comment']}")
    await bot.send_message(UserId.id, f"Ваш запрос был отклонен!\nПричина: {data['admin_comment']}", reply_markup=kb)
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
