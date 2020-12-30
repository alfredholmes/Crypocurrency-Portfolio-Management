import requests, json, hashlib, hmac, datetime, urllib
import numpy as np
import binance.market as market

class account:
	def __init__(self, api_key, secret_key):
		self.api_key, self.secret_key = api_key, secret_key
		self.get_account_balance()


	def generate_signature(self, params):
		return hmac.new(self.secret_key.encode('utf-8'), urllib.parse.urlencode(params).encode('utf-8'), hashlib.sha256).hexdigest()


	def get_account_balance(self):
		ts = int(datetime.datetime.now().timestamp() * 1000)
		
		params = {
			'timestamp': str(ts)
		}
		
		headers = {
			"X-MBX-APIKEY": self.api_key
		}

		signature = self.generate_signature(params)
		params['signature'] = signature

		r = requests.get('https://api.binance.com/api/v3/account', headers=headers, params=params)

		account = json.loads(r.text)


		self.balances = {asset['asset'] : float(asset['free']) for asset in account['balances'] if float(asset['free']) != 0}
		return self.balances

	def get_portfolio_weighted(self, assets):
		self.get_account_balance()
		prices = np.array([1] + [np.mean(market.prices([a + 'USDT' for a in assets[1:]])[b + 'USDT']) for b in assets[1:]])
		account = np.array([self.balances[a] if a in self.balances else 0.0 for a in assets])

		return account * np.array(prices) / np.sum(account * np.array(prices))



	def market(self, currency, quote, side, quote_volume=False, volume=None):
		ts = int(datetime.datetime.now().timestamp() * 1000)

		if volume is not None and volume == 0.0:
			return

		params = {
			'timestamp': str(ts),
			'symbol': currency + quote,
			'type': 'MARKET',
			'side': side
		}

		headers = {
			"X-MBX-APIKEY": self.api_key
		}

		market = currency + quote
		if volume is None:
			#execute maximum trade
			if side == 'SELL':
				volume = self.balances[currency]
				if volume == 0:
					return
				params['quantity'] = np.abs(volume)
				#execute trade
			elif side == 'BUY':
				quote_volume = self.balances[quote]
				if quote_volume == 0:
					return

				params['quoteOrderQty'] = np.abs(quote_volume)

				#execute trade
		else:
			if quote_volume:
				params['quoteOrderQty'] = np.abs(volume)
			else:
				params['quantity'] = np.abs(volume)

		signature = self.generate_signature(params)
		params['signature'] = signature

		print(params)

		r = requests.post('https://api.binance.com/api/v3/order/test', params=params, headers=headers)
		print(r)
		print(r.text)

	def limit_order(market, amount, price):
		pass
