# CUSTOM CALO
import logging

# From https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/12344609#12344609
import atexit
from time import time, strftime, localtime
from datetime import timedelta

def secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))

def log(msg, elapsed=None):
    line = "="*40

    print(line)
    print(secondsToStr(), '-', msg)

    if elapsed:
        el_msg = f"Elapsed time: {elapsed}"
        print(el_msg)
        use_logger(msg, el_msg)
    else:
        use_logger(msg)

    print(line)
    print()

def use_logger(msg, msg2 = None):
    line = "="*40
    logger = logging.getLogger("crawl_DCFP")

    logger.info(line)
    logger.info(f"{msg} - {secondsToStr()}")
    if msg2:
        logger.info(msg2)
    logger.info(line)

def endlog():
    end = time()
    elapsed = end-start
    log("End Program", secondsToStr(elapsed))

# Added by me
def get_start():
    return start

start = time()
atexit.register(endlog)
log("Start Program")