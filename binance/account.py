import requests, json, hashlib, hmac, datetime, urllib
import numpy as np
import binance.market as market

class account:
	def __init__(self, api_key, secret_key):
		self.api_key, self.secret_key = api_key, secret_key
		self.get_account_balance()

		self.market_filters = {}

		self.exchange_info = json.loads(requests.get('https://api.binance.com/api/v3/exchangeInfo').text)
		for symbol in self.exchange_info['symbols']:
			self.market_filters[symbol['symbol']] = {}

			self.market_filters[symbol['symbol']]['precision'] = int(symbol['baseAssetPrecision'])
			self.market_filters[symbol['symbol']]['precision_quote'] = int(symbol['quoteAssetPrecision'])
			
			#self.market_filters[symbol['symbol']]['precision_quote'] = 2
			#self.market_filters[symbol['symbol']]['precision'] = 2


			for filter in symbol['filters']:
				if filter['filterType'] == 'LOT_SIZE':
					self.market_filters[symbol['symbol']]['min_order'] = float(filter['minQty'])
					self.market_filters[symbol['symbol']]['max_order'] = float(filter['maxQty'])
					self.market_filters[symbol['symbol']]['step_size'] = float(filter['stepSize'])
				if filter['filterType'] == 'MIN_NOTIONAL':
					self.market_filters[symbol['symbol']]['min_order_quote'] = float(filter['minNotional'])




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
		print('\n ', currency, quote, side, quote_volume, volume)

		ts = int(datetime.datetime.now().timestamp() * 1000)

		#check to see if the currency and quote are the correct way around, and if not fix this
		if quote + currency in self.market_filters:
			print('switching')
			return self.market(quote, currency,'BUY' if side == 'SELL' else 'SELL',not quote_volume, volume) 

		precision = self.market_filters[currency + quote]['precision']
		precision_quote = self.market_filters[currency + quote]['precision_quote']

		form = "{:."+ str(precision) + "f}"
		form_quote = "{:."+ str(precision_quote) + "f}"


		vol = 0

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
					return 0

				volume = np.floor(np.abs(volume) / self.market_filters[currency + quote]['step_size']) * self.market_filters[currency + quote]['step_size']
				params['quantity'] = form.format(np.abs(volume))
				vol = params['quantity']
				#execute trade
			elif side == 'BUY':
				quote_volume = self.balances[quote]
				if quote_volume == 0:
					return 0

				params['quoteOrderQty'] = form_quote.format(np.abs(quote_volume))
				vol = params['quoteOrderQty']

				#execute trade
		else:
			if quote_volume:
				params['quoteOrderQty'] = form_quote.format(np.abs(volume))
				vol = params['quoteOrderQty']
			else:
				volume = np.floor(np.abs(volume) / self.market_filters[currency + quote]['step_size']) * self.market_filters[currency + quote]['step_size']
				params['quantity'] = form.format(np.abs(volume))
				vol = params['quantity']

		signature = self.generate_signature(params)
		params['signature'] = signature


		if 'quantity' in params:
			print(float(params['quantity']), self.market_filters[currency + quote]['min_order'])
			if float(params['quantity']) < self.market_filters[currency + quote]['min_order']:
				print(currency + quote +' trade below min order')
				return 0
		elif 'quoteOrderQty' in params:
			if float(params['quoteOrderQty']) < self.market_filters[currency + quote]['min_order_quote']:
				print(currency + quote + 'trade below min order')
				return 0



		if float(vol) == 0:
			return 0
		req = requests.post('https://api.binance.com/api/v3/order/test', params=params, headers=headers)
		if req.status_code == 200:
			return float(vol)
		else:
			print(req.text, currency + quote, params)
			print(self.market_filters[currency + quote])
			return 0

	def trade_to_portfolio(self, base, quotes, currencies, portfolio, prices=None):
		if prices is None:
			prices = np.array([1] + [np.mean(market.prices([a + base for a in quotes + currencies])[b + base]) for b in quotes + currencies])

		#normalise the portfolio
		portfolio = np.abs(portfolio) / np.sum(portfolio)

		#get the current portfolio
		current_portfolio = np.array([self.balances[a] if a in self.balances else 0.0 for a in [base] + quotes + currencies])
		print(portfolio, np.sum(current_portfolio * prices))
		
		current_portfolio_weighted = current_portfolio * prices / np.sum(current_portfolio * prices)

		trade_in_base = (portfolio - current_portfolio_weighted) * np.sum(current_portfolio * prices)

		#sell excess currencies to base
		currency_sells = np.zeros(portfolio.size)
		currency_sells[-len(currencies):] = trade_in_base[-len(currencies):]

		print(trade_in_base, currency_sells)

		for i, (currency, base_volume) in enumerate(zip([base] + quotes + currencies, currency_sells)):
			if base_volume >= 0:
				continue

			#check whether we are basically liquidating the asset (< 1% remaining) to avoid overspend issues, otherwise give the full volume to sell
			if portfolio[i] < 0.01:

				self.market(currency, base, 'SELL')


			else:
				print(-base_volume)
				self.market(currency, base, 'SELL', True, -base_volume)
			
			trade_in_base[i] = 0
			trade_in_base[0] += base_volume

		#now sell from the quotes to the deficit currencies
		for i, quote in enumerate([base] + quotes):
			#see if the trade is less than 0 and then sell 
			if trade_in_base[i] < 0:
				for j, currency in enumerate([base] + quotes + currencies):
					#see if we need to buy the currency 
					if trade_in_base[j] > 0:
						#test whether we can buy all of the asset with the current quote asset, otherwise liquidate quote into currency
						if -trade_in_base[i] > trade_in_base[j]:
							volume = trade_in_base[j] / prices[j]
							print(trade_in_base[j])
							self.market(currency, quote, 'BUY', False, volume)
							trade_in_base[i] += volume
							trade_in_base[j] = 0
						else:
							self.market(currency, quote, 'BUY')
							volume = trade_in_base[i] / prices[i]
							print(trade_in_base[i])
							trade_in_base[i] = 0
							trade_in_base[j] += volume

	def limit_order(market, amount, price):
		pass
