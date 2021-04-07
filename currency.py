import sqlite3
import pb
CACHE_AGE = 15  # update time in seconds


def get_currency_rate(currency_name):
    try:
        print('проверка(с базы обновл)')
        return read_cached_currency_rate(currency_name, CACHE_AGE)
    except:
        return get_currency_rate2(currency_name)


def get_currency_rate2(currency_name):
    try:
        rate = get_network_currency_rate(currency_name)
        store_currency_rate(currency_name, rate)
        print('проверка(с сайта)')
        return rate
    except:
        print('проверка(с базы необновл)')
        return read_cached_currency_rate(currency_name)


def dbcursor():
    dbconn = None
    if not dbconn:
        dbconn = sqlite3.connect('currency.db')
        dbconn.execute('''CREATE TABLE IF NOT EXISTS ccy (
                            Abbreviation TEXT NOT NULL PRIMARY KEY,
                            Rate FLOAT NOT NULL,
                            last_updated timestamp default (strftime('%s', 'now')))'''
        )
    return dbconn.cursor()


def read_cached_currency_rate(currency_name, cache = None):
    curs = dbcursor()
    if cache == None:
        curs.execute(f'''SELECT Rate FROM ccy 
                                WHERE Abbreviation = '{currency_name}' ''')
    else:
        curs.execute(f'''SELECT Rate FROM ccy 
                        WHERE Abbreviation = '{currency_name}' and (strftime('%s') - last_updated <= {cache})''')
    value = curs.fetchall()
    if value:
        return value[0][0]
    raise LookupError


def get_network_currency_rate(currency_name):
    idd, abbr, ofcrate = pb.get_exchanges(currency_name)
    return ofcrate


def store_currency_rate(currency_name, rate):
    dbconn = sqlite3.connect('currency.db')
    dbconn.execute(f'''INSERT INTO ccy(Abbreviation, Rate, last_updated) VALUES('{currency_name}', {rate}, strftime("%s"))  
                        on conflict (Abbreviation) do update set Rate=excluded.Rate, last_updated = excluded.last_updated''')
    dbconn.commit()