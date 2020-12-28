import requests, json


def price(symbol):
	params = {
		'symbol': symbol,
		'limit': 5
	}
	request = json.loads(requests.get('https://api.binance.com/api/v3/depth', params=params).text)
	return request['bids'][0][0], request['asks'][0][0]

def prices(symbols):
	request = json.loads(requests.get('https://api.binance.com/api/v3/ticker/bookTicker').text)
	data = {}
	for book in request:
		if book['symbol'] in symbols:
			data[book['symbol']] = [book['bidPrice'], book['askPrice']]

	return relevant