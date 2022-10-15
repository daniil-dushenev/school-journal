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
            session.get('https://sh-open.ris61edu.ru/personal-area/#marks')  # Авторизовались на сайте

            answer = {}
            sum_average = 0     # Для подсчета общего среднего балла
            # Отсюда забираем оценки
            marks_url = 'https://sh-open.ris61edu.ru/api/MarkService/GetSummaryMarks?date=' + str(datetime.now().date())
            marks_responce = session.get(marks_url).json()

            discipline_marks = marks_responce['discipline_marks']
            for disc in discipline_marks:
                discipline = disc['discipline']     # Название предмета
                marks = [int(mark['mark']) for mark in disc['marks']]     # Оценки по предмету списком
                average = round(sum(marks) / len(marks), 2)     # Cредний балл по предмету
                sum_average += average     # Для подсчета общего среднего балла
                marks = ''.join(map(str, marks))    # Оценки по предмету строкой
                answer[discipline] = {'marks': marks, 'average_mark': str(average)}
            all_average = round(sum_average / len(answer), 2)
            answer['average'] = str(all_average)

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
                    study = [x['discipline'] for x in lessons]
                resp[i['date']] = study
            return resp
        except:
            return False


def insert_varible_into_table(id, login):  # добавление записи
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


def get_developer_info(id):  # выгрузка записи
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


def delete_user(id):  # удаление записи
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


def get_is_notifications(id):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select * from marks where id = ?"""
        info = cursor.execute(sql_select_query, (id,))
        if info.fetchone() is None:
                return False
        else:
                return True

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def insert_marks(id, marks, discipline):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_with_param = """INSERT INTO marks
                                    (id, marks, discipline)
                                    VALUES
                                    (?, ?, ?);"""

        cursor.execute(sqlite_insert_with_param, (id, marks, discipline))
        sqlite_connection.commit()

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def update_marks(id, discipline, marks):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_update_query = """UPDATE marks set marks = ? where id = ? discipline = ?"""
        cursor.execute(sql_update_query, (marks, id, discipline))
        sqlite_connection.commit()
        print("Запись успешно обновлена")
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def get_marks(id):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """select * from marks where id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()

        answer = {}
        for row in records:
            answer[row[1]] = row[2]

        cursor.close()
        return answer
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def delete_marks(id):
    try:
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sql_select_query = """DELETE from marks where id = ?"""
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

