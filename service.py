import requests
import datetime
from bs4 import BeautifulSoup
import datetime
import re
import time
import json
import logging

import datasource
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.LOGGING_LEVEL)
logger = logging.getLogger('Service')

pool = datasource.get_pool()

token_reurl = [config.REURL_TOKEN1,config.REURL_TOKEN2,config.REURL_TOKEN3]

def lineNotifyMessage(msg,token):
	line_headers = {
		"Authorization": "Bearer " + token,
		"Content-Type" : "application/x-www-form-urlencoded"
	}
	payload = {'message': msg}
	r = requests.post("https://notify-api.line.me/api/notify", headers = line_headers, params = payload)
	return r.status_code


def tgNotifyMessage(msg):
	bot_token = config.TELEGRAM_ALERT_TOKEN
	chat_id = config.TELEGRAM_MY_CHAT_ROOM
	text = msg
	url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&text=' + text
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}
	response = requests.get(url,headers = headers)


def wake_up_myself():
    logger.info('wake_up_myself')
    url = MYSELF_URL.MYSELF_URL
    try:
        conn = requests.get(url)
    except Exception as e:
        logger.error(str(e), exc_info=True)


def reurl(token,origin_url):
	reurl_headers = {
		"Content-Type" : "application/json" ,
		"reurl-api-key" : token 
	}
	payload = {"url": origin_url}
	payload_json = json.dumps(payload)

	r = requests.post("https://api.reurl.cc/shorten",headers = reurl_headers,data = payload_json)
	# print(r.text)
	try:
		response_json = json.loads(r.text)
	
		if 'res' in response_json:
			return response_json['short_url']
		elif 'code' in response_json :
			return 'fail'
	except json.decoder.JSONDecodeError:
		return r.text


def get_user_subs_board_with_latest_time():
	conn = pool.getconn()
	all_results = []
	with conn:
		with conn.cursor() as cursor: 
			sql = '''
				SELECT pus.board,to_char(pbl.latest_time at time zone 'asia/taipei','yyyy-mm-dd HH24:MI:SS+08') 
				FROM pyptt_user_subs as pus , pyptt_board_list as pbl 
				where pus.board = pbl.board 
				GROUP BY pus.board , pbl.latest_time
				'''
			cursor.execute(sql)
			all_results = cursor.fetchall()
	pool.putconn(conn, close=True)
	return all_results


def get_user_board_key():
	conn = pool.getconn()
	all_results = []
	with conn:
		with conn.cursor() as cursor: 
			sql = '''SELECT pus.user_id,pus.board,pus.sub_key 
				FROM pyptt_user_subs as pus '''
			cursor.execute(sql)
			all_results = cursor.fetchall()
	pool.putconn(conn, close=True)
	return all_results


def get_user_chat_room_id():
	conn = pool.getconn()
	all_results = []
	with conn:
		with conn.cursor() as cursor: 
			sql = '''SELECT pu.id,pu.chat_id 
				FROM pyptt_user as pu '''
			cursor.execute(sql)
			all_results = cursor.fetchall()
	pool.putconn(conn, close=True)
	return all_results


def crawl_ptt(board):
	url =  'https://www.ptt.cc/atom/' + board + '.xml'
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}
	response = requests.get(url,headers = headers)
	soup = BeautifulSoup(response.content,'html.parser')
	titlelist = []
	idlist = []
	authorlist = []
	timelist = []
	articlelist = []
	for entry in soup.find_all('entry') :
		temp = []
		_title = entry.find('title')
		_id = entry.find('id')
		_name = entry.find('name')
		_time = entry.find('published')
		corr_time = str(_time.text[:10]) + ' ' + str(_time.text[11:19]) + '+08'
		# titlelist.append(_title.text)
		# idlist.append(_id.text)
		# authorlist.append(_name.text)
		timelist.append(corr_time)
		temp.append(_title.text)
		temp.append(_id.text)
		temp.append(_name.text)
		temp.append(corr_time)
		articlelist.append(temp) # new to old
		# print(_title.text,_id.text,_name.text,corr_time)
		# print(temp)
	logger.info(f"{'{:<12}'.format(board)} {articlelist[0][3]}")
	return articlelist


