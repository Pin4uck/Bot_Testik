""" модуль sqlite3 предназначен для работы с базами данных"""
import sqlite3
import os
import logging
import pb


DB_CONN = None
CACHE_AGE = int(os.getenv('TGBOT_CACHE_MAXAGE', '3600'))
LOG_LEVEL = os.getenv('TGBOT_LOGLEVEL', 'WARNING')
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=LOG_LEVEL
)


def get_currency_rate(currency_name):
    """Данная функция возвращает обновленное значени валюты,
    либо выполняет функцию get_currency_rate2()"""
    try:
        return read_cached_currency_rate(currency_name, CACHE_AGE)
    except:
        return get_currency_rate2(currency_name)


def get_currency_rate2(currency_name):
    """Данная функция возвращает обновленное значени валюты,
    либо выполняет функцию read_cached_currency_rate() -
    которая выводит необновленное значение с базы данных"""
    try:
        rate = pb.get_exchanges(currency_name)
        store_currency_rate(currency_name, rate)
        logging.debug('updated value from site')
        return rate
    except:
        return read_cached_currency_rate(currency_name)


def dbcursor():
    """Данная функция создает таблицу, если она не создана.
    Также соединяется с базой данных и создает объект cursor()"""
    global DB_CONN
    if not DB_CONN:
        DB_CONN = sqlite3.connect('currency.db')
        DB_CONN.execute('''CREATE TABLE IF NOT EXISTS ccy (
                            Abbreviation TEXT NOT NULL PRIMARY KEY,
                            Rate FLOAT NOT NULL,
                            last_updated timestamp default (strftime('%s', 'now')))''')
    return DB_CONN.cursor(), DB_CONN


def read_cached_currency_rate(currency_name, cache = None):
    """Данная функция выводит с базы данных необходимое значение"""
    curs, _ = dbcursor()
    if cache is None:
        curs.execute(f'''SELECT Rate FROM ccy
                        WHERE Abbreviation = '{currency_name}' ''')
        logging.debug('not updated value from base')
        value = curs.fetchall()
    else:
        curs.execute(f'''SELECT Rate FROM ccy
                        WHERE Abbreviation = '{currency_name}' and 
                        (strftime('%s') - last_updated <= {cache})''')
        value = curs.fetchall()
        if value:
            logging.debug('updated value from base')
    if value:
        return value[0][0]
    raise LookupError(currency_name)


def store_currency_rate(currency_name, rate):
    """Данная функция вночит в базу данных необходимое значение"""
    curs, conn = dbcursor()
    curs.execute(f'''INSERT INTO ccy(Abbreviation, Rate, last_updated)
                    VALUES('{currency_name}', {rate}, strftime("%s"))
                    on conflict (Abbreviation) do update set Rate=excluded.Rate,
                    last_updated = excluded.last_updated''')
    conn.commit()
