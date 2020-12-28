import sqlite3

from urllib.request import pathname2url


def setup(database, currencies):
	#create table for price history
	db = 'data/pricehistory.py'

	try:
    	dburi = 'file:{}?mode=rw'.format(pathname2url(db))
    	conn = sqlite3.connect(dburi, uri=True)
	except sqlite3.OperationalError:
 		conn = sqlite3.connect(db)
 			columns = ''


		for market in currencies:
			columns += market + 'bid float, ' + market + 'ask float'
		
		c.execute('CREATE TABLE CANDLES (id integer PRIMARY KEY, time integer, ' + columns[:-1] + ');')


def addprices(db, prices, currencies):
	pass

def getprices(db, currencies):
	pass


	#create trade history table