#!/usr/local/bin/ python3

##################################
#	Purpose : use to investment tool.
#	Version : 1.0
#	Author	: Stenen Yu
#	Release	:
#	
##################################

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg 
from matplotlib.figure import Figure
# import matplotlib.animation as animation
from matplotlib import style
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc # quotes_historical_yahoo_ohlc ,volume_overlay3
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY ,MonthLocator

import numpy as np
import pandas as pd

import time
import urllib
import json  
import tkinter as tk
from tkinter import ttk
import datetime
import sys
import pprint
import configparser

import GetStock
# from ToolSetting import *

########### win setting ##############

winSetting = {
	"sampling_period"	: 2000 ,

	"atLeastDay" 		: 0,
	"atLeastMonth" 		: 6,
	"atLeastYear" 		: 1,

	"stockLayout"		: 1,

}
 


########### win setting  end ##############

# define
FONT 		= "Verdana"
NORM_FONT 	= (FONT, 16)
LARGE_FONT 	= (FONT, 33)
MID_FONT 	= (FONT, 12)
SMALL_FONT 	= (FONT, 10)

# # color define
BACK_GROUND_COLOR 			= "white"
FORE_GROUND_COLOR 			= "black"
# BACK_GROUND_COLOR 			= "white"
# FORE_GROUND_COLOR 			= "black"
# MENU_BACK_GROUND_COLOR 		= "white"
# MENU_FOR_GROUND_COLOR 		= "black"
STATUS_BAR_COLOR 			= "white"
STATUS_FORE_GROUND_COLOR 	= "black"


DARK_COLOR 	= "#183A54"
WHITE_COLOR = "#183A54"
LIGHT_COLOR	= "#00A3E0"
STOCK_GOOD_COLOR = "red"
STOCK_BAD_COLOR = "green"

CONFIG_FILE = "config.ini"
LOG_FILE 	= "fw.log"
UPDATE = 0
VERSION = 1.0

YEAR, MONTH, DAY = str(datetime.date.today()).split("-")
if (sys.platform == "win32"):
	SYSTEM_CODE = "utf-8"
else :
	# SYSTEM_CODE = "big5"
	SYSTEM_CODE = "utf-8"
# define end


## page info
PageInfo = {
	"mode"			: 	None,
	"pageObject"	: 	None,
	"stopInternet"	: 	0,

	### stock info
	"stockChoice"	: 	None,
	"stockName"		:	None,
	"priceLevel"	: 	5,
	
	"stockPlace"	: 	"TW",
	### house info

}

statusBarMessage = {
	"StockPage" 	: "stock mode", 
	"HousePage" 	: "hourse mode", 



}

## inital 
my_choice_stock = []

FIRST_FRAME		=  True

STOCK_ID_LIST 	= {}
STOCKDATA 		= {}
STOCKMONTHDATA 	= {}


style.use("bmh")
# style.use("ggplot")
# print(style.available)

MONDAYS 		= WeekdayLocator(MONDAY)        # major ticks on the mondays
ALLDAYS 		= DayLocator()              	# minor ticks on the days
MONTHS 			= MonthLocator()
MONTH_FORMATTER	= DateFormatter('%Y-%m')  		# e.g., Jan 12
DAY_FORMATTER 	= DateFormatter('%d')      		# e.g., 12
LOCATOR 		= mticker.MaxNLocator(10)

class InvestmentGUI(ttk.Frame):
	"""
	docstring for InvestmentGUI
	"""
	global PageInfo
	def __init__(self, master = None):
		super(InvestmentGUI, self).__init__(master)
# 		setting inital
		self.parent = master
		self.initSet()

		master.wm_title("InvestmentTool")
		# master.geometry("640x500")
		master.minsize(210, 300)
		windos = master.winfo_toplevel()
		windos.columnconfigure(0, weight = 1)
		windos.rowconfigure(0, weight = 1)

		# master.iconbitmap("bookmark.ico")

		# self["bg"] = BACK_GROUND_COLOR
		self.pack(side = "top", fill = "both", expand = True)
		self.grid_rowconfigure(0, weight = 1)
		self.grid_columnconfigure(0, weight = 1)

#		widget 
		self.createMenu()

		self.statusBar = StatusBar(self)
		self.statusBar.grid(row = 1, column = 0, sticky = "nsew")

		startPage = None
		self.frames = {}
		for page in (StockPage, HousePage):	
			frame = page(self)
			self.frames[page] = frame
			frame.grid(row = 0, column = 0, sticky = "nsew")

			# PRINT(  frame.pageOk() )
			if ( startPage == None ) and (frame.pageOk()):
				startPage = page

