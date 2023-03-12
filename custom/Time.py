# CUSTOM CALO
# From https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution/12344609#12344609
import atexit
from time import time, strftime, localtime
from datetime import timedelta
from custom.File_Helper import get_dcfp_logger

dcfp_logger = get_dcfp_logger(True)

def secondsToStr(elapsed=None) -> str:
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))

def log(msg, elapsed=False, add_line=False):
    line = "="*40

    if add_line:
        msg = "\n" + line + "\n" + msg + "\n"

    if elapsed:
        now = time()
        e_time = now-start
        msg += f"Elapsed time: {secondsToStr(e_time)}\n"
    
    if add_line:
        msg += line
    
    dcfp_logger.info(msg)

def endlog():
    log("End Program", True, True)


start = time()
atexit.register(endlog)
log("Start Program", add_line=True)