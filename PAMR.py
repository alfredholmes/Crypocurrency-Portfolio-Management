"""
Implementation of the PAMR algorithm to test performance when including trading fees

Based on https://link.springer.com/content/pdf/10.1007/s10994-012-5281-z.pdf

"""

import candle_data
import numpy as np
from scipy.optimize import minimize as minimize#


from matplotlib import pyplot as plt

class PAMR:
	#Parameters epsilon and c are as in the paper
	def __init__(self, initial_portfolio, epsilon=0.8, c=500):
		
		self.portfolio = np.array(initial_portfolio)
		self.epsilon = epsilon
		self.c = c

	def loss(self, price_changes):
		return np.max([0, np.sum(self.portfolio * np.array(price_changes)) - self.epsilon])



	def new_weights_PAMR(self, price_changes):
		price_changes = np.array(price_changes)
		x_bar = np.mean(price_changes)
		distance = np.sum((x_bar * np.ones(price_changes.size) - price_changes) ** 2) 
		tau = self.loss(price_changes) / distance

		new_weights = self.portfolio - tau * (price_changes - x_bar * np.ones(price_changes.size))
		new_weights = self.normalise(new_weights)

		return new_weights / np.sqrt(np.sum(new_weights ** 2))

	def normalise(self, new_weights):
		return minimize(lambda x: np.sum((x - new_weights) ** 2), np.array(new_weights), bounds = [(0, np.infty) for _ in new_weights], constraints=[{'type': 'eq', 'fun': lambda x: np.sum(x ** 2) - 1}]).x

	def run(self, price_change_list):
		value = 1
		values = [1]
		portfolios = []
		for price_changes in price_change_list:

			self.portfolio = np.array([1/3, 1/3, 1/3])
			value = value * np.sum(np.array(price_changes) * self.portfolio) * (1 - 0.001)
			values.append(value)

			self.portfolio = self.new_weights_PAMR(price_changes)
		
			portfolios.append(np.array(self.portfolio))
			
		return values, portfolios


def main():
	currencies = ['USDT', 'BTC', 'ETH'] #USDT is assumed to have a constant price of 1, everything else trades against BTC

	data = candle_data.Candles('data/candles_1d.db')
	candles = data.get_candles()

	price_changes = []
	previous_candle = None


	btc_price = []

	for candle in candles:
		if previous_candle is None:
			previous_candle = candle
			continue

		price_changes.append([])

		btc_price.append(candle['BTCUSDT_OPEN'])	
		
		for currency in currencies:
			if currency == 'USDT':
				price_changes[-1].append(1)
			elif currency == 'BTC':
				price_changes[-1].append(candle['BTCUSDT_OPEN'] / previous_candle['BTCUSDT_OPEN'])
			else:
				price_changes[-1].append(candle[currency + 'BTC_OPEN'] * candle['BTCUSDT_OPEN'] / (previous_candle[currency + 'BTC_OPEN'] * previous_candle['BTCUSDT_OPEN'])) 

		previous_candle = candle

	initial_weights = [1/3, 1/3, 1/3]


	plt.plot(np.array(btc_price) / btc_price[0])

	portfolio = PAMR(initial_weights)

	values, weights = portfolio.run(price_changes)
	plt.plot(values)
	plt.show()

if __name__ == '__main__':
	main()