#		bind
		self.createBindSetting()

		## first inital.
		self.showFrame(startPage)

	def initSet(self):

		# ### set gui style
		guiStyle = ttk.Style()
		# guiStyle.theme_use('winnative')
		# PRINT(guiStyle.theme_names())

		# guiStyle.configure("TFrame",
		# 	# background 	= BACK_GROUND_COLOR,	
		# 	background 	= BACK_GROUND_COLOR,	
		# 	foreground 	= FORE_GROUND_COLOR,
		# 	# padding 	= 100,
		# 	# highlightcolor="reliefd"

		# )
		# guiStyle.layout("TFrame",[('Frame.border', {'sticky': 'nswe'})] )

		# # PRINT(self.parent.guiStyle.layout("TFrame"))
		# guiStyle.configure("TLabel",
		# 	background = BACK_GROUND_COLOR,	
		# 	foreground = FORE_GROUND_COLOR,

		# )

		# # set stock init		
		PageInfo["stockChoice"] = my_choice_stock[0]

		# # set log file
		with open(LOG_FILE, "w", encoding = SYSTEM_CODE) as f :
			f.write("#{0} {1} {2}\n".format(YEAR, MONTH, DAY))


	def createMenu(self):
		menuber = tk.Menu(self,
			bg = BACK_GROUND_COLOR,
			fg = FORE_GROUND_COLOR,

			)
		self.parent["menu"] = menuber

		fileMenu = tk.Menu(menuber, tearoff = 0)
		for label, command, shortcut_text, shortcut in (
				# need fix : i dont know why lamba bug.
				("New...", 		self.fileNew, 	"Ctrl+n", 	"<Control-n>"),
				("Open...", 	self.fileOpen, 	"Ctrl+o", 	"<Control-o>"),
				(None,	None, 	None, 	None),
				("Exit",		self.Quit, 		"Esc", 		None),
				):
			if label is None:
				fileMenu.add_separator()
			else:
				fileMenu.add_command(label = label, underline = 0,
						command = command, accelerator = shortcut_text)
				self.parent.bind(shortcut, command)

		menuber.add_cascade(label = "File", menu = fileMenu, underline = 0)

		editMenu = tk.Menu(menuber, tearoff = 0)
		for label, command, shortcut_text, shortcut in (
				("Search...",	self.search, 	"Ctrl+f", 	"<Control-f>"),			
				# ("New...", 		lambda: self.fileNew, 	"Ctrl+n", 	"<Control-n>"),

				):
			if label is None:
				editMenu.add_separator()
			else:
				editMenu.add_command(label = label, underline = 0,
						command = command, accelerator = shortcut_text)
				self.parent.bind(shortcut, command)

		menuber.add_cascade(label = "Edit", menu = editMenu, underline = 0)

		PageMenu = tk.Menu(menuber, tearoff = 0)
		for label, command, shortcut_text, shortcut in (
				("StockPage", lambda : self.showFrame(StockPage), "Ctrl+1", "<Control-1>"),
				("HousePage", lambda : self.showFrame(HousePage), "Ctrl+2", "<Control-2>"),
				# ("Win...",lambda : popumsg("Steven"), "Ctrl+p", "<Control-p>",)
				):
			if label is None:
				PageMenu.add_separator()
			else:
				PageMenu.add_command(label = label, underline = 0,
						command = command, accelerator = shortcut_text)
				self.parent.bind(shortcut, command)

		menuber.add_cascade(label = "Page", menu = PageMenu, underline = 0)

		stockMenu = tk.Menu(menuber, tearoff = 0)
		for label, command, shortcut_text, shortcut in (
				# ("select_stock",None, None, None,),
				("graph", 	lambda : self.frames[StockPage].stockGraphPage(), None, None,),
				# ("Win...",lambda : popumsg("Steven"), "Ctrl+p", "<Control-p>",)
				):
			if label is None:
				stockMenu.add_separator()
			else:
				stockMenu.add_command(label = label, underline = 0,
						command = command, accelerator = shortcut_text)
				self.parent.bind(shortcut, command)

		menuber.add_cascade(label = "Stock", menu = stockMenu, underline = 0)

		helpMenu = tk.Menu(menuber, tearoff = 0)
		for label, command, shortcut_text, shortcut in (
				("About ...",None, None, None,),
				# ("graph", 		lambda: self.showGraph("candle"), None, None,),
				# ("Win...",lambda : popumsg("Steven"), "Ctrl+p", "<Control-p>",)
				):
			if label is None:
				helpMenu.add_separator()
			else:
				helpMenu.add_command(label = label, underline = 0,
						command = command, accelerator = shortcut_text)
				self.parent.bind(shortcut, command)

		menuber.add_cascade(label = "Help", menu = helpMenu, underline = 0)

	def createBindSetting(self):
		parent = self.parent
		parent.bind("<Escape>", self.Quit )
		parent.bind("<Control-f>", self.search )


	def fileNew(self, event=None):
		PRINT("file new")
		pass

	def fileOpen(self, event=None):
		PRINT("file open")
		pass

	def search(self, event=None):
		self.statusBar.setStatus("search...")
		PageInfo["pageObject"].pageSearch()
		PRINT("search..")


	def showFrame(self, cont, event=None):
		frame = self.frames[cont]
		if not (frame == PageInfo["pageObject"]  ) :
			frame.setPageInfo()
			self.statusBar.setStatus("{0}".format(statusBarMessage[ PageInfo["mode"] ]))
			frame.updatePage()		
			frame.tkraise()
			# self.statusBar.set( "..." )

	def polling(self):
		"""
		polling data
		"""
		global PageInfo
		global winSetting
		# PRINT(PageInfo["mode"])
		if (PageInfo["mode"] == "StockPage"):
			PRINT("get stock")
			PageInfo["pageObject"].updatePage()


		elif (PageInfo["mode"] == "HousePage"):
			PRINT("get hourse data")


		else:
			pass

		# ## polling.
		self.afterId = self.parent.after( winSetting["sampling_period"], self.polling )

	def Quit(self, event=None):
		self.parent.after_cancel(self.afterId)
		self.quit()

