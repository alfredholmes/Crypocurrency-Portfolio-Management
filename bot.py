from binance.account import account
import binance.market as market


from portfolioManagement.portfolioManagement import MAMRPortfolioManager
import pickle

import numpy as np

MAMR_MGR = 'data.pkl'
BINANCE_BOT = 'bot.pkl'

#Currencies to Include in selection
CURRENCIES = ['ETH', 'EOS', 'FTT', 'LTC', 'BCH', 'ADA']
#Quote Assets
QUOTES = ['BTC', 'BNB']
RISKLESS = 'USDT'


DATABASE = 'data/candles_1d.db'

class binanceBot:
	def __init__(self, saved=None, n=12):
		if saved is not None:
			with open(saved, 'rb') as file:
				self = pickle.load(file)
				return

		#get the portfolio...
		self.manager = MAMRPortfolioManager(len(CURRENCIES) + len(QUOTES) + 1, 8.6, 800, 100, 0.001, n)

		from data.get_candles_spot import main as get_candles
		get_candles()

		

		price_changes = []
		times = []
		self.prices = []
		
		for candle in candleLoader(DATABASE):
			#consider markets trading against BTC, so we need to invert the USDT price
			self.prices.append(np.array([1 / candle['BTCUSDT_OPEN'], 1] + [candle[currency + 'BTC_OPEN'] for currency in ['BNB'] + CURRENCIES]))
			if len(self.prices) == 1:
				continue
			else:
				price_changes.append(self.prices[-1] / self.prices[-2])
				times.append(candle['open_time'])

		for change, time in zip(price_changes[-n:], times[-n:]):
			self.manager.update(time, change)

		self.portfolio = account.get_portfolio_weight(['USDT'] + QUOTES[1:] + CURRENCIES)

		self.manager.portfolio = self.portfolio


		self.prices.append([np.array(market.prices([currency + RISKLESS for currency in CURRENCIES + QUOTES]))])

	def save(self, location):
		with open(location, 'wb') as file:
			pickle.dump(self, file)

	def update(prices):
		self.prices.append(prices)
		self.returns.append(prices[-1] / prices[-2])








def main():

	binanceBot()
	return

	#load wallet and get balances
	try:
		import keys
	except ModuleNotFoundError:
		print('keys.py file missing - see readme for set up instructions')
		return 
	wallet = account(keys.API, keys.SECRET)
	print(wallet.balances)

	#get current prices
	
	#price array



	try:
		with open(MAMR_MGR, 'rb') as file:
			MAMR_Manager = pickle.load(file)
	except:
		MAMR_Manager = MAMRPortfolioManager(len(CURRENCIES) + len(QUOTES) + 1, 8.6, 800, 100, 0.001, 12)

		MAMR_Manager.update()


	MAMR_Manager.update(0,[1] * (len(CURRENCIES) + len(QUOTES) + 1))

	with open(MAMR_MGR, 'wb') as file:
		pickle.dump(MAMR_Manager, file)

	#calculate portfolio weights


	#calculate next portfolio

	#calculate trade

	#execute trade


if __name__ == '__main__':
	main()