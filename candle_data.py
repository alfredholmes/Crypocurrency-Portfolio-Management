import sqlite3


class Candles:
	def __init__(self, database='data/candles.db'):
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
def main():
	database = Candles()
	print(database.get_candles())


if __name__ == '__main__':
	main()