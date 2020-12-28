#!/usr/bin/env python3

from datetime import datetime, date
from borg_helper import BorgHelper, CustomLog

if __name__ == "__main__":

    logger = None

    try:
        # Logging
        logging = CustomLog()
        logging.set_prod_log('./logs/backup.log')
        logging.set_err_log('./logs/backup.err.log')
        logging.set_stream_log()
        logger = logging.log
        # Begin backup
        BEGIN = datetime.now()
        EXTENSION = BEGIN.strftime('%Y%m%d_%H%M%S')
        logger.info('+++ BORG CREATE REPO - Started at {} +++'.format(BEGIN.strftime('%d/%m/%Y %H:%M:%S')))
        borg_helper = BorgHelper("config/.borg.ini",logger)
        borg_helper.create_repo()
    except Exception as err:
        logger.error(err)
    finally:
        END = datetime.now()
        logger.info(f"--- BORG CREATE REPO - Ended at {END.strftime('%d/%m/%Y %H:%M:%S')}")