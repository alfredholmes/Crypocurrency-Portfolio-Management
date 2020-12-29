from binance.account import account
import binance.market as market
from data.candles import candleLoader
from portfolioManagement.portfolioManagement import MAMRPortfolioManager
import pickle

import datetime
import numpy as np

MAMR_MGR = 'data.pkl'
BINANCE_BOT = 'bot.pkl'

#Currencies to Include in selection
CURRENCIES = ['ETH', 'EOS', 'FTT', 'LTC', 'BCH', 'ADA']
#Quote Assets
QUOTES = ['BTC', 'BNB']
RISKLESS = 'USDT'


DATABASE = 'data/candles_12h.db'

class binanceBot:
	def __init__(self, api, secret, saved=None, n=26):
		self.account = account(api, secret)

		if saved is not None:
			try:
				with open(saved, 'rb') as file:
					loaded = pickle.load(file)
					self.manager = loaded.manager
					self.prices = loaded.prices
					self.returns = loaded.returns
					self.update_times = loaded.update_times
					self.portfolio = loaded.portfolio
					return
			except FileNotFoundError:
				pass

		#get the portfolio...
		self.manager = MAMRPortfolioManager(len(CURRENCIES) + len(QUOTES) + 1, 4.105, 9.5, 1000, 0.0, n)

		from data.get_candles_spot import main as get_candles
		get_candles()

		

		price_changes = []
		times = []
		self.prices = []
		
		for candle in candleLoader(DATABASE):
			#consider markets trading against BTC, so we need to invert the USDT price
			self.prices.append(np.array([1] + [candle[currency + 'USDT_OPEN'] for currency in QUOTES + CURRENCIES]))
			if len(self.prices) == 1:
				continue
			else:
				price_changes.append(self.prices[-1] / self.prices[-2])
				times.append(candle['open_time'])

		for change, time in zip(price_changes[-n:], times[-n:]):
			self.manager.update(time, change)


		self.returns = price_changes
		self.update_times = times
		self.portfolio = self.account.get_portfolio_weighted(['USDT'] + QUOTES + CURRENCIES)
		self.manager.portfolio = self.portfolio
		self.prices.append(np.array([1] + [np.mean(market.prices([a + 'USDT' for a in QUOTES + CURRENCIES])[b + 'USDT']) for b in QUOTES + CURRENCIES]))

	def save(self, location):
		with open(location, 'wb') as file:
			pickle.dump(self, file)

	def update(self):
		self.prices.append(np.array([1] + [np.mean(market.prices([a + 'USDT' for a in QUOTES + CURRENCIES])[b + 'USDT']) for b in QUOTES + CURRENCIES]))
		self.returns.append(self.prices[-1] / self.prices[-2])
		self.update_times.append(int(datetime.datetime.now().timestamp() * 1000))
		self.manager.update(self.update_times[-1], self.returns[-1])

		print(self.manager.portfolio)








def main():


	try:
		import keys
	except ModuleNotFoundError:
		print('keys.py file missing - see readme for set up instructions')
		return 

	bot = binanceBot(keys.API, keys.SECRET, 'state.pkl')
	bot.update()
	bot.save('state.pkl')

if __name__ == '__main__':
	main()