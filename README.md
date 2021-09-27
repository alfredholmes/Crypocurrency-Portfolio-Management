# MAMR, OLMAR, and PAMR simulations for binance exchange
Implementation of PAMR and MAMR portfolio management algorithms for online portfolio management and analysis of cryptocurrency assets.

### MAMR and PAMR Simulations
The scripts `MAMR.py` and `PAMR.py` simulate the returns that the portfolio selection algorithms would have achived had the algorithm been running. We see that MAMR outperforms PAMR in general, although parameter fitting has only been done by eye - no system has been implemented (yet). The MAMR implementation differes slightly from the paper by using a different moving average for the return prediction which empirically enjoys better results.

#### MAMR 12 hour - 0.1% Trading Fee
![MAMR 12 hour](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/Figure_0.png)
##### Example Portfolio Through Time
![Portfolio through time](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/example_portfolio.png)

#### PAMR 30 minute Performance - with the trading fee of 0.1%
Parameters fitted to maximise the mean daily return, algorithm runs every 30 minutes
![PAMR-2 Performance](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/PAMR-BTC-comparison.png)


### Requirements
	pip3 install requests numpy scipy  


### To run PAMR/MAMR simulations
	git clone https://github.com/alfredholmes/Binance-Portfolio-Management.git
	cd Binance-Portfolio-Management
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
