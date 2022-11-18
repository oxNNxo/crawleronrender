import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

REURL_TOKEN1 = os.getenv('REURL_TOKEN1')
REURL_TOKEN2 = os.getenv('REURL_TOKEN2')
REURL_TOKEN3 = os.getenv('REURL_TOKEN3')

LOGGING_LEVEL = int(os.getenv('LOGGING_LEVEL',20))
PTT_CRAWLER_PERIOD = int(os.getenv('PTT_CRAWLER_PERIOD',10))
WAKE_UP_MYSELF_PERIOD = int(os.getenv('WAKE_UP_MYSELF_PERIOD',10))

TELEGRAM_ALERT_TOKEN = os.getenv('TELEGRAM_ALERT_TOKEN')
TELEGRAM_MY_CHAT_ROOM = os.getenv('TELEGRAM_MY_CHAT_ROOM')

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT', 5000))

MYSELF_URL = os.getenv('MYSELF_URL')