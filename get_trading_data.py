"""
Script to Download Hourly data from the binance REST API

Author: Alfred Holmes, https://github.com/alfredholmes

"""

import requests, json, sqlite3, datetime


#MARKETS = ['BTCUSDT', 'ETHBTC', 'BNBBTC', 'EOSBTC']
MARKETS = ['BTCUSDT']
START_DATE = datetime.datetime(year=2018, month=1, day=1)
END_DATE = datetime.datetime.now()
INTERVAL = '1h'
INTERVALS = {
			 '1m': 60 * 60 * 1000,
			 
			 '3m': 3 * 60 * 60 * 1000, 
			 '5m': 5 * 60 * 60 * 1000, 
			 '15m': 15 * 60 * 60 * 1000, 
			 '30m': 30 * 60 * 60 * 1000, 
			 '1h':  60 * 60 * 60 * 1000, 
			 
			 '2h': 2 * 60 * 60 * 60 * 1000, 
			 '4h': 4 * 60 * 60 * 60 * 1000, 
			 '6h': 6 * 60 * 60 * 60 * 1000, 
			 '8h': 8 * 60 * 60 * 60 * 1000, 

			 '12h': 12 * 60 * 60 * 60 * 1000, 
			 '1d':  24 * 60 * 60 * 60 * 1000, 

			 '3d': 3 * 24 * 60 * 60 * 60 * 1000, 
			 '1w': 7 * 24 * 60 * 60 * 60 * 1000
			}
LIMIT = 1000 #number of candles to return

DATABASE = 'data/candles.db'


def main():
	db = sqlite3.connect(DATABASE)
	c = db.cursor()
	columns = ''
	for market in MARKETS:
		columns += ', ' + market + '_OPEN float, ' + market + '_CLOSE float' 
	#c.execute('CREATE TABLE CANDLES (id integer PRIMARY KEY, open_time integer, close_time integer' + columns + ');')


	start_ms = int(START_DATE.timestamp() * 1000)
	end_ms = int(END_DATE.timestamp() * 1000)

	candle_data = {market: [] for market in MARKETS}
	times = set()
	while  start_ms < end_ms:
		break
	for market in MARKETS:

		params = {
			'symbol': market,
			'interval': INTERVAL,
			'startTime': start_ms,
			'endTime': start_ms + LIMIT * INTERVALS[INTERVAL],
			'limit': 1000
		}
		r = requests.get('https://api.binance.com/api/v3/klines', params=params)
		
		try:
			candles = json.loads(r.text)
		except json.decoder.JSONDecodeError:
			print('error decoding json')
			continue

		candle_data[market] += candles
		for candle in candles:
			times.add(candle[0])

		


		

	start_ms + INTERVALS[INTERVAL]

if __name__ == '__main__':
	main()