###########  class 
class StockPage(ttk.Frame):
	"""
	docstring for StockPage



	"""
	global PageInfo
	def __init__(self, parent, controller = None):
		super(StockPage, self).__init__(parent)
		global STOCKDATA
		self.parent = parent
		self.setOk = True
		self.graph = None

		self.basicTodayList = [ '買價']
		self.basicList 		= ['開盤', '漲停價', '最高價', '買價', '買量', '最低價', '賣量', '昨收' ]
		self.priceList 		= ['最佳買價', '買量', '最佳賣價', '賣量']

		STOCKDATA = GetStock.get_realtime_stock_info(my_choice_stock)
		# PRINT(STOCKDATA)

		if not (STOCKDATA == 0):
			for x in STOCKDATA.keys():
				STOCK_ID_LIST[ STOCKDATA[x]['股票名稱'] ] =  x

			if (winSetting["stockLayout"] == 1):
				self.stockBasicPage()
			elif (winSetting["stockLayout"] == 2):
				self.stockBasicPage(side = "left")
				self.stockGraphPage(master = self, side = "right")
			else:
				pass

		else :
			self.setOk = False

	def featureStock(self, parentWin , side = "top"):
		"""
		stock page with feature element.

		"""
		frameStockBasicLocal = tk.LabelFrame(parentWin, 
			text = "今日行情", 
			background = BACK_GROUND_COLOR,
			foreground = FORE_GROUND_COLOR,
			# padx 	= 10,

			)
		frameStockBasicLocal.pack(side = side, fill = "both", padx = 4)
		frameStockBasicLocal.grid_rowconfigure(0, weight = 1)
		frameStockBasicLocal.grid_columnconfigure(0, weight = 1)


		self.stockDataTodayInfo = {}
		# today  = self.basicTodayList[0]
		# stockDataTodayInfo[today] = ttk.Label(frameStockBasicLocal,
		# 	textvariable = (self.basicToday[today]),
		# 	anchor = "nw",
		# 	font = NORM_FONT, 
		# 	# borderwidth = 20,
		# 	# width = 20,
		# 	# justify = "left",
		# 	)
		# stockDataTodayInfo[today].grid(row = 0, column = 0, sticky = "nsew")	

		today  = self.basicTodayList[0]
		color 	= FORE_GROUND_COLOR
		# good_flag = STOCKDATA[ PageInfo["stockChoice"] ][ '漲跌flag' ]
		good_flag = float(STOCKDATA[ PageInfo["stockChoice"] ][ '買價' ])- float(STOCKDATA[ PageInfo["stockChoice"] ][ '昨收' ])

		try:
			if ( good_flag > 0 ):
				color = STOCK_GOOD_COLOR
			elif (good_flag < 0 ) :
				color = STOCK_BAD_COLOR
		except NameError as err  :
			PRINT(err)


		self.stockDataTodayInfo[today] = tk.Label(frameStockBasicLocal,
			textvariable = (self.basicToday[today]),
			font = LARGE_FONT, 
			foreground = color,
			bg 	= BACK_GROUND_COLOR,
			# borderwidth = 20,
			# width = 20,
			# justify = "left",
			)
		self.stockDataTodayInfo[today].grid(row = 1, column = 1, sticky = "nsew")

	def stockBasicPage(self, side = "top"):
		"""
		the stock main function.		
		"""
		self.basicToday = {}
		for x in (self.basicTodayList):
			self.basicToday[x] = tk.StringVar()

		frameStockBasic = tk.Frame(self, 
			borderwidth = 0, 
			relief = "sunken",
			bg 	= BACK_GROUND_COLOR,
			)
		frameStockBasic.pack(side = side, fill = "both", expand = True)
		frameStockBasic.grid_rowconfigure(0, weight = 1)
		frameStockBasic.grid_columnconfigure(0, weight = 1)

		# # menu with appear stock name
		self.optionMenuString = tk.StringVar()

		for x in STOCK_ID_LIST :
			# PRINT( STOCK_ID_LIST[x])
			if ( STOCK_ID_LIST[x] == my_choice_stock[0] ):
				self.optionMenuString.set( x )

		self.optionMenu = tk.OptionMenu(frameStockBasic,
			self.optionMenuString, 
			*( STOCK_ID_LIST.keys() )	 )

		self.optionMenu.config(
			font = MID_FONT,
			bg = BACK_GROUND_COLOR,

			)
		self.optionMenu.pack(side = "top", fill = "x")

		# PRINT( self.optionMenuString.get() )

		# # 
		self.featureStock( frameStockBasic )

		frameStockBasicinfo = tk.LabelFrame(frameStockBasic, 
			text = "今日走勢",
			background = BACK_GROUND_COLOR,
			foreground = FORE_GROUND_COLOR, 
			)
		frameStockBasicinfo.pack(side = "top", fill = "both",expand = False, padx = 4)
		frameStockBasicinfo.grid_rowconfigure(0, weight = 1)
		frameStockBasicinfo.grid_columnconfigure(0, weight = 1)


		frameStockBasicPrice = tk.LabelFrame(frameStockBasic, 
			text = "最佳價量", 
			background = BACK_GROUND_COLOR,
			foreground = FORE_GROUND_COLOR,
			)
		frameStockBasicPrice.pack(side = "top", fill = "both", padx = 4)
		frameStockBasicPrice.grid_rowconfigure(0, weight = 1)
		frameStockBasicPrice.grid_columnconfigure(0, weight = 1)

		frameStockBasicglobal = tk.LabelFrame(frameStockBasic, 
			text = "全球走勢", 
			background = BACK_GROUND_COLOR,
			foreground = FORE_GROUND_COLOR,
			# pady 	= 10,
			# height = 150,
			 )
		frameStockBasicglobal.pack(side = "top", fill = "both", padx = 4, expand = True, pady = 2)
		frameStockBasicglobal.grid_rowconfigure(0, weight = 1)
		frameStockBasicglobal.grid_columnconfigure(0, weight = 1)


		self.priceString = {}
		self.stockDataPriceInfo = {}
		pos = 0
		for price in ( self.priceList ):		
			self.stockDataPriceInfo[price] = tk.Label(frameStockBasicPrice, 
				text = "{0}".format( price ), 
				font = SMALL_FONT, 
				bg 	= BACK_GROUND_COLOR,
				fg 	= FORE_GROUND_COLOR,
				# borderwidth = 20,
				# width = 20,
				# justify = "left",

				)

			self.stockDataPriceInfo[price].grid(row = 0, column = pos, sticky = "nsew")	
			self.stockDataPriceInfo[price].rowconfigure(0, weight = 1)
			self.stockDataPriceInfo[price].columnconfigure(0, weight = 1)
			self.stockDataPriceInfo[price].columnconfigure(1, weight = 1)
			self.stockDataPriceInfo[price].columnconfigure(2, weight = 1)
			self.stockDataPriceInfo[price].columnconfigure(3, weight = 1)

			self.priceString[price] = {}
			self.stockDataPriceInfo[price] = {}
			for x in range( PageInfo["priceLevel"]):
				self.priceString[price][x] = tk.StringVar()
				self.stockDataPriceInfo[price][x] = tk.Label(frameStockBasicPrice, 
					textvariable = ( self.priceString[price][x] ), 
					font = SMALL_FONT, 
					bg 	= BACK_GROUND_COLOR,
					fg 	= FORE_GROUND_COLOR,
					# borderwidth = 20,
					# width = 20,
					# justify = "left",

					)

				self.stockDataPriceInfo[price][x].grid(row = (x+1), column = pos, sticky = "nsew")	
				self.stockDataPriceInfo[price][x].rowconfigure(0, weight = 1)
				self.stockDataPriceInfo[price][x].columnconfigure(0, weight = 1)
				self.stockDataPriceInfo[price][x].columnconfigure(1, weight = 1)
				self.stockDataPriceInfo[price][x].columnconfigure(2, weight = 1)
				self.stockDataPriceInfo[price][x].columnconfigure(3, weight = 1)

			pos += 1	


		stockDataInfo = {}
		self.basicString = {}
		pos = 0
		for basic in ( self.basicList ):
			self.basicString[basic] = tk.StringVar()
			stockDataInfo[basic] = tk.Label(frameStockBasicinfo, 
				text = "{0}".format( basic ), 
				anchor = "nw",
				font = NORM_FONT, 
				bg 	= BACK_GROUND_COLOR,
				fg 	= FORE_GROUND_COLOR,
				# borderwidth = 100,
				# width = 20,
				# justify = "left",

				)

			stockDataInfo[basic].grid(row = pos, column = 0, sticky = "new")			
			stockDataInfo[basic].rowconfigure(0, weight = 1)
			stockDataInfo[basic].rowconfigure(1, weight = 1)
			stockDataInfo[basic].rowconfigure(2, weight = 1)
			stockDataInfo[basic].rowconfigure(3, weight = 1)
			stockDataInfo[basic].rowconfigure(4, weight = 1)
			stockDataInfo[basic].columnconfigure(0, weight = 1)

			stockDataInfo[basic] = tk.Label(frameStockBasicinfo, 
				textvariable = ( self.basicString[basic] ), 
				anchor = "ne",
				font = NORM_FONT, 
				bg 	= BACK_GROUND_COLOR,
				fg 	= FORE_GROUND_COLOR,				
				# borderwidth = 100,
				# width = 20,
				# justify = "left",

				)

			stockDataInfo[basic].grid(row = pos, column = 1, sticky = "new")
			stockDataInfo[basic].rowconfigure(0, weight = 1)
			stockDataInfo[basic].rowconfigure(1, weight = 1)
			stockDataInfo[basic].rowconfigure(2, weight = 1)
			stockDataInfo[basic].rowconfigure(3, weight = 1)
			stockDataInfo[basic].rowconfigure(4, weight = 1)
			stockDataInfo[basic].columnconfigure(0, weight = 1)

			pos += 1

	def stockGraphPage(self , master = None , side = "top"):
		"""
		the stock graph set.		
		"""
		# global fig
		stockCode 	= PageInfo["stockChoice"]
		self.graph = stockCode
		self.fig = plt.figure( 
			# 	# figsize 		= None,
			# 	# dpi 			= None,
				facecolor  		= BACK_GROUND_COLOR,
				edgecolor 		= BACK_GROUND_COLOR,
			# 	# linewidth 		= 0.0,
			# 	# frameon 		= None,
			# 	# subplotpars 	= None,
			# 	# tight_layout 	= None,
				)

		if (master == None):
			self.stockgraph = tk.Tk() 
			self.stockgraph.wm_title(  self.optionMenuString.get()  )
			master = self.stockgraph
			self.stockgraph.bind("<Escape>", self.Quit )

		frameStockgraph = tk.LabelFrame(master, 
			text = "技術分析", 
			background = BACK_GROUND_COLOR,
			# foreground = FORE_GROUND_COLOR,
			# padding = 5, 
			# borderwidth = 5,
			)

		frameStockgraph.pack(side = side, fill = "both", expand = True)

		frameStockgraph.grid_rowconfigure(0, weight = 1)
		frameStockgraph.grid_columnconfigure(0, weight = 1)

		self.canvas = FigureCanvasTkAgg(self.fig, frameStockgraph)
		# canvas.show()
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side = "top", fill = "both", expand = True)

		toolbar = NavigationToolbar2TkAgg(self.canvas, frameStockgraph)
		toolbar.update()
		self.canvas._tkcanvas.pack(side = "top", fill = "both", expand = True) 	

		# PageInfo["graphMode"] = "stock"

		# # update data
		if (self.get_historical_stock(stockCode)) :
			self.updateStockGraph(stockCode)

	# #  layout end.

	def get_historical_stock(self, stockCode):
		global STOCKMONTHDATA	
		global winSetting
		# e = 2

		days = int(winSetting["atLeastYear"])*365 + int(winSetting["atLeastMonth"])*31 + int(winSetting["atLeastDay"])
		date1 = datetime.datetime.today()
		
		# date1 = date1 - timedelta( days = e )   
		date2 = date1 - datetime.timedelta( days = days )   
		# delta = timedelta(days = 1)
		# dates = mdates.drange(date2, date1, delta)

		from_day 	= ( (date2.strftime("%Y,%m,%d")).split(",") )
		to_day 		= ( (date1.strftime("%Y,%m,%d")).split(",") )

		try :
			if stockCode in STOCKMONTHDATA.keys() :
				pass
			else :
				stockData = STOCKDATA[ PageInfo["stockChoice"] ]
				datesFun = mdates.date2num
				# PRINT( stockCode )
				self.stockHistoricalData = []
				self.volume = []
				# STOCKMONTHDATA[stockCode] = quotes_historical_yahoo_ohlc('{0}.{1}'.format( stockCode,PageInfo["stockPlace"] ), from_day, to_day)

				while (PageInfo["stopInternet"] == 1):
					pass

				PageInfo["stopInternet"] 	= 1
				STOCKMONTHDATA[stockCode]  	= GetStock.get_history_stock_info( stockCode, from_day , to_day )
				PageInfo["stopInternet"] 	= 0
				# PRINT(STOCKMONTHDATA[stockCode])

				cnt = 0
				for line in STOCKMONTHDATA[stockCode] :
					year, month, day = line[0].split("-")
					if (cnt == days):
						break

					if (cnt == 0 ):
						# PRINT( "EN")
						self.stockHistoricalData.append( ( datesFun( datetime.datetime( int(YEAR), int(MONTH), int(DAY) ) ), 
							float(stockData[ '開盤' ]),  	# open
							float(stockData[ '最高價' ]), 	# high
							float(stockData[ '最低價' ]), 	# low
							float(stockData[ '買價' ]), 	# close
							int(stockData[ '當盤成交量' ])		# volume   
							) )

						self.volume.append( float(stockData[ '買價' ]  ))
						# cnt += 1

					if int(line[5]) > 0 :

						# self.stockHistoricalData.append( ( dates[days - cnt-1], float(line[1]), float(line[2]), float(line[3]), float(line[4]), int(line[5])   ) )
						self.stockHistoricalData.append(( datesFun( datetime.datetime( int(year), int(month), int(day) ) ) , 
							float(line[1]), 
							float(line[2]), 
							float(line[3]), 
							float(line[4]), 
							int(line[5])   
							) )
						self.volume.append( int(line[5])  )
						# self.stockHistoricalData.append( ( line[0], float(line[1]), float(line[2]), float(line[3]), float(line[4]), int(line[5])   ) )

					cnt += 1	

				# PRINT( self.stockHistoricalData )	
				stockdataArray 	= np.array(self.stockHistoricalData )
				self.dates 		= stockdataArray.T[0]
				self.Open 		= stockdataArray.T[1]
				self.High 		= stockdataArray.T[2]
				self.Low 		= stockdataArray.T[3]
				self.Close 		= stockdataArray.T[4]
				# self.volume 	= stockdataArray.T[5]		
				# d = [x for x in self.dates]

		except urllib.error.URLError as err :
			PRINT(err)
			self.parent.statusBar.setMessage("{0}".format(  " no internet"   ))
			return 0
		else:		
			return 1

	def pageSearch(self, para):
		PageInfo["stockChoice"] = str(para)
		self.updatePage()

	def setPageInfo(self):
		PageInfo["mode"] = "StockPage"
		PageInfo["pageObject"] = self

	def pageOk(self):
		return self.setOk

	def Quit(self, event = None):
		# PRINT(event)
		# PageInfo["graphMode"] = None
		self.quit()

	def updateStockGraph(self, stockCode ):
		global STOCKMONTHDATA
		global MONTH_FORMATTER
		global MONTHS
		global ALLDAYS

		fig = self.fig
		data = self.stockHistoricalData
		dates 	= self.dates
		Open 	= self.Open
		High 	= self.High
		Low 	= self.Low
		Close 	= self.Close
		volume 	= self.volume
		date = [x for x in self.dates]


		figA = plt.subplot2grid((10,4), (0,0), rowspan = 6, colspan = 4)
		figB = plt.subplot2grid((10,4), (7,0), rowspan = 3, colspan = 4, sharex = figA)

		#####
		figA.clear()
		figB.clear()

		figA.xaxis.set_major_locator(MONTHS)
		figA.xaxis.set_minor_locator(ALLDAYS)
		# figA.xaxis.set_major_locator(LOCATOR)
		figA.xaxis.set_major_formatter(MONTH_FORMATTER)
		figA.autoscale_view()

		# PRINT( self.stockHistoricalData )

		candlestick_ohlc(figA, data, 
			# width		=0.2, 
			colorup		='g', 
			colordown	='r', 
			alpha		=0.8
			)

		figA.plot(dates, Close, "-" , linewidth = 0.7 )

		# figA.legend(
		# 	bbox_to_anchor=(0., 1.02, 1., .102),
		# 	loc="upper right",
		# 	ncol=2, 
		# 	borderaxespad=0. 
		# 	)

		# ## plot
		# PRINT(volume)
		barlist = figB.bar(date,volume,
			width = 0.5,

			)
		for i in range(len(date)):
			if Open[i]<Close[i]:
				barlist[i].set_color('r')
			else:
				barlist[i].set_color('g')
		
		# figB.legend(
		# 	bbox_to_anchor=(0., 1.0, 1., .10),
		# 	loc=1,
		# 	ncol=2, 
		# 	borderaxespad=0.
		# 	)
		
		# # rodate x axis
		plt.setp(plt.gca().get_xticklabels(), rotation=30)

		# # update draw
		self.canvas.draw()
		self.canvas.flush_events()

	def updatePage(self):
		global STOCKDATA
		global STOCKMONTHDATA
		global GS
		# global fig_data

		if not ( STOCK_ID_LIST[self.optionMenuString.get()] == PageInfo["stockChoice"]) :
			# PRINT(self.optionMenuString.get() )
			PageInfo["stockChoice"] = STOCK_ID_LIST[self.optionMenuString.get()]

		stockCode = PageInfo["stockChoice"]
		PageInfo["stockName"] = self.optionMenuString.get()

		if (FIRST_FRAME == True):
			# STOCKDATA = GetStock.get_realtime_stock_info(my_choice_stock)	
			# PRINT("first frame")
			pass
		else :
			if ( PageInfo["stopInternet"] == 0 ):
				PageInfo["stopInternet"] = 1
				STOCKDATA = GetStock.get_realtime_stock_info(stockCode)	
				PageInfo["stopInternet"] = 0


		if ( STOCKDATA != 0 ):
			stock = STOCKDATA[stockCode]
			# PRINT(stock)

			# pprint.pprint(STOCKDATA)
			for x in (self.basicTodayList):
				# PRINT(x)
				self.basicToday[x].set( stock[x] )

				if (x == '買價'):
					color = FORE_GROUND_COLOR
					good_flag = float(STOCKDATA[ PageInfo["stockChoice"] ][ '買價' ])- float(STOCKDATA[ PageInfo["stockChoice"] ][ '昨收' ])
					try:
						if ( good_flag > 0 ):
							color = STOCK_GOOD_COLOR
						elif (good_flag < 0 ) :
							color = STOCK_BAD_COLOR
					except NameError as err  :
						PRINT(err)
					# # update cofigure
					self.stockDataTodayInfo[x].config( foreground 	= color , )
					self.stockDataTodayInfo[x].update_idletasks()

			for x in (self.basicList):
				# PRINT(x)
				if x in ( '買量', '賣量' ) :
					self.basicString[x].set( stock[x][0] )
				else :
					self.basicString[x].set( stock[x] )

			MaxSell = 0
			LabelSell = None
			MaxBuy = 0
			LabelBuy = None
			temp = 0
			for x in (self.priceList):
				for y in range(PageInfo["priceLevel"]):
					self.priceString[x][y].set( stock[x][y] )
					temp = float(stock[x][y])
					# self.stockDataPriceInfo[x][y].config( foreground 	= FORE_GROUND_COLOR)
					# self.stockDataPriceInfo[x][y].update_idletasks()
					if ( x == "買量" and temp > MaxBuy ):
						MaxBuy = temp
						LabelBuy = y
						# PRINT( stock[x][y] )
					elif ( x == "賣量" and temp > MaxSell ):
						MaxSell = temp
						LabelSell = y

			# ## pre
			if not (FIRST_FRAME):
				self.stockDataPriceInfo["買量"][self.LabelBuy_pre].config( 		foreground 	= FORE_GROUND_COLOR, underline = 2 )
				self.stockDataPriceInfo["最佳買價"][self.LabelBuy_pre].config( 	foreground 	= FORE_GROUND_COLOR, underline = 2 )
				self.stockDataPriceInfo["賣量"][self.LabelSell_pre].config( 		foreground 	= FORE_GROUND_COLOR, underline = 2 )
				self.stockDataPriceInfo["最佳賣價"][self.LabelSell_pre].config( 	foreground 	= FORE_GROUND_COLOR, underline = 2 )		

			self.stockDataPriceInfo["買量"][LabelBuy].config( 		foreground 	= STOCK_GOOD_COLOR, underline = 2 )
			self.stockDataPriceInfo["最佳買價"][LabelBuy].config( 	foreground 	= STOCK_GOOD_COLOR, underline = 2 )
			self.stockDataPriceInfo["賣量"][LabelSell].config( 		foreground 	= STOCK_GOOD_COLOR, underline = 2 )
			self.stockDataPriceInfo["最佳賣價"][LabelSell].config( 	foreground 	= STOCK_GOOD_COLOR, underline = 2 )

			if not (FIRST_FRAME):
				self.stockDataPriceInfo["買量"][self.LabelBuy_pre].update_idletasks()
				self.stockDataPriceInfo["最佳買價"][self.LabelBuy_pre].update_idletasks()
				self.stockDataPriceInfo["賣量"][self.LabelSell_pre].update_idletasks()
				self.stockDataPriceInfo["最佳賣價"][self.LabelSell_pre].update_idletasks()

			self.stockDataPriceInfo["買量"][LabelBuy].update_idletasks()
			self.stockDataPriceInfo["最佳買價"][LabelBuy].update_idletasks()
			self.stockDataPriceInfo["賣量"][LabelSell].update_idletasks()
			self.stockDataPriceInfo["最佳賣價"][LabelSell].update_idletasks()					


			self.LabelBuy_pre = LabelBuy
			self.LabelSell_pre = LabelSell

		else :
			self.parent.statusBar.setMessage("can not get stock data {0}.".format(stockCode))
		
		# ### update graph
		if not ( self.graph == None ):
			self.graph = PageInfo["stockChoice"]
			if not ( self.graph in STOCKMONTHDATA.keys()  ):
				if (self.get_historical_stock(self.graph)) :
					# PRINT( self.stockHistoricalData )
					self.updateStockGraph(self.graph)
			else :
				pass
				# self.updateStockGraph(self.graph)

