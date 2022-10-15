import schedule
import time
import telebot
from datetime import datetime
import sqlite3
import crypto, main
import logging


bot = telebot.TeleBot('5296800210:AAHCEde6JJpJZoZQpisQylxjXXDR1nMmeGI')
# logging.basicConfig(filename="/var/log/tgbot/demon_bot.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
# logging.info('Демон запущен')


def send():
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()

        sql_select_query = """select id from marks"""
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        cursor.close()
        ids = set()
        for rec in records:
            ids.add(rec[0])


    except sqlite3.Error as error:
        logging.info(error)
        cursor.close()
    finally:
        if sqlite_connection:
            sqlite_connection.close()

    for id in ids:
        data = main.get_developer_info(id)
        login = data[0]
        password = crypto.decode(str(id), data[1], data[2], data[3])

        old = main.get_marks(id)
        marks = main.check_marks(login, password)

        answer = {}
        for discipline in marks:
            if discipline != 'average':
                if discipline in old:
                    if marks[discipline]['marks'] != old[discipline]:
                        new = (marks[discipline]['marks']).replace(old[discipline], "", 1)
                        main.update_marks(id, discipline, marks[discipline]['marks'])
                        answer[discipline] = new
                else:
                    answer[discipline] = marks[discipline]['marks']
                    main.insert_marks(id, marks[discipline]['marks'], discipline)
        if answer != {}:
            text = '*Выставлены новые оценки!*\n'
            for discipline in answer:
                try:
                    mark = [int(x) for x in old[discipline]]
                    average = round((sum(mark) / len(mark)), 2)
                    delta = float(marks[discipline]["average_mark"]) - average
                    if delta >= 0:
                        delta = f"+{round(delta, 2)}"
                    else:
                        delta = f"{round(delta, 2)}"
                except:
                    delta = f'+{float(marks[discipline]["average_mark"])}'
                text += f'_{discipline.title()}_ - {answer[discipline]}, новый средний балл - *{marks[discipline]["average_mark"]} ({delta})*\n'
            bot.send_message(id, text, parse_mode='Markdown')

    # for id in ids:
    #     log.append(id)
    #     data = main.get_developer_info(id)
    #     login = data[0]
    #     password = crypto.decode(str(id), data[1], data[2], data[3])
    #     marks = main.check_marks(login, password)
    #     try:
    #         example = f'*{marks["name"]}, выставлены новые оценки!*\n'
    #         text = example
    #         marks.pop("name")
    #         for study in marks:
    #             if study != 'average':
    #                 mark = main.get_dict(id, study)
    #                 if marks[study]['marks'] == mark:
    #                     pass
    #                 else:
    #                     mark_now = marks[study]['marks']
    #                     if len(mark_now) > len(mark):
    #                         mark_new = mark_now[len(mark):]
    #                         sum = 0
    #                         for i in mark:
    #                             sum += int(i)
    #                         average = round((sum / len(mark)), 2)
    #                         delta = float(marks[study]["average_mark"]) - average
    #                         if delta >= 0:
    #                             delta = f"+{round(delta, 2)}"
    #                         else:
    #                             delta = f"{round(delta, 2)}"
    #                         text += f'_{study.title()}_ - {mark_new}, новый средний балл - *{marks[study]["average_mark"]} ({delta})*\n'
    #                         main.update_dict(id, study, mark_now)
    #         if text != example:
    #             bot.send_message(id, text, parse_mode='Markdown')
    #             logging.info('Отправлено')
    #     except:
    #         log.append(f'{id} Error')
    # logging.info(f'Check:{str(log)}')

send()
schedule.every().day.at("06:30").do(send)
schedule.every().day.at("07:50").do(send)
schedule.every().day.at("08:40").do(send)
schedule.every().day.at("09:50").do(send)
schedule.every().day.at("10:40").do(send)
schedule.every().day.at("11:40").do(send)
schedule.every().day.at("13:15").do(send)
schedule.every().day.at("16:00").do(send)
schedule.every().day.at("17:30").do(send)
schedule.every().day.at("19:00").do(send)

while True:
    schedule.run_pending()
    time.sleep(60)
