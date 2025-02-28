import numpy as np
from scipy.optimize import minimize


def project_onto_simplex(v):
    '''Fast projection onto the unit simplex, see https://jp.mathworks.com/matlabcentral/fileexchange/30332-projection-onto-simplex'''
    m = v.size
    s = np.sort(v)[::-1]
    
    temp_sum = 0    
    for i in range(m - 1):
        temp_sum += s[i]
        t_max = (temp_sum - 1) / (i + 1)
        if t_max > s[i + 1]:
            break
    else:
        t_max = (temp_sum + s[-1] - 1) / m
    

    return np.max([v - t_max, np.zeros(m)], axis=0)

class portfolioManager:
    #n number of assets available for investment, assets is an array  of names for each available assets
    def __init__(self, n):
        #self.portfolio = np.ones(n)/n
        self.portfolio = np.zeros(n)
        
        self.portfolio[0] = 1
        #self.portfolios = [self.portfolio]
        self.value = 1
        self.prices = [np.ones(n)]
        self.price_changes = []
        self.update_times = []
        self.returns = []

    #function to update the portfolio
    def update(self, time, price_changes):
        #keep track of the portfolio update time, might be worth checking that there are no 
        self.update_times.append(time)
        self.price_changes.append(price_changes)
        self.prices.append(self.prices[-1] * price_changes)
        
        
        
        profit = (np.sum(np.array(price_changes) * self.portfolio) - np.sum(self.portfolio)) * self.value
        self.returns.append(profit / self.value)
        self.value += profit



        self.portfolio *= price_changes
        self.portfolio /= np.sum(np.abs(self.portfolio))

        #pick next portfolio
        target_portfolio = self.calculate_next_portfolio()
        
        trade = target_portfolio - self.portfolio       

        self.execute_trade(trade)
        

        #update data
        
        
        #self.portfolios.append(np.array(self.portfolio))



    def fees(self, time):
        return 1


    #Finds the most efficient (hopefully) trade to get to the desired portfolio
    def execute_trade(self, trade):

        to_sell = np.min([trade, np.zeros(trade.size)], axis=0)
        value_sold = -np.sum(to_sell)
        self.portfolio += to_sell

        to_buy = np.max([trade, np.zeros(trade.size)], axis=0) 
        self.portfolio += to_buy

        #cost of operation
        self.portfolio /= np.sum(np.abs(self.portfolio))
        
        
    #function to find a valid portfolio with minimal distance to the suggested portfolio
    def normalise(self, new_weights):
        if np.sum(np.abs(new_weights)) == 0:
            return new_weights
    
        minimum = project_onto_simplex(new_weights)
        
        return minimum / np.sum(np.abs(minimum)) #return normalised portfolio


    #for base class the strategy is buy and hold
    def calculate_next_portfolio(self):
        return np.array(self.portfolio)

class PAMRPortfolioManager(portfolioManager):
    def __init__(self, n, epsilon, c):
        super().__init__(n)
        self.epsilon, self.c = epsilon, c


    def calculate_next_portfolio(self):
        price_changes = np.array(self.price_changes[-1])
        tau = self.loss(self.portfolio, price_changes) / (1 / (2 * self.c) + np.sum((self.portfolio - np.mean(self.portfolio)) ** 2))
        new_weights = self.portfolio - tau * (self.portfolio - np.mean(self.portfolio))
        return self.normalise(new_weights)

    def loss(self, b, price_changes):
        return np.max([0, np.sum(b * price_changes) - self.epsilon])


class MAMRPortfolioManager(portfolioManager):
    """
        Implements Algorithm 3 from https://doi.org/10.1155/2020/5956146

        n - int, number of assets
        c_1, c_2, epsilon floats, as defined in the paper and determine the loss funciton. Really we only care about epsilon / c_1 and epsilon/ c_2.
                If optimising then shouold fix epsilon = 1 say, and should have c_1 < c_2 so that 1 / c_2 < 1 / c_1. If this isn't the case then the loss function
                won't behave as expected.
        omega - number of periods in the moving average

    """

    def __init__(self, n, epsilon, c_1, c_2, omega=5):
        super().__init__(n)
        self.epsilon, self.c_1, self.c_2, self.omega = epsilon, c_1, c_2, omega
        self.ma = np.ones(n)

    def calculate_next_portfolio(self):
        price_changes = np.array(self.price_changes[-1])
        self.ma = np.mean(self.prices[-self.omega:], axis=0) / self.prices[-1]
        x_bar = np.mean(self.ma)


        alpha = 0 if np.sum((self.ma - x_bar * np.ones(self.ma.size)) ** 2) == 0 else self.loss(self.portfolio, self.ma) / np.sum((self.ma - x_bar * np.ones(self.ma.size)) ** 2)
        new_weights = self.portfolio + alpha * (self.ma - x_bar * np.ones(self.ma.size))
        new_weights = self.normalise(new_weights)
        
        return new_weights
    

    def update(self, time, price_changes):
        super().update(time, price_changes)
        self.prices = self.prices[-self.omega:]
        self.price_changes = self.price_changes[-self.omega:]

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

    
