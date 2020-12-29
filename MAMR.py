from data.candles import candleLoader
from portfolioManagement.portfolioManagement import PAMRPortfolioManager, MAMRPortfolioManager
import datetime
from matplotlib import pyplot as plt

import numpy as np

#need to run data/get_candles_spot.py
DATABASE = 'data/candles_12h.db'
CURRENCIES = ['BTC', 'ETH', 'EOS', 'LTC', 'BNB', 'XRP', 'BCH', 'ADA', 'XMR']
#CURRENCIES = ['BTC', 'ETH', 'EOS', 'LTC', 'BNB', 'BCH', 'ADA']

def main():
	#get all the candles and calculate the price changes
	price_changes = []
	prices = []
	times = []

	for candle in candleLoader(DATABASE):
		#consider markets trading against BTC, so we need to invert the USDT price
		prices.append(np.array([1] + [candle[currency + 'USDT_OPEN'] for currency in CURRENCIES]))
		if len(prices) == 1:
			continue
		else:
			price_changes.append(prices[-1] / prices[-2])
			price_changes[-1][0] = 1.05 ** (1 / 365)
			times.append(candle['open_time'])

	#manager = MAMRPortfolioManager(len(CURRENCIES) + 1, 11.75, 371, 995, 0.001, 23)
	#manager = MAMRPortfolioManager(len(CURRENCIES) + 1, 4.105, 9.5, 1000, 0.00075, 26)
	manager = MAMRPortfolioManager(len(CURRENCIES) + 1, 4.105, 9.5, 1000, 0.001, 26)

	for change, time in zip(price_changes, times):
		manager.update(time, change)


	print(manager.value)
	
	
	plt.figure(0)



	plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], np.array(manager.values[1:]), label='MAMR Portfolio Value')
	plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], [p[1]/prices[0][1] for p in prices[1:]], label='BTC Return')
	plt.yscale('log')
	plt.ylabel('Return')
	plt.title('MAMR 12 hour updates, 0.001 Transaction Fee')
	plt.legend()


	plt.figure(1)

	for i, currency in enumerate(['USDT'] + CURRENCIES):
		plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], [p[i] for p in manager.portfolios[1:]], label=currency)
	plt.legend()

	plt.show()

	


if __name__ == '__main__':
	main()