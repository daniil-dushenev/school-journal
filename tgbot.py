import logging

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import locale

import datetime

import main, crypto

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot('')
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


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


def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Текущие оценки📊", callback_data="marks"),
               InlineKeyboardButton("Расписание🗓", callback_data="schedule"))
    markup.add(InlineKeyboardButton("Изменить настройки🛠", callback_data="settings"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "marks":
        data = main.get_developer_info(call.from_user.id)
        login_login = data[0]
        password = crypto.decode(str(call.from_user.id), data[1], data[2], data[3])
        if data == None:
            bot.send_message(call.from_user.id, 'Ошибка🚫\nНет доступа к оценкам, проверьте введенные данные')
        else:
            mes = bot.send_message(call.from_user.id, 'Загрузка...')
            marks = main.check_marks(login_login, password)
            if marks:
                text = '📈*Оценки на ' + datetime.date.today().strftime("%d.%m.%Y") + '*📅\n'
                for key in marks:
                    if key == 'average':
                        text += '_Средний балл по всем предметам:_ *' + marks[key] + '*'
                    else:
                        text += '_' + key.capitalize() + ':_ ' + marks[key]['marks'] + ' - *' + marks[key]['average_mark'] + '*\n'
                bot.edit_message_text(chat_id=call.from_user.id, message_id=mes.message_id, text=text, parse_mode='Markdown', reply_markup=gen_markup())
                print('Отправлено')
            else:
                bot.send_message(call.from_user.id, 'Ошибка🚫\nНет доступа к оценкам, проверьте введенные данные')

    if call.data == 'schedule':
        data = main.get_developer_info(call.from_user.id)
        login_login = data[0]
        password = crypto.decode(str(call.from_user.id), data[1], data[2], data[3])
        if data == None:
            bot.send_message(call.from_user.id, 'Ошибка🚫\nНет доступа к расписанию, проверьте введенные данные.')
        else:
            mes = bot.send_message(call.from_user.id, 'Загрузка...')
            schedule = main.check_schedule(login_login, password)
            today = datetime.date.today()
            if schedule:
                text = '📈*Расписание на ' + today.strftime("%d.%m.%Y") + '*📅\n' \
                                            f'*{today.strftime("%A").title()}*\n' \

                for key in schedule:
                    if key == today.strftime("%d.%m.%Y"):
                        count = 1
                        for lesson in schedule[key]:
                            text += f'*{count}* - _' + lesson.title() + '_\n'
                            count += 1
                bot.edit_message_text(chat_id=call.from_user.id, message_id=mes.message_id, text=text,
                                      parse_mode='Markdown', reply_markup=gen_markup())
                print('Отправлено')
            else:
                bot.send_message(call.from_user.id, 'Ошибка🚫\nНет доступа к расписанию, возможно, оно еще не заполнено администратором.')


    if call.data == 'settings':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отмена❌")
        markup.add(item)
        sent = bot.send_message(call.from_user.id, 'Для авторизации в электронный журнал введите его логин:', reply_markup=markup)
        bot.register_next_step_handler(sent, login)


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
