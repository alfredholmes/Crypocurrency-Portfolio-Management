import numpy as np
from scipy.optimize import minimize



class portfolioManager:
	#n number of assets available for investment, assets is an array  of names for each available assets
	def __init__(self, n, trading_fee=0):
		#self.portfolio = np.ones(n)/n
		self.portfolio = np.zeros(n)
		
		self.portfolio[0] = 1
		self.portfolios = [self.portfolio]
		self.trading_fee = trading_fee
		self.margin = 1
		self.value = 1
		self.values = [1]
		self.prices = [np.ones(n)]
		self.price_changes = []
		self.update_times = []

	#function to update the portfolio, interest is the interest to be paid for holding borrowed assets in futures markets for example
	def update(self, time, price_changes, interest=0):
		#keep track of the portfolio update time, might be worth checking that there are no 
		self.update_times.append(time)
		self.price_changes.append(price_changes)
		self.prices.append(self.prices[-1] * price_changes)
		
		profit = (np.sum(np.array(price_changes) * self.portfolio) - np.sum(self.portfolio)) * self.value
		self.value += profit


		if np.sum(np.abs(self.portfolio)) > 0:
			interest_cost = self.portfolio * interest
			self.value -= np.sum(interest_cost) * self.value

			self.portfolio *= price_changes
			self.portfolio /= 1 if np.sum(np.abs(self.portfolio)) == 0 else (np.sum(np.abs(self.portfolio)) / self.margin)

		#pick next portfolio
		target_portfolio = self.calculate_next_portfolio()
		
		trade = target_portfolio - self.portfolio		

		self.execute_trade(trade)
		

		#update data
		self.values.append(self.value * self.fees(time))
		
		
		self.portfolios.append(np.array(self.portfolio))



	def fees(self, time):
		return 1


	#Finds the most efficient (hopefully) trade to get to the desired portfolio
	#TODO: constraints, evaluate performance
	def find_trade(self, new, connected=False):
		changes = new - self.portfolio
		new_portfolio = np.array(self.portfolio)
		constraints = (
				{
					'type': 'eq',
					'fun': lambda x: x[0]
				},
				{
					'type': 'ineq',
					'fun': lambda x: self.portfolio + np.min([np.zeros(x.size),x], axis=0)
				},
			)
		trade = minimize(error, changes, args=(self.portfolio, new, self.trading_fee), constraints=constraints).x
		return trade
	#executes a trade and returns the loss fraction of the portfolio value post trade
	#trade formatted as follows: negative values are moved form balance to quote, and then positive balance is moved from USD to quote
	def execute_trade(self, trade):

		to_sell = np.min([trade, np.zeros(trade.size)], axis=0)
		value_sold = - (1 - self.trading_fee) * np.sum(to_sell)
		self.portfolio += to_sell

		to_buy = np.max([trade, np.zeros(trade.size)], axis=0) * (1 - self.trading_fee) ** 2
		self.portfolio += to_buy

		#cost of operation
		
		cost = value_sold / (1 - self.trading_fee) * self.trading_fee + np.sum(to_buy) / (1 - self.trading_fee) ** 2 * self.trading_fee
		

		self.value -= cost * self.value



		self.portfolio /= np.sum(np.abs(self.portfolio))
		
		
	#function to find a valid portfolio with minimal distance to the suggested portfolio
	def normalise(self, new_weights):
		if np.sum(np.abs(new_weights)) == 0:
			return new_weights

		
		
		result = minimize(
							lambda x: np.sum((x - new_weights) ** 2), 
							np.array(new_weights), 
							jac=lambda x: 2 * (x - new_weights), 
							bounds = [(0, np.infty) for _ in new_weights], 
							constraints=[{'type': 'eq', 'fun': lambda x: np.sum(np.abs(x)) - 1}]
						)
		minimum = result.x
		



		#return np.max([new_weights, np.zeros(new_weights.size)], axis=0) / np.sum(np.max([new_weights, np.zeros(new_weights.size)], axis=0))
		return minimum / np.sum(np.abs(minimum))


	#for base class the strategy is buy and hold
	def calculate_next_portfolio(self):
		return np.array(self.portfolio)

class PAMRPortfolioManager(portfolioManager):
	def __init__(self, n, epsilon, c, trading_fee =0):
		super().__init__(n, trading_fee)
		self.epsilon, self.c= epsilon, c


	def calculate_next_portfolio(self):
		price_changes = np.array(self.price_changes[-1])
		tau = self.loss(self.portfolio, price_changes) / (1 / (2 * self.c) + np.sum((self.portfolio - np.mean(self.portfolio)) ** 2))
		new_weights = self.portfolio - tau * (self.portfolio - np.mean(self.portfolio))
		return self.normalise(new_weights)

	def loss(self, b, price_changes):
		return np.max([0, np.sum(b * price_changes) - self.epsilon])


class MAMRPortfolioManager(portfolioManager):
	def __init__(self, n, epsilon, c_1, c_2, trading_fee=0, omega=5):
		super().__init__(n, trading_fee)
		self.epsilon, self.c_1, self.c_2, self.omega = epsilon, c_1, c_2, omega
		self.ma = np.ones(n)

	def calculate_next_portfolio(self):
		price_changes = np.array(self.price_changes[-1])
		self.ma = np.mean(self.price_changes[-self.omega:], axis=0)
		x_bar = np.mean(self.ma)


		alpha = 0 if np.sum((self.ma - x_bar * np.ones(self.ma.size)) ** 2) == 0 else self.loss(self.portfolio, self.ma) / np.sum((self.ma - x_bar * np.ones(self.ma.size)) ** 2)
		#print(self.loss(self.ma) / np.sum((self.ma - x_bar * np.ones(self.ma.size)) ** 2))
		new_weights = self.portfolio + alpha * (self.ma - x_bar * np.ones(self.ma.size))
		new_weights = self.normalise(new_weights)
		
		return new_weights


	def loss(self, b, x):

		
		if np.sum(np.abs(b)) == 0:
			return 1
		gain = np.sum(b * x) - 1
	

		if np.abs(gain) >= self.epsilon / self.c_1:
			return 0
		elif gain <= 0:
			return -gain
		elif gain <= self.epsilon / self.c_2:
			return self.epsilon / self.c_2 - gain
		else:
			return self.epsilon / self.c_1 - gain


if __name__ == '__main__':
	#test_trading_calculation()
	test_PAMR()

	
