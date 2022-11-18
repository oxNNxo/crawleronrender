import json
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

import config




psycopg2.extras.register_uuid()
try:
	pool = ThreadedConnectionPool(0, 20, host=config.DATABASE_HOST, database=config.DATABASE_NAME, user=config.DATABASE_USER,
                              password=config.DATABASE_PASSWORD)
except Exception as e:
	print(str(e))

def get_pool():
    return pool