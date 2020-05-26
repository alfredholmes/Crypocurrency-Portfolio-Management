from data.candles import candleLoader
from portfolioManagement.portfolioManagement import PAMRPortfolioManager
import datetime
from matplotlib import pyplot as plt

import numpy as np

DATABASE = 'data/futures_candles_30m.db'
CURRENCIES = ['USDT', 'BTC', 'ETH', 'LTC', 'XMR', 'EOS']

def main():
	#get all the candles and calculate the price changes
	price_changes = []
	prices = []
	times = []
	for candle in candleLoader(DATABASE):
		prices.append(np.array([1] + [candle[currency + 'USDT_open'] for currency in CURRENCIES[1:]]))
		if len(prices) == 1:
			continue
		else:
			price_changes.append(prices[-1] / prices[-2])
			times.append(candle['open_time'])

	manager = PAMRPortfolioManager(len(CURRENCIES), 0.5, 50, 0.0004, 0)
	for change, time in zip(price_changes, times):
		print((times[-1] - time) / (1000 * 60 * 30))
		manager.update(time, change)

	plt.figure(0)

	plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], manager.values[1:])
	plt.plot([datetime.datetime.fromtimestamp(time / 1000) for time in times], [p[1]/prices[0][1] for p in prices[1:]])

	plt.figure(1)

	plt.plot(manager.portfolios)

	plt.show()


if __name__ == '__main__':
	main()