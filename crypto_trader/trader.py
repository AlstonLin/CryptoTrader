import threading
import time
from crypto_trader.api import API

TRADING_CURRENCIES = ['BTC', 'ETH']

class Trader(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config
        self.api = API(
            self.config['geminiApiKey'],
            self.config['geminiApiSecret'],
            self.config['sandbox'],
        )

    def update(self):
        balance = self.api.getBalance()
        currentPrices = self.api.getMostRecentPrice()
        worth = self.getPortfolioWorth(balance, currentPrices)
        for symbol in TRADING_CURRENCIES:
            self.updateCurrency(symbol, worth, balance, currentPrices)
        self.printBalance(balance, currentPrices)

    def getPortfolioWorth(self, balance, currentPrices):
        worth = float(balance['USD'])
        for symbol in TRADING_CURRENCIES:
            tradeSymbol = self.getTradeSymbol(symbol)
            worth += float(balance[symbol]) * float(currentPrices[tradeSymbol]['last'])
        return worth

    def updateCurrency(self, symbol, portfolioWorth, balance, currentPrices):
        tradeSymbol = self.getTradeSymbol(symbol)
        currencyWorth = float(balance[symbol]) * float(currentPrices[tradeSymbol]['last'])
        pctDiff = currencyWorth / portfolioWorth - self.config['targetPct'][symbol] / 100
        # Buy more to get to target
        if pctDiff * 100 < -1 * self.config['minTradePercentage']:
            usdBuy = portfolioWorth * abs(pctDiff)
            if usdBuy < float(balance['USD']):
                askPrice = float(currentPrices[tradeSymbol]['ask'])
                buyAmount = usdBuy / askPrice
                self.api.buy(tradeSymbol, round(buyAmount, 8), askPrice)
        elif pctDiff * 100 > self.config['minTradePercentage']:
            usdSell = portfolioWorth * pctDiff
            bidPrice = float(currentPrices[tradeSymbol]['bid'])
            sellAmount = usdSell / bidPrice
            self.api.sell(tradeSymbol, round(sellAmount, 6), bidPrice)

    def printBalance(self, balance, currentPrices):
        print('Your Balance')
        print('USD - {}'.format(balance['USD']))
        for symbol in TRADING_CURRENCIES:
            tradeSymbol = self.getTradeSymbol(symbol)
            symbolWorth = float(balance[symbol]) * float(currentPrices[tradeSymbol]['last'])
            print('{} - {}(${} USD)'.format(symbol, balance[symbol], symbolWorth))
        print('TOTAL - ${} USD'.format(self.getPortfolioWorth(balance, currentPrices)))

    def getTradeSymbol(self, symbol):
        return '{}usd'.format(symbol.lower())

    def run(self):
        while True:
            self.update()
            time.sleep(self.config['checkEvery'])
