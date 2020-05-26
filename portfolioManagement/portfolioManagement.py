import numpy as np
from scipy.optimize import minimize


#error function to minimise when trading into new portfolio
def error(trades, old, new, trading_fee):
	old = np.array(old)
	new = np.array(new)
	first_pass = np.min([np.zeros(trades.size), trades], axis=0)
	second_pass = np.max([np.zeros(trades.size), trades], axis=0)

	first_pass_fees = np.sum(np.abs(first_pass)) * trading_fee
	second_pass_fees = np.sum(np.abs(second_pass)) * trading_fee

	portfolio_value= 1 - first_pass_fees - (1 - first_pass_fees) * second_pass_fees

	new_portfolio = old + first_pass
	new_portfolio[0] += -np.sum(first_pass) * (1 - trading_fee)
	new_portfolio[0] -= np.sum(second_pass)
	new_portfolio +=  second_pass * (1 - trading_fee)

	distance_to_line = np.sqrt(np.sum((new * np.sum(new * new_portfolio) / np.sum(new ** 2) - new_portfolio) ** 2))

	return distance_to_line - portfolio_value

class portfolioManager:
	#n number of assets available for investment, assets is an array  of names for each available assets
	def __init__(self, n, trading_fee =0):
		self.portfolio = np.ones(n) / n
		self.portfolios = [self.portfolio]
		self.trading_fee = trading_fee
		self.value = 1
		self.values = [1]
		self.prices = [np.ones(n)]
		self.price_changes = []
		self.update_times = []

	def update(self, time, price_changes):
		#keep track of the portfolio update time, might be worth checking that there are no 
		self.update_times.append(time)
		self.price_changes.append(price_changes)
		self.prices.append(self.prices[-1] * price_changes)
		self.value *= np.sum(np.array(price_changes) * self.portfolio)
		
		#pick next portfolio
		target_portfolio = self.calculate_next_portfolio()

		trade = self.find_trade(target_portfolio)
		self.value *= self.execute_trade(trade)

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
		first_pass = np.min([np.zeros(trade.size), trade], axis=0)
		second_pass = np.max([np.zeros(trade.size), trade], axis=0)

		first_pass_fees = np.sum(np.abs(first_pass)) * self.trading_fee
		second_pass_fees = np.sum(np.abs(second_pass)) * self.trading_fee

		portfolio_value= 1 - first_pass_fees - (1 - first_pass_fees) * second_pass_fees

		new_portfolio = self.portfolio + first_pass
		new_portfolio[0] += -np.sum(first_pass) * (1 - self.trading_fee)
		new_portfolio[0] -= np.sum(second_pass)
		new_portfolio +=  second_pass * (1 - self.trading_fee)

		self.portfolio = new_portfolio / np.sum(new_portfolio)

		return portfolio_value


	#for base class the strategy is buy and hold
	def calculate_next_portfolio(self):
		return np.array(self.portfolio)

class PAMRPortfolioManager(portfolioManager):
	def __init__(self, n, epsilon, c, trading_fee =0, margin=0):
		super().__init__(n, trading_fee)
		self.epsilon = epsilon
		self.c = c
		self.margin = margin

	def calculate_next_portfolio(self):
		price_changes = np.array(self.price_changes[-1])

		x_bar = np.mean(price_changes)
		distance = np.sum((x_bar * np.ones(price_changes.size) - price_changes) ** 2)
		if self.c > 0:
			tau = self.loss(price_changes) / (distance + 1 / (2*self.c))
		else:
			tau = 2**10
			self.portfolio = np.zeros(self.portfolio.size)

		new_weights = self.portfolio - tau * (price_changes - x_bar * np.ones(price_changes.size))
		new_weights = self.normalise(new_weights)

		return new_weights

	
	def normalise(self, new_weights):
		if self.margin == 0:
			result = minimize(lambda x: np.sum((x - new_weights) ** 2), np.array(new_weights), jac=lambda x: 2 * (x - new_weights), bounds = [(0, np.infty) for _ in new_weights], constraints=[{'type': 'eq', 'fun': lambda x: np.sum(np.abs(x)) - 1}])
		else:
			result = minimize(lambda x: np.sum((x - new_weights) ** 2), np.array(new_weights), jac=lambda x: 2 * (x - new_weights), constraints=[{'type': 'ineq', 'fun': lambda x: self.margin - np.sum(np.abs(x))}])

		minimum = result.x

		return minimum / np.sum(np.abs(minimum)) * self.margin

	def loss(self, price_changes):
		return np.max([0, np.sum(self.portfolio * price_changes) - self.epsilon])

def test_trading_calculation():
	pm = portfolioManager(3, 0.1)
	pm.find_trade(pm.portfolio, [0, 0, 1])
	print(pm.value)

def test_PAMR():
	from matplotlib import pyplot as plt
	pm = PAMRPortfolioManager(3, 0.5, 200, 0.001)
	for i in range(100):
		pm.update(i, np.random.rand(3) * 1.1)

	plt.plot(pm.values)
	plt.show()

if __name__ == '__main__':
	#test_trading_calculation()
	test_PAMR()

	
