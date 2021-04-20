import sqlite3
import pb
import os
import logging

dbconn = None
CACHE_AGE = int(os.getenv('TGBOT_CACHE_MAXAGE', 3600))
LOG_LEVEL = os.getenv("TGBOT_LOGLEVEL", "WARNING")
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=LOG_LEVEL
)


def get_currency_rate(currency_name):
    try:
        return read_cached_currency_rate(currency_name, CACHE_AGE)
    except:
        return get_currency_rate2(currency_name)


def get_currency_rate2(currency_name):
    try:
        rate = pb.get_exchanges(currency_name)
        store_currency_rate(currency_name, rate)
        logging.debug('updated value from site')
        return rate
    except:
        return read_cached_currency_rate(currency_name)


def dbcursor():
    global dbconn
    if not dbconn:
        dbconn = sqlite3.connect('currency.db')
        dbconn.execute('''CREATE TABLE IF NOT EXISTS ccy (
                            Abbreviation TEXT NOT NULL PRIMARY KEY,
                            Rate FLOAT NOT NULL,
                            last_updated timestamp default (strftime('%s', 'now')))''')
    return dbconn.cursor(), dbconn


def read_cached_currency_rate(currency_name, cache = None):
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
    curs, conn = dbcursor()
    curs.execute(f'''INSERT INTO ccy(Abbreviation, Rate, last_updated) VALUES('{currency_name}', {rate}, strftime("%s"))  
                        on conflict (Abbreviation) do update set Rate=excluded.Rate, last_updated = excluded.last_updated''')
    conn.commit()


