

import imaplib
import email
import logging
import time

from email.header import decode_header

from config import email_addr, email_port, login, password

from models.ParsedMessage import ParsedMessage

from resources.Resources import Resources

from message_process import process_message


def connect(addr, port, user, password) -> imaplib.IMAP4_SSL:
    """
    Соединяется с IMAP сервером и логинится.
    :param addr:
    :param port:
    :param user:
    :param password:
    :return:
    """
    conn = imaplib.IMAP4_SSL(addr, port)
    conn.login(user, password)
    conn.select()

    return conn


def get_unseen(conn: imaplib.IMAP4_SSL):
    """
    Получает непрочитанные сообщения
    :param conn:
    :return:
    """
    # status, messages = conn.select("INBOX")
    status, messages = conn.search(None, '(UNSEEN)')
    print(status, messages)

    return messages[0].decode().split()


def load_message(conn: imaplib.IMAP4_SSL, message_id: int) -> ParsedMessage:
    """
    Загружает сообщение с message_id
    :param conn:
    :param message_id:
    :return:
    """
    res, msg = conn.fetch(str(message_id), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = parse_message(response)
            return msg


def extract_body(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])


def parse_message(data: tuple) -> ParsedMessage:
    """
    Преобразует данные сообщения в тип ParsedMessage.
    :param data:
    :return:
    """
    msg = email.message_from_bytes(data[1])
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        # if it's a bytes, decode to str
        subject = subject.decode(encoding)
    # decode email sender
    from_addr, encoding = decode_header(msg.get("From"))[0]
    if isinstance(from_addr, bytes):
        from_addr = from_addr.decode(encoding)
    if msg.is_multipart():
        # iterate over email parts
        body = None
        for part in msg.walk():
            # extract content type of email
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            try:
                # get the email body
                body = part.get_payload(decode=True).decode()
            except Exception:
                pass
            if content_type == "text/plain":
                # print text/plain emails and skip attachments
                # print(body)
                break
            if "attachment" in content_disposition:
                # download attachment
                filename = part.get_filename()
    else:
        # extract content type of email
        content_type = msg.get_content_type()
        # get the email body
        body = msg.get_payload(decode=True).decode()
        if content_type == "text/plain":
            # print only text email parts
            pass
    if body is not None:
        return ParsedMessage(from_addr, subject, body)


def monitor_emails():
    logging.info("Monitoring emails!")
    while Resources.run_search:
        check_new_emails()
        sleep_timeout_flag(Resources.UPDATE_INTERVAL)


def sleep_timeout_flag(seconds: float):
    n = 0
    while Resources.run_search and n < seconds:
        time.sleep(1)
        n += 1


def check_new_emails():
    """
    Получает все непрочитанные письма и обрабатывает их.
    :return:
    """
    logging.info("Checking emails!")
    conn = connect(email_addr, email_port, login, password)
    unseen = get_unseen(conn)

    try:
        pass
        for i in unseen:
            msg = load_message(conn, i)
            process_message(msg)

    finally:
        try:
            conn.close()
        except:
            pass
        conn.logout()
