# Automated Portfolio Management Analysis for Binance Cryptocurrency Exchange
Implementation of PAMR and MAMR portfolio management algorithms for online portfolio management and analysis of cryptocurrency assets.

### MAMR 12 hour
![MAMR 12 hour](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/Figure_0.png)
#### Example Portfolio Through Time
![Portfolio through time](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/example_portfolio.png)

### Performance - with the trading fee of 0.1%
Parameters fitted to maximise the mean daily return, algorithm runs every 30 minutes
![PAMR-2 Performance](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/PAMR-BTC-comparison.png)


### Requirements
	pip3 install requests numpy scipy  

### Binance Trading Bot
Create a file keys.py and assign the api key and secret key from a binance account to the variables api and secret respectively in the keys file. When the bot runs it gets the spot portfolio of the tracked currencies (currencies in the CURRENCIES variable) and runs the MAMR algorithm to calculate the next portfolio and then makes the trade (not currently implemented) in a way that minimises the trade volume to reduce fees. The state, along with the market data is then pickled and is opened on the next run. The parameters in the implementation expect the script to be run every 12 hours. 

### To run PAMR/MAMR simulations
	git clone https://github.com/alfredholmes/binancePAMR.git
	cd binancePAMR
	python3 data/get_candles_spot.py 
	python3 PAMR.py
	python3 MAMR.py

In general MAMR outperforms PAMR for cryptocurrency portfolios.

### References / useful papers
#### Passive aggressive mean reversion 
Li, B., Zhao, P., Hoi, S.C.H. et al. PAMR: Passive aggressive mean reversion strategy for portfolio selection. Mach Learn 87, 221–258 (2012). https://doi.org/10.1007/s10994-012-5281-z
https://link.springer.com/content/pdf/10.1007/s10994-012-5281-z.pdf
#### Multiperiodical Asymmetric Mean Reversion
Peng, Zijin & Xu, Weijun & Li, Hongyi. (2020). A Novel Online Portfolio Selection Strategy with Multiperiodical Asymmetric Mean Reversion. Discrete Dynamics in Nature and Society. 2020. 1-13. 10.1155/2020/5956146. 
http://downloads.hindawi.com/journals/ddns/2020/5956146.pdf
