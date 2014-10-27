__author__ = 'brayden'

import logging


class Log:
    def __init__(self):
        pass
    def info(self, message):
        logging.info(message)

    def warning(self, message):
        logging.warning(message)

    def error(self, message):
        logging.error(message)

    def critical(self, message):
        logging.critical(message)