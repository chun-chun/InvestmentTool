##################################
#	Purpose : fetch Stock data.
#	Version : 1.0
#	Author	: Stenen Yu
#	Release	:
#	
##################################

import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
import datetime
import json
import sys
import os
import csv

from ToolSetting import *

import pprint
# global parma

INFO = "info"
FILEPATH = "stockData"

# YEAR, MONTH, DAY = str(datetime.date.today()).split("-")

def record_stock_data( stockData = {} ):
	pprint.pprint(stockData)
	global INFO

	if not (len(stockData)):
		print("no data(1)")
		return 1

	fileName 	= "stockData"
	stockCode 	= stockData[INFO]["code"]
	csvName 	= {
					"day"	: "month",
					"month"	: "year",
					"year"	: "all",

					}.get(stockData[INFO]["style"], "exeption" )
	

	if len( stockData )>0 :
		if not (os.path.exists("./{}".format(fileName))) :
			os.mkdir("./{}".format(fileName))

		if not (os.path.exists("./{0}/{1}".format(fileName, stockCode))) :
			os.mkdir("./{0}/{1}".format(fileName, stockCode))		

		with open("./{0}/{1}/{2}.csv".format(fileName, stockCode, csvName),"w", encoding = SYSTEM_CODE) as f :
			f.write(str(stockData))

	else :
		print("No data")

def get_month_history(stockCode = 2317, year = 2016, stockData = None):
	stockCode = str(stockCode)	
	year = str(year)

	if (stockData == None) :
		stockData = {}

	url = "http://www.twse.com.tw/ch/trading/exchange/FMSRFK/FMSRFKMAIN.php"

	data = {
		"query_year" 	: (year),
		"CO_ID"			: (stockCode),
		"query-button"	:"查詢"
		}

	headers = {
		"Accept-Language":"en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
		"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
		}

	re = requests.post(url, headers = headers, data = data)
	re.encoding  = 'utf-8'
	# print(help(BeautifulSoup))

	soup = BeautifulSoup(re.text, "html.parser")

	levelname = soup.table.thead.find_all("tr")[1].find_all("td")
	level = soup.table.tbody.find_all("tr")
	levelvale = level[0].find_all("td")
	# print((re.text))

	cnt = 0
	name = {}
	for x in levelname:
		# print(str(x.string).decode("ascii").encode("utf-8")) 
		if x.string not in stockData.keys():
			stockData[x.string] = []
		name[cnt] = x.string
		cnt += 1

	for x in level:
	    vale = x.find_all("td")
	    cnt = 0
	    for y in vale:
	    	# print(y)
	    	stockData[name[cnt]].append(y.string)
	    	cnt += 1

	if (stockData.get(INFO, "Add")) == "Add" :
		stockData[INFO] = {"code": stockCode, "style": "month", "end": len(level)}
	else:
		stockData[INFO]["end"] = len(level) 

	return stockData

def get_more_month_history(stockCode = 2317, track_month = 5, from_year = None):
	stock_data = {}
	# if ( check_csv_data_info() == 	
	for x in reversed(range(5)) :
		stock_data = get_month_history(stockCode = stockCode, stockData = stock_data, year = int(from_year) - x)

	stock_data[INFO]["from_year"] = from_year 
	stock_data[INFO]["end_year"] = str(int(from_year) - x) 
	return stock_data

def get_history_stock_use_YahooApi( stockCode, from_time, to_time, mode = "day", fileName = None):
	from_year , from_month , from_day = from_time 
	to_year , to_month , to_day = to_time 
	from_month	= str( int(from_month) -1 )
	to_month	= str( int(to_month) -1 )
	Flag = True
	downloadFlag = True

	if mode == "hour":
		pass
	else :
		StockUrl = "http://ichart.finance.yahoo.com/table.csv?s={stockCode}&a={from_month}&b={from_day}&c={from_year}&d={to_month}&e={to_day}&f={to_year}&g=d&ignore=.csv".format(
			stockCode 	= stockCode,

			from_year 	= from_year, 
			from_month 	= from_month, 
			from_day 	= from_day,

			to_year 	= to_year ,
			to_month 	= to_month ,
			to_day 		= to_day,

			)

		# print (  StockUrl)

		if fileName == None:
			fileName = str(stockCode)

		data = []
		fileName = 	os.path.join( FILEPATH, "{0}.csv".format(fileName) )

		if (os.path.exists(fileName)):
			
			filedate = os.path.getmtime(fileName)
			filedate = datetime.fromtimestamp(filedate)

		# # download stock csv file

			if ( ( int(to_year) == int(filedate.year)) and ( int(to_month) == int(filedate.month)-1) and ( int(to_day) == int(filedate.day)) ):
				downloadFlag = False

		# while True:

		if (downloadFlag):
			urllib.request.urlretrieve(StockUrl, fileName)

		listtmp = []
		with open(fileName, "r" ) as f:
			# data = csv.reader(f)
			for row in csv.reader(f):
				# print((row))
				if Flag == True:
					Flag = False
				else:
					data.append(row)

			tmp_year, tmp_month, tmp_day = row[0].split("-")
			# pprint.pprint(row[0].split("-"))

		# if ():
		# 	pass
		# with urllib.request.urlopen(StockUrl) as f :
		# 	f_csv = csv.DictReader(f.read())
		# 	for row in f_csv:
		# 		print(row)

		return data


