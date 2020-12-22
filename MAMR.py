from data.candles import candleLoader
from portfolioManagement.portfolioManagement import PAMRPortfolioManager, MAMRPortfolioManager
import datetime
from matplotlib import pyplot as plt

import numpy as np

#need to run data/get_candles_spot.py
DATABASE = 'data/candles_1d.db'
#CURRENCIES = ['ETH', 'EOS', 'LTC', 'BNB', 'XRP', 'BCH', 'ADA', 'XMR']
CURRENCIES = ['ETH', 'EOS', 'LTC', 'BNB', 'BCH', 'ADA']

def main():
	#get all the candles and calculate the price changes
	price_changes = []
	prices = []
	times = []

	for candle in candleLoader(DATABASE):
		#consider markets trading against BTC, so we need to invert the USDT price
		prices.append(np.array([1 / candle['BTCUSDT_OPEN'], 1] + [candle[currency + 'BTC_OPEN'] for currency in CURRENCIES]))
		if len(prices) == 1:
			continue
		else:
			price_changes.append(prices[-1] / prices[-2])
			times.append(candle['open_time'])

	#this is questionable as C_2 < C_1, perhaps over fit?
	manager = MAMRPortfolioManager(len(CURRENCIES) + 2, 8.6, 800, 100, 0.001, 12)

	for i, (change, time) in enumerate(zip(price_changes, times)):
		print((times[-1] - time) / (1000 * 60 * 30))		
		manager.update(time, change)
	plt.figure(0)



	plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], np.array(manager.values[1:]) / np.array([p[0]/prices[0][0] for p in prices[1:]]), label='MAMR Portfolio Value')
	plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], [prices[0][0]/p[0] for p in prices[1:]], label='BTC Return')
	plt.yscale('log')
	plt.ylabel('Return')
	plt.title('MAMR Daily Updates, 0.001 Transaction Fee')
	plt.legend()


	plt.figure(1)

	for i, currency in enumerate(['USDT', 'BTC'] + CURRENCIES):
		plt.plot([p[i] for p in manager.portfolios], label=currency)
	plt.legend()

	plt.show()


if __name__ == '__main__':
	main()