#####  class house page
class HousePage(ttk.Frame):
	"""
	docstring for HousePage
	"""
	global PageInfo
	def __init__(self, parent, controller = None):
		super(HousePage, self).__init__(parent)
		
		self.setOk = True
		# PageInfo["mode"] = "HousePage"

		label = ttk.Label(self, text = "HousePage" )
		label.pack(padx = 10, pady = 10)

		button = ttk.Button(self, text = "button")
		button["command"] = lambda: parent.showFrame(StockPage)
		button.pack()		

	def pageSearch(self, para):
		# PageInfo["stockChoice"] = str(para)
		self.updatePage()

	def setPageInfo(self):
		PageInfo["mode"] = "HousePage"
		PageInfo["pageObject"] = self

	def pageOk(self):
		return self.setOk

	def updatePage(self):
		pass


# the element of status bar
class StatusBar(ttk.Frame):

    def __init__(self, master):
        super(StatusBar, self).__init__(master)

        # # 	message init
        self.message = ttk.Label(self, 
        	relief="sunken", 
        	anchor="w", 
        	text = "wait...",
        	background = STATUS_BAR_COLOR,
        	foreground = STATUS_FORE_GROUND_COLOR,
        	)
        self.message.pack(fill="x", side = "left", expand = True, ipadx = 1, ipady = 1)

        # # status init
        self.status = ttk.Label(self, 
        	relief="sunken", 
        	anchor="e",
        	background = STATUS_BAR_COLOR,
        	foreground = STATUS_FORE_GROUND_COLOR,
        	)
        self.status.pack(fill="x", side = "right",expand = False, ipadx = 5, ipady = 1)


    def setStatus(self, format, *args):
        self.status.config(text = format % args)
        self.status.update_idletasks()

    def clearStatus(self):
        self.status.config(text="")
        self.status.update_idletasks()

    def setMessage(self, format, *args):
        self.message.config(text=format % args)
        self.message.update_idletasks()

    def clearMessage(self):
        self.message.config(text="")
        self.message.update_idletasks()



