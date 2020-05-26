import sqlite3
import datetime

class candleLoader:
	def __init__(self, database, start_time=0, end_time=datetime.datetime.now().timestamp() * 1000):
		self.conn = sqlite3.connect(database)
		self.cursor = self.conn.cursor()
		self.r = self.cursor.execute('SELECT * FROM CANDLES WHERE open_time > ' + str(start_time) + ' AND open_time <' + str(end_time))
		self.headers = [x[0] for x in self.r.description]
		
	def __iter__(self):
		return self

	def __next__(self):
		next_candle = next(self.r)
		return {title: d for title, d in zip(self.headers, next_candle)}




	