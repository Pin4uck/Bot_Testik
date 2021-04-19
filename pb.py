import re
import requests
import json


URL = 'https://www.nbrb.by/api/exrates/rates?periodicity=0'


def load_exchange():
    return json.loads(requests.get(URL).text)


def get_exchange(ccy_key):
    for exc in load_exchange():
        if ccy_key == exc['Cur_Abbreviation']:
            return exc
    return False


def get_exchanges(ccy_pattern):
    ccy_pattern = re.escape(ccy_pattern) + '.*'
    for exc in load_exchange():
        if re.match(ccy_pattern, exc['Cur_Abbreviation'], re.IGNORECASE) is not None:
            return exc['Cur_OfficialRate']
    raise LookupError(ccy_pattern)