def update_board_latest_time(blt_list):
	conn = pool.getconn()
	all_results = []
	with conn:
		with conn.cursor() as cursor: 
			for blt in blt_list:
				sql = '''
				UPDATE pyptt_board_list
				SET latest_time = TIMESTAMP with time zone %s
				WHERE board = %s;
				COMMIT;
				'''
				cursor.execute(sql,(blt[0],blt[1]))
	pool.putconn(conn, close=True)


def check_ptt_newfeed():
	logger.info('Checking for ptt newfeed')
	board_latest_time = get_user_subs_board_with_latest_time()
	blt = {}
	for pair in board_latest_time:
		blt[pair[0]] = {}
		blt[pair[0]]['pre_latest_time'] = pair[1]
	all_results = get_user_board_key()
	ubk = {}
	for pair in all_results:
		if pair[0] not in ubk:
			ubk[pair[0]] = {}
		if pair[1] not in ubk[pair[0]]:
			ubk[pair[0]][pair[1]] = []
		ubk[pair[0]][pair[1]].append(pair[2])
	all_results = get_user_chat_room_id()
	user_chat_id = {}
	for pair in all_results:
		user_chat_id[pair[0]] = pair[1]
	try:
		for boardName in blt:
			blt[boardName]['article'] = crawl_ptt(boardName)
			blt[boardName]['now_latest_time'] = blt[boardName]['article'][0][3]
			time.sleep(1)
		for user in ubk:
			newfeed_article = []
			for boardName in ubk[user]:
				latesttime = blt[boardName]['pre_latest_time']
				_latesttime = datetime.datetime.strptime(latesttime,'%Y-%m-%d %H:%M:%S+08')
				_minute = _latesttime.time().minute
				if  _minute >= 0 and _minute < 20 :
					token = token_reurl[0]
				elif _minute >= 20 and _minute < 40 :
					token = token_reurl[1]
				elif _minute >= 40 and _minute < 60 :
					token = token_reurl[2]
				for article in reversed(blt[boardName]['article']) : # old to new
					articletime = datetime.datetime.strptime(article[3],'%Y-%m-%d %H:%M:%S+08')
					if articletime > _latesttime:
						for pattern in ubk[user][boardName]:
							_pattern = re.compile(pattern,flags=re.IGNORECASE)
							if re.search(_pattern,article[0]) :
								if 'reurl.cc' not in article[1]:
									article[1] = reurl(token,article[1])
								time.sleep(1)
								newfeed = 1
								morefeed = 1
								newfeed_article.append('{:<12}'.format(boardName) + ' ' + article[1] + '\n' + article[0])	# board link <br> title
								break
			while len(newfeed_article) > 0:
				newline_chara = '\n'
				msg_user = f"```{newline_chara.join(newfeed_article[:10])}```"
				lineNotifyMessage(msg_user,user_chat_id[user])
				newfeed_article = newfeed_article[10:]
	except IndexError:
		logger.error(str(IndexError))
		pass
	except requests.exceptions.ConnectionError:
		logger.error(str(requests.exceptions.ConnectionError))
		pass
	except requests.exceptions.SSLError:
		logger.error(str(requests.exceptions.SSLError))
		pass
	except Exception as e:
		logger.error(str(e))
		pass
	update_latesttime = list()
	for boardName in blt:
		update_latesttime.append((blt[boardName]['now_latest_time'],boardName))
	done = 0
	while done == 0:
		try:
			update_board_latest_time(update_latesttime)
			done = 1
			logger.info('Checking for ptt newfeed successfully')
		except Exception as e:
			tgNotifyMessage('Update PyPTT error:'+str(e))
			logger.error(str(e))





def simple_sql(sql):

	conn = pool.getconn()
	all_results = []
	with conn:
		with conn.cursor() as cursor:    
			cursor.execute(sql)
			all_results = cursor.fetchall()
			conn.commit()
	pool.putconn(conn, close=True)
	return all_results