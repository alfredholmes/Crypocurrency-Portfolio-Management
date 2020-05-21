"""
Script to Download Hourly data from the binance REST API

Author: Alfred Holmes, https://github.com/alfredholmes

"""

import requests, json, sqlite3, datetime


#MARKETS = ['BTCUSDT', 'ETHBTC', 'BNBBTC', 'EOSBTC']
MARKETS = ['BTCUSDT', 'ETHBTC']
START_DATE = datetime.datetime(year=2018, month=1, day=1)
END_DATE = datetime.datetime.now()
INTERVAL = '30m'
INTERVALS = {
			 '1m': 60 * 60 * 1000,
			 
			 '3m': 3 * 60 * 60 * 1000, 
			 '5m': 5 * 60 * 60 * 1000, 
			 '15m': 15 * 60 * 60 * 1000, 
			 '30m': 30 * 60 * 60 * 1000, 
			 '1h':  60 * 60 * 1000, 
			 
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


def fix_data(times, intervals, time_step):
	if times[0] != intervals[0][0]:
		#1st entry missing, copy first entry to get the missing times
		row = intervals[0]
		number_missing = int((row[0] - times[0]) / time_step)
		for i in range(number_missing):
			row[0] = times[0] + i * time_step
			intervals.append([r for r in row])

	missing = []

	for i, time in enumerate(times):
		if time != intervals[i - len(missing)][0]:
			number_missing = int((intervals[i - len(missing)][0] - time) / time_step)
			
			for j in range(number_missing):
				missing.append(i + j)

	
	for i, j in enumerate(missing):
		new_time = times[0] + j * time_step
		print(new_time)
		old_row = intervals[i + j - 1]
		new_row = [r for r in old_row]
		new_row[0] = new_time 
		intervals.insert(i + j, new_row)

	for k, (i, j) in enumerate(zip(times, intervals)):
		if i != j[0]:
			print(k, i - j[0])

	return intervals



def main():
	db = sqlite3.connect(DATABASE)
	c = db.cursor()
	columns = ''
	for market in MARKETS:
		columns += ', ' + market + '_OPEN float, ' + market + '_CLOSE float,' + market + '_HIGH float,' + market + '_LOW float,' + market + '_VOLUME float'
	
	c.execute('DROP TABLE CANDLES') 
	c.execute('CREATE TABLE CANDLES (id integer PRIMARY KEY, open_time integer, close_time integer' + columns + ');')


	start_ms = int(START_DATE.timestamp() * 1000)
	#end_ms = int(END_DATE.timestamp() * 1000)
	end_ms = start_ms + 5 * INTERVALS[INTERVAL] * 1000

	current_ms = start_ms

	candle_data = []
	while  current_ms < end_ms:
		print((end_ms - current_ms) / INTERVALS[INTERVAL])
		times = [current_ms + i * INTERVALS[INTERVAL] for i in range(LIMIT)]
		interval = []
		
		for market in MARKETS:

			params = {
				'symbol': market,
				'interval': INTERVAL,
				'startTime': current_ms,
				'endTime': current_ms + LIMIT * INTERVALS[INTERVAL],
				'limit': LIMIT
			}
			r = requests.get('https://api.binance.com/api/v3/klines', params=params)
			
			try:
				candles = json.loads(r.text)
			except json.decoder.JSONDecodeError:
				print('error decoding json')
				continue

			if interval == []:
				interval = fix_data(times, candles, INTERVALS[INTERVAL])
			else:
				candles = fix_data(times, candles, INTERVALS[INTERVAL])
				for i, (row, addition) in enumerate(zip(interval, candles)):
					interval[i] += addition[1:]
					if interval[i][0] - addition[0] > INTERVALS[INTERVAL]:
						print((interval[i][0] - addition[0]) / INTERVALS[INTERVAL])
						print('OUT OF SYNC')

		current_ms += 1000 * INTERVALS[INTERVAL]
		
		candle_data += interval

	for candle in candle_data:
		columns = 'open_time'
		data = str(candle[0])
		for i, market in enumerate(MARKETS):
			open_price = candle[1 + i * 11 + 0]
			close_price = candle[1 + i * 11 + 3]
			high_price = candle[1 + i * 11 + 3]
			low_price = candle[1 + i * 11 + 3]
			volume = candle[1 + i * 11 + 3]

			data += ', ' + str(open_price) + ', ' + str(close_price)

			columns += ', ' + market + '_OPEN'
			columns += ', ' + market + '_CLOSE'
			columns += ', ' + market + '_HIGH'
			columns += ', ' + market + '_LOW'
			columns += ', ' + market + '_VOLUME'

		c.execute('INSERT INTO CANDLES (' + columns + ') VALUES (' + data +')')


			
	db.commit()
	

		

	start_ms + INTERVALS[INTERVAL]

if __name__ == '__main__':
	main()