import logging

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import locale

import datetime

import main, crypto

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot('5296800210:AAHCEde6JJpJZoZQpisQylxjXXDR1nMmeGI')
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def send_marks(id):
    data = main.get_developer_info(id)
    login_login = data[0]
    password = crypto.decode(str(id), data[1], data[2], data[3])
    if data == None:
        bot.send_message(id, 'Ошибка🚫\nНет доступа к оценкам, проверьте введенные данные')
    else:
        mes = bot.send_message(id, 'Загрузка...')
        marks = main.check_marks(login_login, password)
        if marks:
            text = '📈*Оценки на ' + datetime.date.today().strftime("%d.%m.%Y") + '*📅\n'
            for key in marks:
                if key == 'average':
                    text += '_Средний балл по всем предметам:_ *' + marks[key] + '*'
                else:
                    text += '_' + key.capitalize() + ':_ ' + marks[key]['marks'] + ' - *' + marks[key]['average_mark'] + '*\n'
            bot.edit_message_text(chat_id=id, message_id=mes.message_id, text=text, parse_mode='Markdown', reply_markup=gen_markup())
            print('Отправлено')
        else:
            bot.send_message(id, 'Ошибка🚫\nНет доступа к оценкам, проверьте введенные данные')


def send_schedule_day(id):
    data = main.get_developer_info(id)
    login_login = data[0]
    password = crypto.decode(str(id), data[1], data[2], data[3])
    if data == None:
        bot.send_message(id, 'Ошибка🚫\nНет доступа к расписанию, проверьте введенные данные.')
    else:
        mes = bot.send_message(id, 'Загрузка...')
        schedule = main.check_schedule(login_login, password)
        today = datetime.date.today()
        if schedule:
            text = '📈*Расписание на ' + today.strftime("%d.%m.%Y") + '*📅\n\n' \
                                        f'*{today.strftime("%A").title()}*\n' \

            for key in schedule:
                if key == today.strftime("%Y-%m-%d"):
                    count = 1
                    if schedule[key] != None:
                        for lesson in schedule[key]:
                            text += f'*{count}* - _' + lesson.title() + '_\n'
                            count += 1
                    else:
                        text += 'Уроков нет'
            bot.edit_message_text(chat_id=id, message_id=mes.message_id, text=text,
                                  parse_mode='Markdown', reply_markup=gen_markup())
            print('Отправлено')
        else:
            bot.send_message(id, 'Ошибка🚫\nНет доступа к расписанию, возможно, оно еще не заполнено администратором.')


def send_schedule_week(id):
    data = main.get_developer_info(id)
    login_login = data[0]
    password = crypto.decode(str(id), data[1], data[2], data[3])
    if data == None:
        bot.send_message(id, 'Ошибка🚫\nНет доступа к расписанию, проверьте введенные данные.')
    else:
        mes = bot.send_message(id, 'Загрузка...')
        schedule = main.check_schedule(login_login, password)
        today = datetime.date.today()
        if schedule:
            text = '📈*Расписание на ' + today.strftime("%d.%m.%Y") + '*📅\n'

            for key in schedule:
                today = datetime.datetime.strptime(key, '%Y-%m-%d').strftime("%A")

                text += f'\n*{today.title()}*\n'
                count = 1
                if schedule[key] != None:
                    for lesson in schedule[key]:
                        text += f'*{count}* - _' + lesson.title() + '_\n'
                        count += 1
                else:
                    text += 'Уроков нет\n'
            bot.edit_message_text(chat_id=id, message_id=mes.message_id, text=text,
                                  parse_mode='Markdown', reply_markup=gen_markup())
            print('Отправлено')
        else:
            bot.send_message(id, 'Ошибка🚫\nНет доступа к расписанию, возможно, оно еще не заполнено администратором.')



@bot.message_handler(commands=['start'])
def start(msg):
    try:
        main.get_developer_info(msg.chat.id)[0]
        bot.send_message(msg.chat.id, 'Привет, что хочешь сделать?', reply_markup=gen_markup())

    except:
        bot.send_message(msg.chat.id, 'Привет! Это бот, который помогает следить за твоими оценками. Для начала работы нужно предоставить данные от входа в свой электронный журнал.')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отмена❌")
        markup.add(item)
        sent = bot.send_message(msg.chat.id, 'Для авторизации в электронный журнал введите его логин:',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, login)


