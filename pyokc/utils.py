try:
    from pyokc.settings import DELAY
except ImportError:
    from settings import DELAY

import time

def sleep(seconds):
    # make a function to sleep here so that we can override with
    # fancier logic later
    time.sleep(seconds)
