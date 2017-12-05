import requests
import base64
import os
import yaml
import hmac
import json
import hashlib

SANDBOX_API = 'https://api.sandbox.gemini.com'
REAL_API = 'https://api.gemini.com'

class API:
    def __init__(self, apiKey, apiSecret, sandbox):
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.sandbox = sandbox
        # Loads state
        if self.sandbox:
            self.stateFile = 'state_sandbox.yaml'
        else:
            self.stateFile = 'state.yaml'
        if os.path.exists(self.stateFile):
            with open(self.stateFile, 'r') as f:
                state = yaml.load(f)
                self.nonce = state['nonce']
        else:
            # Default state
            self.nonce = 0

    def buy(self, symbol, quantity, price):
        print('BUY {} x {} @ {}'.format(quantity, symbol, price))
        response = self._makeRequest(
            '/v1/order/new',
            {
                'symbol': symbol,
                'amount': quantity,
                'price': price,
                'side': 'buy',
                'type': 'exchange limit',
            },
        )
        return response

    def sell(self, symbol, quantity, price):
        print('SELL {} x {} @ {}'.format(quantity, symbol, price))
        response = self._makeRequest(
            '/v1/order/new',
            {
                'symbol': symbol,
                'amount': quantity,
                'price': price,
                'side': 'sell',
                'type': 'exchange limit',
            },
        )
        return response

    def getPriceHistory(self):
        data = {}
        for symbol in ['btcusd', 'ethusd']:
            url = '{0}/v1/trades/{1}'.format(
                SANDBOX_API if self.sandbox else REAL_API,
                symbol,
            )
            response = requests.request('GET', url).json()
            data[symbol] = response
        return data

    def getMostRecentPrice(self):
        data = {}
        for symbol in ['btcusd', 'ethusd']:
            url = '{0}/v1/pubticker/{1}'.format(
                SANDBOX_API if self.sandbox else REAL_API,
                symbol,
            )
            response = requests.request('GET', url).json()
            data[symbol] = response
        return data

    def getBalance(self):
        response = self._makeRequest(
            '/v1/balances',
            {},
        )
        return {
            balance['currency']: balance['amount'] for balance in response
        }

    def _makeRequest(self, url, payload):
        payload.update({
            'nonce': self.nonce,
            'request': url,
	})
        payload = base64.b64encode(json.dumps(payload).encode('UTF-8'))
        signature = hmac.new(
            self.apiSecret.encode('UTF-8'),
            payload,
            hashlib.sha384
        ).hexdigest()
        headers = {
	    'Content-Type': "text/plain",
	    'Content-Length': "0",
	    'X-GEMINI-APIKEY': self.apiKey,
	    'X-GEMINI-PAYLOAD': payload,
	    'X-GEMINI-SIGNATURE': signature,
	    'Cache-Control': "no-cache"
	}
        if self.sandbox:
            fullUrl = SANDBOX_API + url
        else:
            fullUrl = REAL_API + url
        response = requests.request('POST', fullUrl, headers=headers)
        self.nonce += 1
        self._saveState()
        return response.json()

    def _saveState(self):
        with open(self.stateFile, 'w') as f:
            state = {
                'nonce': self.nonce,
            }
            yaml.dump(state, f)

