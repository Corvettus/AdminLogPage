
from service.emailService import monitor_emails
from service.database import init_db

from resources.Resources import Resources

import time
import threading

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def launch_parser():
    init_db()
    Resources.run_search = True

    emails_thread = threading.Thread(target=monitor_emails)
    emails_thread.start()

    try:
        while Resources.run_search:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Got KeyboardInterrupt, finishing task...")
        Resources.run_search = False
        emails_thread.join()


if __name__ == "__main__":
    launch_parser()
