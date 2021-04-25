
from config import CALLS_API_KEY

import requests

CALL_URL = "https://lk.calldog.ru/apiCalls/create"


def make_call(phone):
    """
    Производит звонок по телефону phone с оповещением об аварии.
    :param phone:
    :return:
    """
    res = requests.post(CALL_URL, json={
        "apiKey": CALLS_API_KEY,
        "phone": phone,
        "dutyPhone": 1,
        "record": {
            "text": "Тестовое сообщение о сбое оборудования",
        }
    })
    print(res)
    print(res.json())
