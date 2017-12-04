import yaml
import sched
import time

from crypto_trader.trader import Trader

# Constants
CONFIG_FILE = 'config.yaml'
SECRETS_FILE = 'secrets.yaml'

# Helper Functions
def get_config():
    with open(CONFIG_FILE, 'r') as config_file:
        config = yaml.load(config_file)
    with open(SECRETS_FILE, 'r') as secrets_file:
        config.update(yaml.load(secrets_file))
    return config

if __name__ == '__main__':
    Trader(get_config()).start()