def get_history_stock_info(stockCode, from_day, to_day, location = ".tw", mode = "day", fileName = None, api = "yahoo"):
	stockHistoryData = None

	if( type(stockCode) is int ):
		stockCode =  str(stockCode) 

	stockCodeTmp = stockCode + location
	# print(stockCode)
	lenList = len(stockCodeTmp)
	if(not lenList):
		print("there is no stock id need to find")
		return 0 ;

	if (api == "yahoo"):
		stockHistoryData = get_history_stock_use_YahooApi(stockCodeTmp, from_day, to_day, mode , fileName = stockCode )

	return stockHistoryData

def get_realtime_stock_info(StockList):

	if( type(StockList) is int ):
		StockList = [ str(StockList) ]
	elif ( type(StockList) is str ):
		StockList = [StockList]

	# print(StockList)
	lenList = len(StockList)
	if(not lenList):
		print("there is no stock id need to find")
		return 0 ;

	data = {}
	mapList = {
		'ex': u'上市上櫃',
		# 's': 'ssssss',
		'd': u'當日', 
		'v': u'當日累計成交量', 
		'w': u'跌停價', 
		'y': u'昨收', 
		'h': u'最高價', 
		# 'tk1': '2317.tw_tse_20160519_B_9999279012', 
		'c': u'公司代號', 
		# 'p': 'pppp', 
		# 'oa': 'oooaaa', 
		# 'tlong': '資料時間', 
		'g': u'買量', 
		'ip': u'漲跌flag', 
		'pz': u'買價', 
		'l': u'最低價', 
		'nf': u'公司全名', 
		# 'mt': 'mmmtttt', 
		# 'ov': 'oooovvvv', 
		'tv': u'當盤成交量', 
		# 'ps': 'pppssss', 
		# 'tk0': '2317.tw_tse_20160519_B_9999297439', 
		'f': u'賣量', 
		# 'ot': u'時間', 
		# 'ts': 'tttssss', 
		'b': u'最佳買價', 
		'n': u'股票名稱', 
		'z': u'最近成交價', 
		# 'i': 'iiiiii', 
		't': u'資料時間', 
		'a': u'最佳賣價', 
		'u': u'漲停價', 
		'o': u'開盤', 
		# 'it': 'iiitttt', 
		# 'ob': 'oooobbbbb', 
		# 'ch': '2317.tw', 
		# 'oz': 'oooozzzzz'
		}

	headers = {
		'Accept-Language':'zh-TW'
		}


	# # stock url 
	StockUrl = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=" 
	for member in StockList:
		StockUrl += 'tse_{0}.tw|'.format(member)

	# print(StockUrl)

	try:
		req = requests.session()
		req.get('http://mis.twse.com.tw/stock/index.jsp',
			headers = headers
			)
	except requests.exceptions.ConnectionError as err:
		print(err)
		return 0

	response = req.get(StockUrl)
	datatemp = response.json()
	# pprint.pprint(datatemp)

	if not (datatemp["msgArray"]):
		# print("error data.")
		return None

	# # classify receive data
	for x in range(lenList):
		message = datatemp["msgArray"][x]
		name = message["c"]
		# name = message["n"]
		data[name] = {}
		for para in mapList.keys():
			if para in ("b", "a", "g", "f") :
				# part of more data 
				data[name][mapList[para]]  = message[para].split("_")[:-1]
			else :
				data[name][mapList[para]]  = message[para]

	# pprint.pprint(data)
	return data





def main():


	# data = get_more_month_history()	
	# data = {}
	# for x in reversed(range(5)) :
	# 	data = get_month_history(stockData = data, year = int(YEAR) - x)
	# 	# pprint.pprint(id(data))
	# pprint.pprint((data))
	# data2 = get_month_history(year = 2015)
	# for x in data.keys():
	# 	data[x].extend(data2[x])

	# print(data)
	# record_stock_data(stockData = data )
	# pprint.pprint((data))
	# pprint.pprint((data2))


	ans = get_realtime_stock_info( "2317" )
	# ans = get_history_stock_info( "2317" , ( 2015, 6, 20  ), ( 2015, 8, 4  ) )
	# pprint.pprint(ans)
	# with open("a.log", "w") as f:
	# 	pprint.pprint(ans, stream = f, encoding = big)

if __name__ == '__main__':
	main()
