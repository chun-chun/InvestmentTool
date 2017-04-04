##################################
#	Purpose : fetch Stock data.
#	Version : 1.0
#	Author	: Stenen Yu
#	Release	:
#	
##################################


import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import os
import pandas_datareader as pdr
import matplotlib.pyplot as plt
plt.style.use('ggplot')
# import numpy as np

# main function
def main():
 
	stockId = 2317

	startDay = datetime.datetime(2017, 3, 15)
	endDay = datetime.datetime(2017, 4, 4)

	stockId = str(stockId) + ".tw"
	stockAllData = pdr.get_data_yahoo(stockId, startDay, endDay)

	closeData = stockAllData["Adj Close"]
	closeData.plot()
	plt.legend()	
	plt.show()
	# plt.figure()

	# writer = pd.ExcelWriter('output.xlsx')
	# stockAllData.to_excel(writer,'Sheet1')
	# writer.save()

	print(closeData)

if __name__ == '__main__':
	main()

