from binance.account import account
import binance.market as market


#Currencies to Include in selection
CURRENCIES = ['ETH', 'EOS', 'FTT', 'LTC', 'BCH', 'ADA']
#Quote Assets
QUOTES = ['BTC', 'BNB']
RISKLESS = 'USDT'

def main():

	#load wallet and get balances
	wallet = account(keys.API, keys.SECRET)
	print(wallet.balances)

	#get current prices
	prices = market.prices([currency + RISKLESS for currency in CURRENCIES + QUOTES])
	#price array


	#calculate portfolio weights

	


if __name__ == '__main__':
	main()