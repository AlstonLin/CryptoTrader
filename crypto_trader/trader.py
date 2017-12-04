import threading
import time
from crypto_trader.api import API

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
        print(currentPrices)

    def run(self):
        while True:
            self.update()
            time.sleep(self.config['checkEvery'])
