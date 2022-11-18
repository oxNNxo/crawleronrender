import logging
import threading
import time

import schedule

from flask import Flask, request


import app
import service
import config

webapp = Flask(__name__)
webapp.logger.setLevel(logging.WARNING)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.LOGGING_LEVEL)
logger = logging.getLogger('App')

# if __name__ == '__main__':

	
# 	app.run()



def my_job():
	schedule.every(config.PTT_CRAWLER_PERIOD).minutes.do(service.check_ptt_newfeed)

	while True:
		schedule.run_pending()
		time.sleep(30)




@webapp.route('/')
def webhook_handler():
	"""Set route /hook with POST method will trigger this method."""
	return 'ok'

def run() -> None:
	t = threading.Thread(target=app.my_job)
	t.start()
	logger.info('Crawler on render is started.')
	service.check_ptt_newfeed()
	app.run(host=config.HOST, port=config.PORT)
