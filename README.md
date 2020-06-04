# Automated Portfolio Management Analysis for Binance Cryptocurrency Exchange
Implementation of PAMR and MAMR portfolio management algorithms for analysis and online portfolio management of cryptocurrency assets.

### Performance - with the trading fee of 0.1%
Parameters fitted to maximise the mean daily return, algorithm runs every 30 minutes
![PAMR-2 Performance](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/PAMR-BTC-comparison.png)

Current portfolio consists of 8 large market cap coins.

### Portfolio through time 
![Portfolio through time](https://raw.githubusercontent.com/alfredholmes/BinancePAMR/master/results/portfolio-through-time.png)

### Requirements
	pip3 install requests numpy scipy  

### To run PAMR simulation
	git clone https://github.com/alfredholmes/binancePAMR.git
	cd binancePAMR
	python3 data/get_candles.py 
	python3 analysis/PAMR.py

### References / useful papers
#### Passive aggressive mean reversion 
Li, B., Zhao, P., Hoi, S.C.H. et al. PAMR: Passive aggressive mean reversion strategy for portfolio selection. Mach Learn 87, 221–258 (2012). https://doi.org/10.1007/s10994-012-5281-z
https://link.springer.com/content/pdf/10.1007/s10994-012-5281-z.pdf
#### Multiperiodical Asymmetric Mean Reversion
Peng, Zijin & Xu, Weijun & Li, Hongyi. (2020). A Novel Online Portfolio Selection Strategy with Multiperiodical Asymmetric Mean Reversion. Discrete Dynamics in Nature and Society. 2020. 1-13. 10.1155/2020/5956146. 
http://downloads.hindawi.com/journals/ddns/2020/5956146.pdf
