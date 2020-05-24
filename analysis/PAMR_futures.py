"""
Implementation of the PAMR algorithm to test performance when including trading fees

Based on https://link.springer.com/content/pdf/10.1007/s10994-012-5281-z.pdf

"""

import candle_data
import numpy as np
from scipy.optimize import minimize as minimize
import datetime


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
		if self.c > 0:
			tau = self.loss(price_changes) / (distance + 1 / (2*self.c))
		else:
			tau = 2**10
			self.portfolio = np.zeros(self.portfolio.size)

		new_weights = self.portfolio - tau * (price_changes - x_bar * np.ones(price_changes.size))
		new_weights = self.normalise(new_weights)

		self.portfolio = new_weights

	def normalise(self, new_weights):
		result = minimize(lambda x: np.sum((x - new_weights) ** 2), np.array(new_weights), jac=lambda x: 2 * (x - new_weights), bounds = [(0, np.infty) for _ in new_weights], constraints=[{'type': 'eq', 'fun': lambda x: np.sum(np.abs(x)) - 1}])
		#maybe check
		minimum = result.x

		return minimum / np.sum(minimum)

	def run(self, price_change_list, funding_rate):
		value = 1
		values = [1]
		portfolios = []
		returns = []
		btc_trading_volume = []
		btc_price = 1/3

		for i, price_changes in enumerate(price_change_list):
			previous_portfolio = np.array(self.portfolio)
			previous_value = value

			self.portfolio =  self.portfolio * np.array(price_changes) / np.sum(self.portfolio * np.array(price_changes))

			value *= np.sum(self.portfolio * np.array(price_changes))
			self.new_weights_PAMR(price_changes)
			traded_volume = np.sum(np.abs(self.portfolio - previous_portfolio))
			holding_fee = np.sum(self.portfolio[1:] -np.array(funding_rate[i]) * self.portfolio[1:]) + self.portfolio[0]

			#print(np.array(funding_rate[i]) * self.portfolio[1:])
			value -= value * traded_volume * self.tradingfee

			if i * 6 == 0:
				value *= holding_fee

			values.append(value)
			returns.append(value / previous_value)

			btc_price *= price_changes[1]

			btc_trading_volume.append(traded_volume * value / btc_price)


			portfolios.append(np.array(self.portfolio))

		return values, portfolios, returns, btc_trading_volume



def main():
	currencies = ['USDT', 'BTC', 'ETH', 'EOS', 'LTC', 'BNB', 'XRP', 'BCH', 'ADA', 'XMR']
	#currencies = ['USDT', 'BTC']
	data = candle_data.Candles('data/futures_candles_30m.db')
	candles = data.get_candles(datetime.datetime(year=2017, month=1, day=1).timestamp() * 1000)
	#candles = data.get_candles()
	price_changes = []
	previous_candle = None

	initial_weights = np.zeros(2 * len(currencies) - 1)
	initial_weights[0] = 1
	#portfolio = PAMR(initial_weights, 0.3, 50, 0.0004 * 0.9)
	portfolio = PAMR(initial_weights, 0.5, 20, 0.0004 * 0.9)



	prices = []
	funding_rates = []

	for candle in candles:
		if previous_candle is None:
			previous_candle = candle
			continue

		price_changes.append([])

		prices.append([candle['BTCUSDT_open']] + [candle[c + 'USDT_open'] for c in currencies[2:]])
		funding_rates.append([candle[market + 'USDT_funding_rate'] for market in currencies[1:]])


		for currency in currencies:
			if currency == 'USDT':
				price_changes[-1].append(1)
			else:
				price_changes[-1].append(candle[currency + 'USDT_open'] / previous_candle[currency + 'USDT_open'])

		price_changes[-1] += [1 / r for r in price_changes[-1][1:]]
		funding_rates[-1] += [-r for r in funding_rates[-1]]


		previous_candle = candle

	#initial_weights = np.ones(len(currencies)) / len(currencies)




	best_performing = 0
	best_return =  prices[-1][0]
	for i, final_price in enumerate(prices[-1]):
		if final_price / prices[0][i] > best_return:
			best_performing = i
			best_return = final_price / prices[0][i]

	plt.figure(0)
	plt.plot(np.array([p[best_performing] for p in prices]) / prices[0][best_performing], label=currencies[best_performing + 1] +' Price')


	values, weights, returns, traded_volume = portfolio.run(price_changes, funding_rates)

	plt.plot(values, label='PAMR-2')
	plt.yscale('log')
	plt.xlabel('Trading Period')
	plt.ylabel('Return')


	#plt.legend()

	plt.figure(1)
	for i, currency in enumerate(currencies):
		plt.plot([w[i] for w in weights], label=currency)
		if i > 0:
			plt.plot([w[i + len(currencies) - 1] for w in weights], label=currency + ' short')
	plt.legend()

	#plt.figure(2)
	#plt.plot([np.sum(traded_volume[max(int(i - 30 * 24), 0):i]) for i in range(len(traded_volume))])

	plt.show()

if __name__ == '__main__':
	main()
