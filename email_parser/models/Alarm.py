
from sqlalchemy import Column, BigInteger, VARCHAR, TIMESTAMP, func, INT, BOOLEAN
from sqlalchemy.orm import relationship, Session

from service.database import Base


class Alarm(Base):
    __tablename__ = 'alarms'

    id = Column(BigInteger().with_variant(INT, "sqlite"), primary_key=True)
    subject = Column(VARCHAR(256))
    unit = Column(INT)
    version = Column(VARCHAR(32))
    rack = Column(VARCHAR(32))
    error = Column(VARCHAR(128))
    generic = Column(VARCHAR(128))
    addr = Column(INT)
    alarm_date = Column(TIMESTAMP)
    alarm_if_error = Column(BOOLEAN)
    acknowledged = Column(BOOLEAN)
