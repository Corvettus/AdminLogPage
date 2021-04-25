
from typing import AnyStr, Pattern, Optional

from sqlalchemy.orm import Session

from models.ParsedMessage import ParsedMessage
from models.Alarm import Alarm

from service.database import provide_session
from service.alarmService import process_new_alarm

import datetime
import logging
import re


def parse_group(pattern: AnyStr, s: str) -> Optional[str]:
    parse = re.search(pattern, s)
    if parse is None:
        return None
    return parse.group(1)


DELIMITER = "------------------------------------------------"
FIRST_LINE = "Unit:"
DATETIME_FORMAT = "%d/%m/%y %H:%M"


@provide_session
def process_message(msg: ParsedMessage, session: Session):
    """
    Функция парсинга сообщения.
    При необходимости производит оповещение о аварии.
    :param msg:
    :param session:
    :return:
    """
    alarms = msg.message.split(DELIMITER)
    for alarm in alarms:
        alarm = alarm.replace("\r", "")
        if FIRST_LINE.lower() in alarm.lower():
            alarm = FIRST_LINE + alarm.partition(FIRST_LINE)[2]
        lines = alarm.splitlines()
        if len(lines) < 3:
            continue
        unit = parse_group("Unit:(\\w+)", alarm)
        version = parse_group("Version:(.+)", alarm)
        rack = lines[1]
        error = lines[2]
        generic = parse_group("Generic: (.+)", alarm)
        addr = parse_group("Addr: (.+)", alarm)
        alarm_date = parse_group("Alarm occurred: (.+)", alarm)
        if alarm_date:
            alarm_date = datetime.datetime.strptime(alarm_date, DATETIME_FORMAT)
        alarm_if_error = "Alarm if error" in alarm
        acknowledged = parse_group("Acknowledged: (\\w+)", alarm)
        if acknowledged:
            acknowledged = acknowledged.lower() == "yes"

        alarm = Alarm(subject=msg.subject, unit=unit, version=version, rack=rack, error=error, generic=generic,
                      addr=addr, alarm_date=alarm_date, alarm_if_error=alarm_if_error, acknowledged=acknowledged)
        session.add(alarm)
        session.commit()

        logging.info("New alarm!")
        logging.info(msg)

        process_new_alarm(alarm)


