import sys, csv
sys.path.append("./")

from os import listdir

from portfolioManagement.portfolioManagement import PAMRPortfolioManager

from matplotlib import pyplot as plt
import numpy as np
import datetime


def get_data():
    files = listdir("data/")
    
    prices = {}

    for file in files:
        currency = file.split('USDT.csv')[0]
        #construct a dict {opentime: openprice}
        prices[currency] = {}
        with open(f'data/{file}', 'r') as f:
            csvfile = csv.DictReader(f)
            for line in csvfile:
                prices[currency][int(float(line['time']))] = float(line['open'])
            

    print('collecting times')

    open_times = set()
    for currency in prices:
        open_times = open_times.union(prices[currency])


    currencies = [currency for currency in prices]

    times = sorted(open_times)

    print('creating price change array')
    price_changes = []
    previous_price = {currency: -1 for currency in currencies}
    for time in times:
        price_change = []
        for currency in currencies:
            if time in prices[currency]:
                if previous_price[currency] == -1: 
                    price_change.append(1)
                else:
                    price_change.append(prices[currency][time] / previous_price[currency])
                previous_price[currency] = prices[currency][time]

            #else just keep everything the same
            else:
                price_change.append(1)
        price_changes.append(price_change)

    print('done')
    return currencies, times, price_changes

        


    

def main():
    currencies, times, price_changes = get_data()
  
    datetimes = [datetime.datetime.fromtimestamp(t / 1000) for t in times]

    manager = PAMRPortfolioManager(len(currencies), 0.5, 10) 

    values = []

    print('running managers')
    
    for time, changes in zip(times, price_changes):
        manager.update(time, changes)
        values.append(manager.value)

    fig, axs = plt.subplots(2)
    
    axs[0].plot(datetimes, values)
    
    prices = np.cumprod(price_changes, axis=0)


    print('Plotting currencies')

    for i, currency in enumerate(currencies):
        axs[1].plot(datetimes, [p[i] for p in prices], label=currency)
    plt.legend() 
    plt.show()



if __name__ == "__main__":
   main() 