@bot.message_handler(commands=['menu'])
def menu(msg):
    bot.send_message(msg.chat.id, 'Привет, что хочешь сделать?', reply_markup=gen_markup())


@bot.message_handler(commands=['marks'])
def marks_com(msg):
    send_marks(msg.from_user.id)


@bot.message_handler(commands=['schedule'])
def marks_com(msg):
    send_schedule_day(msg.from_user.id)


@bot.message_handler(commands=['schedule_week'])
def marks_com(msg):
    send_schedule_week(msg.from_user.id)


@bot.message_handler(commands=['settings'])
def settings(msg):
    is_notifications = main.get_is_notifications(msg.from_user.id)
    bot.send_message(chat_id=msg.from_user.id, text='Какие настройки вы хотите изменить?', reply_markup=settings_markup(is_notifications))



def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Текущие оценки📊", callback_data="marks"))
    markup.add(InlineKeyboardButton("Расписание на день🗓", callback_data="schedule_day"))
    markup.add(InlineKeyboardButton("Расписание на неделю🗓", callback_data="schedule_week"))
    markup.add(InlineKeyboardButton("Изменить настройки🛠", callback_data="settings"))
    return markup


def settings_markup(is_notifications):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Изменить логин и пароль", callback_data="set_login"))

    if is_notifications:
        s = 'Выключить'
        command = 'off_nottif'
    else:
        s = 'Включить'
        command = 'on_nottif'
    markup.add(InlineKeyboardButton(s + " уведмоления об оценках", callback_data=command))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "marks":
        send_marks(call.from_user.id)

    if call.data == 'schedule_day':
        send_schedule_day(call.from_user.id)

    if call.data == 'schedule_week':
        send_schedule_week(call.from_user.id)

    if call.data == 'settings':
        is_notifications = main.get_is_notifications(call.from_user.id)
        bot.send_message(chat_id=call.from_user.id, text='Какие настройки вы хотите изменить?', reply_markup=settings_markup(is_notifications))

    if call.data == 'set_login':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отмена❌")
        markup.add(item)
        sent = bot.send_message(call.from_user.id, 'Для авторизации в электронный журнал введите его логин:',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, login)

    if call.data == 'on_nottif':
        mes = bot.send_message(call.from_user.id, 'Секундочку...')
        data = main.get_developer_info(call.from_user.id)
        login = data[0]
        password = crypto.decode(str(call.from_user.id), data[1], data[2], data[3])

        marks_data = main.check_marks(login, password)
        for discipline in marks_data:
            if discipline != 'average':
                marks = marks_data[discipline]['marks']
                main.insert_marks(call.from_user.id, marks, discipline)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=mes.message_id, text='Уведомления об оценках успешно включены!', reply_markup=gen_markup())

    if call.data == 'off_nottif':
        main.delete_marks(call.from_user.id)
        bot.send_message(call.from_user.id, 'Уведомления об оценках успешно выключены!', reply_markup=gen_markup())


def login(msg):
    if msg.text == 'Отмена❌':
        bot.send_message(msg.chat.id, 'Отмена операции..', reply_markup=gen_markup())
    else:
        if main.get_developer_info(msg.chat.id) == None:
            main.insert_varible_into_table(msg.chat.id, msg.text)
        else:
            main.update_sqlite_table(msg.chat.id, msg.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отмена❌")
        markup.add(item)
        sent = bot.send_message(msg.chat.id, 'Отлично! Теперь введите пароль от журнала:', reply_markup=markup)
        bot.register_next_step_handler(sent, password)


def password(msg):
    if msg.text == 'Отмена❌':
        bot.send_message(msg.chat.id, 'Отмена операции..', reply_markup=gen_markup())
    else:
        main.update_password(msg.chat.id, msg.text)
        bot.send_message(msg.chat.id, 'Данные успешно получены!', reply_markup=gen_markup())





print('Бот запущен')

bot.infinity_polling()
