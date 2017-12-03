import yaml
import sched
import time

from crypto_trader import update

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

def start_scheduler(config):
    scheduler = sched.scheduler(time.time, time.sleep)
    def run_task(c): 
        update.update(c)
        scheduler.enter(30, 1, run_task, (config, ))
    scheduler.enter(0, 1, run_task, (config, ))
    scheduler.run()

if __name__ == '__main__':
    start_scheduler(get_config())