### global function

## in time function.
def LoadToolSetting():
	global CONFIG_FILE
	global my_choice_stock
	global winSetting

	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)

	for section in config.sections():
		x = config[section]
		if (section == "gui"):
			winSetting["sampling_period"] 	=  int(x["sampling_period"])
			winSetting["atLeastDay"] 		=  int(x["atLeastDay"])
			winSetting["atLeastMonth"] 		=  int(x["atLeastMonth"])
			winSetting["atLeastYear"] 		=  int(x["atLeastYear"])
			winSetting["stockLayout"] 		=  int(x["stockLayout"])
			
		elif ( section == "stock" ):
			
			my_choice_stock = x["my_choice_stock"].split("/")

		elif ( section == "house" ):
			pass

		else:
			pass

	# PRINT(winSetting )

	# SaveToolSetting()

def SaveToolSetting(mode = None):
	global CONFIG_FILE

	config = configparser.ConfigParser()
	# PRINT( "|".join(my_choice_stock) )

	# set default
	if (mode == 1):
		config["gui"] = {}
		config["gui"]["sampling_period"] = 1000
		config["gui"]["atLeastDay"] = 0
		config["gui"]["atLeastMonth"] = 6
		config["gui"]["atLeastYear"] = 0
		config["gui"]["stockLayout"] = 1
		config["stock"] = {}
		config["stock"]["my_choice_stock"] = "0050"
		config["house"] = {}

	else:
		config["stock"]["my_choice_stock"] = "/".join(my_choice_stock)


	# ## write to file
	with open( CONFIG_FILE, "w" ) as configfile :
		config.write(configfile)

def PRINT(pram):
	with open(LOG_FILE,"a",encoding = SYSTEM_CODE) as f :
		# f.write(str(pram)+"\n")
		# print(pram, file = f)
		pprint.pprint(pram )
		pprint.pprint(pram, stream = f)

def popumsg(msg):
	popu = tk.Tk()
	popu.wm_title("ERROR MESSAGE!")
	popuframe = tk.Frame(popu )
	popuframe.pack()

	label = ttk.Label(popuframe, text = msg, font = LARGE_FONT)
	label.pack(side = "top", fill = "x", pady = 20, padx = 20)
	bu = tk.Button(popu, text = "Okey", command = popu.destroy)
	bu.pack(side = "bottom", fill = "both",pady = 5)



if __name__ == "__main__":
	LoadToolSetting()
	root = tk.Tk()
	win = InvestmentGUI(master = root)
	root.protocol("WM_DELETE_WINDOW", win.Quit )
	root.afterId = root.after(winSetting["sampling_period"], win.polling)
	FIRST_FRAME = False
	win.mainloop()





