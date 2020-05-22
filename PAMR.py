"""
Implementation of the PAMR algorithm to test performance when including trading fees

Based on https://link.springer.com/content/pdf/10.1007/s10994-012-5281-z.pdf

"""

import candle_data
import numpy as np
from scipy.optimize import minimize as minimize


from matplotlib import pyplot as plt

class PAMR:
	#Parameters epsilon and c are as in the paper
	def __init__(self, initial_portfolio, epsilon=0.4, c=0.01, tradingfee=0):
		
		self.portfolio = np.array(initial_portfolio)
		self.epsilon = epsilon
		self.c = c
		self.tradingfee = tradingfee

	def loss(self, price_changes):
		return np.max([0, np.sum(self.portfolio * np.array(price_changes)) - self.epsilon])



	def new_weights_PAMR(self, price_changes):
		price_changes = np.array(price_changes)
		x_bar = np.mean(price_changes)
		distance = np.sum((x_bar * np.ones(price_changes.size) - price_changes) ** 2)
		tau = self.loss(price_changes) / (distance + 1 / (2*self.c))

		new_weights = self.portfolio - tau * (price_changes - x_bar * np.ones(price_changes.size))
		new_weights = self.normalise(new_weights)

		self.portfolio = new_weights

	def normalise(self, new_weights):
		result = minimize(lambda x: np.sum((x - new_weights) ** 2), np.array(new_weights), jac=lambda x: 2 * (x - new_weights), bounds = [(0, np.infty) for _ in new_weights], constraints=[{'type': 'eq', 'fun': lambda x: np.sum(np.abs(x)) - 1}])
		#maybe check 
		minimum = result.x

		return minimum / np.sum(minimum)

	def run(self, price_change_list):
		value = 1
		values = [1]
		portfolios = []
		returns = []
		

		for price_changes in price_change_list:
			previous_portfolio = np.array(self.portfolio)
			previous_value = value

			self.portfolio =  self.portfolio * np.array(price_changes) / np.sum(self.portfolio * np.array(price_changes))

			value *= np.sum(self.portfolio * np.array(price_changes))
			self.new_weights_PAMR(price_changes)
			traded_volume = np.sum(np.abs(self.portfolio - previous_portfolio))
			value -= value * traded_volume * self.tradingfee
			
			values.append(value)
			returns.append(value / previous_value)



		
			portfolios.append(np.array(self.portfolio))
			
		return values, portfolios, returns

def get_prices(db, currencies=['USDT', 'BTC', 'ETH', 'EOS', 'LTC', 'BNB', 'BCH', 'XRP']):

	data = candle_data.Candles(db)
	candles = data.get_candles()

	price_changes = []
	previous_candle = None
	for candle in candles:
		if previous_candle is None:
			previous_candle = candle
			continue

		price_changes.append([])

		
				
		for currency in currencies:
			if currency == 'USDT':
				price_changes[-1].append(1)
			elif currency == 'BTC':
				price_changes[-1].append(candle['BTCUSDT_OPEN'] / previous_candle['BTCUSDT_OPEN'])
			else:
				price_changes[-1].append(candle[currency + 'BTC_OPEN'] * candle['BTCUSDT_OPEN'] / (previous_candle[currency + 'BTC_OPEN'] * previous_candle['BTCUSDT_OPEN'])) 

		previous_candle = candle

	return price_changes


def main():
	currencies = ['USDT', 'BTC', 'ETH', 'EOS', 'LTC', 'BNB', 'BCH', 'XRP'] #USDT is assumed to have a constant price of 1, everything else trades against BTC

	data = candle_data.Candles('data/candles_30m.db')
	candles = data.get_candles()

	price_changes = []
	previous_candle = None


	prices = []

	for candle in candles:
		if previous_candle is None:
			previous_candle = candle
			continue

		price_changes.append([])

		prices.append([candle['BTCUSDT_OPEN']] + [candle[c + 'BTC_OPEN'] for c in currencies[2:]])
			
		
		for currency in currencies:
			if currency == 'USDT':
				price_changes[-1].append(1)
			elif currency == 'BTC':
				price_changes[-1].append(candle['BTCUSDT_OPEN'] / previous_candle['BTCUSDT_OPEN'])
			else:
				price_changes[-1].append(candle[currency + 'BTC_OPEN'] * candle['BTCUSDT_OPEN'] / (previous_candle[currency + 'BTC_OPEN'] * previous_candle['BTCUSDT_OPEN'])) 

		previous_candle = candle

	initial_weights = np.ones(len(currencies)) / len(currencies)
	#initial_weights = np.zeros(len(currencies))
	#initial_weights[0] = 1


	best_performing = 0
	best_return =  prices[-1][0]
	for i, final_price in enumerate(prices[-1]):
		if final_price / prices[0][i] > best_return:
			best_performing = i
			best_return = final_price / prices[0][i]

	plt.figure(0)
	plt.plot(np.array([p[best_performing] for p in prices]) / prices[0][best_performing], label=currencies[best_performing + 1] +' Price')

	portfolio = PAMR(initial_weights, 0.8, 10, 0.00075)

	values, weights, returns = portfolio.run(price_changes)
	#plt.plot(np.cumprod([p[2] for p in price_changes]))
	plt.plot(values, label='PAMR-2')
	plt.yscale('log')
	plt.xlabel('Trading Hour')
	plt.ylabel('Return')
	#plt.ylim((0.4, 10))
	plt.legend()

	plt.figure(1)
	for i, currency in enumerate(currencies):
		plt.plot([w[i] for w in weights], label=currency)
	plt.legend()

	#plt.figure(2)
	#plt.hist(returns, bins=4000, density=True, alpha=0.5)
	#plt.hist(np.array([p[best_performing] for p in prices])[:-1] / np.array([p[best_performing] for p in prices])[1:], bins=4000, density=True, alpha=0.5)
	plt.show()

if __name__ == '__main__':
	main()