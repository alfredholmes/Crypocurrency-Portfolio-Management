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
		self.balances = np.array([self.account.balances[c] if c in self.account.balances else 0.0 for c in [RISKLESS] + QUOTES + CURRENCIES])

		

		if saved is not None:
			try:
				with open(saved, 'rb') as file:
					loaded = pickle.load(file)
					self.manager = loaded.manager
					self.prices = loaded.prices
					self.returns = loaded.returns
					self.update_times = loaded.update_times
					self.portfolio = np.array(loaded.portfolio)
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
		
		self.manager.portfolio = np.array(self.portfolio)
		self.prices.append(np.array([1.05 ** (0.5 / 365)] + [np.mean(market.prices([a + 'USDT' for a in QUOTES + CURRENCIES])[b + 'USDT']) for b in QUOTES + CURRENCIES]))

	def save(self, location):
		with open(location, 'wb') as file:
			pickle.dump(self, file)

	def update(self):
		self.prices.append(np.array([1.05 ** (0.5 / 365)] + [np.mean(market.prices([a + 'USDT' for a in QUOTES + CURRENCIES])[b + 'USDT']) for b in QUOTES + CURRENCIES]))
		self.returns.append(self.prices[-1] / self.prices[-2])
		self.update_times.append(int(datetime.datetime.now().timestamp() * 1000))
		usd_balances = self.balances * self.prices[-1]

		self.manager.update(self.update_times[-1], self.returns[-1])
		target_portfolio_usd = self.manager.portfolio * np.sum(usd_balances)

		trade = target_portfolio_usd - usd_balances

		buys = np.max([trade, np.zeros(trade.size)], axis=0)
		sells = np.min([trade, np.zeros(trade.size)], axis=0)
		
		#Trade negative non quote assets to BNB
		currency_sells = np.zeros(sells.size)
		currency_sells[-len(CURRENCIES):] = sells[-len(CURRENCIES):]

		#calculate volume to sell
		currency_sell_volume = -currency_sells / self.prices[-1]
		buy_volume = buys / self.prices[-1]
		#execute trade to BNB
		for i, (currency, volume) in enumerate(zip(['USDT'] + QUOTES + CURRENCIES, currency_sell_volume)):
			if volume == 0:
				continue
			print('Trade: ' + currency + 'BNB\t ', volume)
			self.account.market(currency, 'BNB', 'SELL', False, volume)

			trade[i] = 0.0


		#trade the quote assets to make up the deficits
		for i, quote in enumerate(['USDT'] + QUOTES):
			#ignore BNB

			if trade[i] < 0:

				#sell the asset
				#find currency to sell to
				for j, currency in enumerate(['USDT'] + QUOTES + CURRENCIES):
					side = 'BUY'
					quote_volume = False
					if quote == 'BNB' and currency == 'BTC':
						continue
					if currency == 'USDT' and (quote == 'BTC' or quote == 'BNB'):
						continue
					

					if quote == 'BNB' and currency == 'ETH':
						side = 'SELL'
						quote_volume = True
						currency = 'BNB'
						quote = 'ETH'
					

					if trade[j] > 0 and -trade[i] < trade[j]:
						print('Trade: ' + currency + quote + ' liquidate')
						traded = self.account.market(currency, quote, side)
						if traded > 0:
							trade[i] += traded * self.prices[-1][i]
							trade[j] -= traded * self.prices[-1][i]
						break
					elif trade[j] > 0:
						print('Trade: ' + currency + quote, trade[j] / self.prices[-1][j])
						traded = self.account.market(currency, quote, side, quote_volume, trade[j] / self.prices[-1][j])
						if traded > 0:	
							trade[i] += traded * self.prices[-1][j]
							trade[j] -= traded * self.prices[-1][j]

					if quote == 'ETH':
						quote = 'BNB'


		self.portfolio = self.account.get_portfolio_weighted(['USDT'] + QUOTES + CURRENCIES)
		print(self.portfolio, self.manager.portfolio)
		
		with open('output.txt', 'a') as file:
			file.write(str(self.manager.portfolio) + str(self.portfolio))

		self.manager.portfolio = np.array(self.portfolio)


def main():


	try:
		import keys
	except ModuleNotFoundError:
		print('keys.py file missing - see readme for set up instructions')
		return 

	bot = binanceBot(keys.API, keys.SECRET, 'state.pkl')
	bot.account.trade_to_portfolio('USDT', QUOTES, CURRENCIES, [1] * (1 + len(QUOTES + CURRENCIES)))

	#bot.update()
	#bot.save('state.pkl')

if __name__ == '__main__':
	main()
