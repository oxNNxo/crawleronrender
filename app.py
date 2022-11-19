import logging
import threading
import time

import schedule


import app
import bot
import service
import config



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.LOGGING_LEVEL)
logger = logging.getLogger('App')

if __name__ == '__main__':
	t = threading.Thread(target=app.my_job)
	t.start()
	logger.info('Crawler on render is started.')
	bot.run()




def my_job():
	schedule.every(config.PTT_CRAWLER_PERIOD).minutes.do(service.check_ptt_newfeed)
	schedule.every(config.CAPITAL_FUND_CRAWLER_PERIOD).minutes.do(service.check_capitalfund_newfeed)
	schedule.every(config.WAKE_UP_MYSELF_PERIOD).minutes.do(service.wake_up_myself)
	while True:
		schedule.run_pending()
		time.sleep(30)





	
	
