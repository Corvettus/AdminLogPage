
from models.Alarm import Alarm

from service.callService import make_call

from config import phone_to_call


NOTIFY_ON_ERRORS = frozenset({
    "--- High Temp Alarm"
})


def process_new_alarm(alarm: Alarm):
    if alarm.error in NOTIFY_ON_ERRORS:
        # Нужно уведомить об ошибке
        pass
        print("Notifying!")
        make_call(phone_to_call)
