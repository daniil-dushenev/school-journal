import requests
import json
from datetime import datetime
import pytz
import sqlite3
import crypto


def check_marks(login, password):
    with requests.Session() as session:
        try:
            url = 'https://sh-open.ris61edu.ru/auth/login'

            data = {
                'login_login': login,
                'login_password': password
            }

            r = session.post(url, data=data)
            print(r)
            session.get('https://sh-open.ris61edu.ru/personal-area/#marks')

            marks_url = 'https://sh-open.ris61edu.ru/api/MarkService/GetSummaryMarks?date=' + str(datetime.now().date())
            average = session.get('http://sh-open.ris61edu.ru/api/ProfileService/GetPersonData').text
            marks_responce = session.get(marks_url).text
            marks = dict(json.loads(marks_responce))
            average = dict(json.loads(average))
            marks = marks['discipline_marks']
            answer = {}
            for disc in marks:
                disc['discipline']
                d_marks = ''
                for mark in disc['marks']:
                    d_marks += str(mark['mark'])
                    answer[disc['discipline']] = {'marks': d_marks, 'average_mark': disc['average_mark']}
            av_mark = average['indicators']
            for i in av_mark:
                if i['name'] == 'Общий средний балл':
                    av_mark = i['value']
            answer['average'] = av_mark
            # total_url = 'https://sh-open.ris61edu.ru/api/MarkService/GetTotalMarks?childPersonId=123456'
            # total_res = session.get(total_url).json()
            # periods = total_res['subperiods']
            # total_marks = total_res['discipline_marks']
            # answer['total_marks'] = []
            # total_periods = []
            # for i in total_marks:
            #     periods_list = []
            #     period_marks = i["period_marks"]
            #     for x in period_marks:
            #         for y in periods:
            #             if y['code'] == x['subperiod_code']:
            #                 period = y['name']
            #                 if period not in total_periods:
            #                     total_periods.append(period)
            #         periods_list.append({period: x['mark']})
            #     answer['total_marks'].append({i['discipline']: periods_list})
            # answer['periods'] = total_periods
            return answer
        except:
            return False


def check_schedule(login, password):
    with requests.Session() as session:
        try:
            url = 'https://sh-open.ris61edu.ru/auth/login'

            data = {
                'login_login': login,
                'login_password': password
            }

            r = session.post(url, data=data)
            session.get('https://sh-open.ris61edu.ru/personal-area/#marks')
            url = 'https://sh-open.ris61edu.ru/api/ScheduleService/GetWeekSchedule?date=' + str(datetime.now().date())
            res = session.get(url).json()
            days = res['days']
            resp = {}
            for i in days:
                try:
                    if i['is_weekend']:
                        study = None
                except:
                    lessons = i['lessons']
                    study = []
                    for x in lessons:
                        study.append(x['discipline'])
                resp[i['date']] = study
            return resp
        except:
            return False

# print(check_schedule('РК53_ДушеневДан', 'XyA9qpA4'))

def insert_varible_into_table(id, login):  #добавление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_with_param = """INSERT INTO profiles
                                    (id, login)
                                    VALUES
                                    (?, ?);"""

        cursor.execute(sqlite_insert_with_param, (id, login))
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу profiles")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_developer_info(id):  #выгрузка записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select * from profiles where id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        print("Вывод Telegram ", id)
        for row in records:
            # print("Password:", row[2])
            return [row[1], row[2], row[3], row[4]]

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def delete_user(id):  #удаление записи
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """DELETE from profiles where id = ?"""
        cursor.execute(sql_select_query, (id,))
        sqlite_connection.commit()
        print("Запись успешно удалена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def update_sqlite_table(id, login):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_update_query = """UPDATE profiles set login = ? where id = ?"""
        cursor.execute(sql_update_query, (login, id))
        sqlite_connection.commit()
        print("Запись успешно обновлена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def update_password(id, password):
    try:
        dict = crypto.encode(str(id), password)
        nonce = dict['nonce']
        ciphertext = dict['ciphertext']
        tag = dict['tag']

        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_update_query = """UPDATE profiles set nonce = ?,
                            ciphertext = ?,
                            tag = ? where id = ?"""
        cursor.execute(sql_update_query, (nonce, ciphertext, tag, id))
        sqlite_connection.commit()
        print("Запись успешно обновлена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


# sqlite_connection = sqlite3.connect('data.db')
# sqlite_create_table_query = '''CREATE TABLE profiles(
#                             id TEXT NOT NULL,
#                             login TEXT NOT NULL,
#                             nonce BLOB,
#                             ciphertext BLOB,
#                             tag BLOB);'''
#
# cursor = sqlite_connection.cursor()
# print("База данных подключена к SQLite")
# cursor.execute(sqlite_create_table_query)
# sqlite_connection.commit()
# print("Таблица SQLite создана")
#
# cursor.close()


#
# sqlite_connection = sqlite3.connect('data.db')
# sqlite_create_table_query = '''DROP TABLE profiles;'''
#
# cursor = sqlite_connection.cursor()
# print("База данных подключена к SQLite")
# cursor.execute(sqlite_create_table_query)
# sqlite_connection.commit()
# print("Таблица SQLite создана")
#
# cursor.close()

#
# py

# msc = pytz.timezone('Africa/Kampala')
# print(datetime.now(tz=msc).strftime('%H:%M %d.%m.%Y'))
#

# delete_user('100499943')
# sqlite_connection = sqlite3.connect('data.db')
# cursor = sqlite_connection.cursor()
# print("Подключен к SQLite")
#
# sql_select_query = """select * from profiles where id = ?"""
# cursor.execute(sql_select_query, (id,))
# records = cursor.fetchall()
# print("Вывод Telegram ", id)
# print(records)
# for row in records:
#     print("ID:", row[0])
#     print("Login:", row[1])
#     # print("Password:", row[2])
#     return [row[1], row[2]]

# print(get_developer_info('100499943'))
# print(update_sqlite_table('100499943', 'XyA9qpA4'))
# print(get_developer_info('100499943'))
# insert_varible_into_table('1132453574', 'PK53_ПетроваНС', 'п09092005')
# print(data)
# print(check_marks('РК53_ДушеневДан', 'XyA9qpA4'))         # 'РК53_Бульская123', 'CJhRx5sL'
