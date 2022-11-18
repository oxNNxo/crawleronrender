import os
import logging
import datetime

from flask import Flask, request

import service
import config

webapp = Flask(__name__)
webapp.logger.setLevel(logging.WARNING)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.LOGGING_LEVEL)
logger = logging.getLogger('Bot')


@webapp.route('/')
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    return 'ok'

def run() -> None:
    service.check_ptt_newfeed()
    webapp.run(host=config.HOST, port=config.PORT)