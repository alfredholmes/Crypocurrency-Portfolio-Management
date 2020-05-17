"""
Script to Download Hourly data from the binance REST API

Author: Alfred Holmes, https://github.com/alfredholmes

"""

import requests, json, sqlite3, datetime


#MARKETS = ['BTCUSDT', 'ETHBTC', 'BNBBTC', 'EOSBTC']
MARKETS = ['BTCUSDT', 'ETHBTC']
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
	c.execute('CREATE TABLE CANDLES (id integer PRIMARY KEY, open_time integer, close_time integer' + columns + ');')


	start_ms = int(START_DATE.timestamp() * 1000)
	#end_ms = int(END_DATE.timestamp() * 1000)
	end_ms = start_ms + 5 * INTERVALS[INTERVAL]

	current_ms = start_ms

	candle_data = []
	while  current_ms < end_ms:
		print((end_ms - current_ms) / INTERVALS[INTERVAL])
		interval = []
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

			if interval == []:
				interval = candles
			else:
				for i, (row, addition) in enumerate(zip(interval, candles)):
					interval[i] += addition[1:]
					if interval[i][0] - addition[0] > INTERVALS[INTERVAL]:
						print(interval[i][0] - addition[0])
						print('OUT OF SYNC')

		current_ms += INTERVALS[INTERVAL]
		
		candle_data += interval

	for candle in candle_data:
		columns = 'open_time'
		data = str(candle[0])
		for i, market in enumerate(MARKETS):
			open_price = candle[1 + i * 11 + 0]
			close_price = candle[1 + i * 11 + 3]

			data += ', ' + str(open_price) + ', ' + str(close_price)

			columns += ', ' + market + '_OPEN'
			columns += ', ' + market + '_CLOSE'

		print(columns, data)
		c.execute('INSERT INTO CANDLES (' + columns + ') VALUES (' + data +')')


			
	db.commit()
	

		

	start_ms + INTERVALS[INTERVAL]

if __name__ == '__main__':
	main()