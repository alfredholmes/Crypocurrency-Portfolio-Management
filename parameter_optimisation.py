"""
Script to try and optimise the parameters for the PAMR Algorithm

The script brute forces around possible parameter values before refining the selection using the minimize function


Author: Alfred Holmes, https://github.com/alfredholmes
"""

import PAMR
from scipy.optimize import minimize
import numpy as np

from multiprocessing import Pool

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
	
	epsilon_range = (0.5, 1)
	c_range = (0.0001, 20)


	parameters = [(x, y, price_changes) for x in np.linspace(epsilon_range[0], epsilon_range[1]) for y in np.linspace(c_range[0], c_range[1])]
	with Pool() as p:
		results = p.starmap(PAMR_mean_return, parameters)

	result = minimize(lambda x: -PAMR_mean_return(x[0], x[1], price_changes), initial)

	print(result)

if __name__ == '__main__':
	main()