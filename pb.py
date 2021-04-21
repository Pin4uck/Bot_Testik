"""Модуль json позволяет кодировать и декодировать данные в удобном формате"""
import json
import re
import requests


URL = 'https://www.nbrb.by/api/exrates/rates?periodicity=0'


def load_exchange():
    """Данная функция возвращает полученные данные с сайта"""
    return json.loads(requests.get(URL).text)


def get_exchange(ccy_key):
    """Данная функция возвращает данные по валюте(ccy_key)
     из полученных данных в load_exchange()"""
    for exc in load_exchange():
        if ccy_key == exc['Cur_Abbreviation']:
            return exc
    return False


def get_exchanges(ccy_pattern):
    """Данная функция возвращает курс валют(exc['Cur_OfficialRate'])
     из полученных данных в get_exchange(ccy_key)"""
    ccy_pattern = re.escape(ccy_pattern) + '.*'
    for exc in load_exchange():
        if re.match(ccy_pattern, exc['Cur_Abbreviation'], re.IGNORECASE) is not None:
            return exc['Cur_OfficialRate']
    raise LookupError(ccy_pattern)
