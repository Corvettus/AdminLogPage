
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from functools import wraps

from config import psql_credentials

import os

if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    DATABASE_URL = f'postgresql+psycopg2://{psql_credentials["user"]}:{psql_credentials["pass"]}@' \
                   f'{psql_credentials["host"]}:{psql_credentials["port"]}/{psql_credentials["dbname"]}'

engine = create_engine(DATABASE_URL, echo=False)

SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    session = SessionMaker()

    Base.metadata.create_all(engine)

    session.close()


def provide_session(func):
    """
    Прокидывает в функцию новую сессию БД и автоматически осуществляет контроль ресурсов
        (закрывает сессию при любом завершении выполнения функции)

    Пример использования:
    @provide_session
    def func(session):
        session.query(...)

    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "session" in kwargs or list(filter(lambda arg: isinstance(arg, Session), args)):
            return func(*args, **kwargs)
        session = SessionMaker()
        try:
            result = func(*args, session=session, **kwargs)
        finally:
            session.close()
        return result
    return wrapper
