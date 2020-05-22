
"""
Class to handle loading data from the sqlite3 database once ./get_trading_data.py has been run to aquire the candlestick data

Author: Alfred Holmes, https://github.com/alfredholmes
"""

import sqlite3

class Candles:
	def __init__(self, database='data/candles_1h.db'):
		self.conn = sqlite3.connect(database)
		self.cursor = self.conn.cursor()

	def get_candles(self):
		r = self.cursor.execute('SELECT * FROM CANDLES')
		headers = [x[0] for x in r.description]
		candles = []
		for line in r:
			candle = {title: d for title, d in zip(headers, line)}
			candles.append(candle)
		return candles



