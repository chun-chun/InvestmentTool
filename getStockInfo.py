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


# import urllib.request
# import urllib.parse
# import requests
# from bs4 import BeautifulSoup
# import datetime
# import json
# import sys
# import os
# import csv







# main function
def main():

	aapl = pdr.get_data_yahoo('AAPL', 
		start=datetime.datetime(2006, 10, 1), 
		end=datetime.datetime(2012, 1, 1))

	data = aapl.head()



	print(data)

if __name__ == '__main__':
	main()

