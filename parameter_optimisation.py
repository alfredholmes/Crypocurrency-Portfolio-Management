"""
Script to try and optimise the parameters for the PAMR Algorithm

The script brute forces around possible parameter values before refining the selection using the minimize function


Author: Alfred Holmes, https://github.com/alfredholmes
"""

import PAMR
from scipy.optimize import brute as brute
from scipy.optimize import minimize as minimize
import numpy as np

DATABASE = 'data/candles_30m.db'



def PAMR_mean_return(epsilon, c, price_changes):
	#initial_portfolio = np.ones(len(price_changes[0])) / len(price_changes[0])
	initial_portfolio = np.zeros(len(price_changes[0]))
	initial_portfolio[0] = 1
	portfolio = PAMR.PAMR(initial_portfolio, epsilon, c, 0.00075)
	_, _, returns = portfolio.run(price_changes)
	print(epsilon, c, np.mean(returns))

	return np.mean(returns)

def main():
	price_changes = PAMR.get_prices(DATABASE) 
	result = brute(lambda x: -PAMR_mean_return(x[0], x[1], price_changes), [(0.5, 1), (0.001, 10)], Ns=20)
	initial = result.x0

	result = minimize(lambda x: -PAMR_mean_return(x[0], x[1], price_changes), initial)

	print(result)

if __name__ == '__main__':
	main()