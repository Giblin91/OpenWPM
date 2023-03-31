# CUSTOM CALO
import logging
import random

from custom.File_Helper import get_tranco_domains, get_dcfp_logger, PATH_TO_DCFP_HTML, DATADIR, OWPM_LOG, SQLITE, LEVELDB
from custom.Cookie_Handler import AcceptCookiesCommand

from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.storage.leveldb import LevelDbProvider
from openwpm.task_manager import TaskManager

def format_args(args):

    line = "*"*40
    out_str = "\n"

    out_str += line + "\n"
    out_str += f"Num of Browsers:\t{args.browsers}\n"
    out_str += f"Top Sites to Crawl:\t{args.top}\n"
    out_str += f"Emulate Mobile:\t\t{args.mobile}\n"
    out_str += f"Display Mode:\t\t{args.display_mode}\n"
    out_str += f"Accept Cookies:\t\t{args.cookies}\n"
    out_str += line

    return out_str

def gen_random_crawl_id(id_size = 20):

    crawl_id = ""
    
    for i in range(id_size):
        crawl_id += chr(random.randint(ord('a'), ord('z')))

    return crawl_id

def main(args):
    NUM_BROWSERS = args.browsers
    TOP_SITES = args.top
    MOBILE = args.mobile
    # display_mode = native, headless, xvfb
    DISPLAY = args.display_mode
    COOKIES = args.cookies

    CRAWL_ID = gen_random_crawl_id()

    # Logging Parameters
    formatted_args = format_args(args)
    dcfp_logger = get_dcfp_logger() # We do not setup, because we assume done in Time class
    dcfp_logger.info(formatted_args)

    # The list of sites that we wish to crawl
    # We want our DCFP site to crawl first, to have it as "control" site
    # Then we append retrieved data
    sites = ["file://" + str(PATH_TO_DCFP_HTML)]
    #sites = ["https://adobe.com", "https://tiktok.com"]
    sites += get_tranco_domains(TOP_SITES)

    # Loads the default ManagerParams
    # and NUM_BROWSERS copies of the default BrowserParams

    manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
    browser_params = [BrowserParams(display_mode=DISPLAY) for _ in range(NUM_BROWSERS)]

    # Update browser configuration (use this for per-browser settings)
    for browser_param in browser_params:
        # Record HTTP Requests and Responses
        browser_param.http_instrument = True # could be useful as side measurement
        # Record cookie changes
        browser_param.cookie_instrument = False
        # Record Navigations
        browser_param.navigation_instrument = False
        # Record JS Web API calls
        browser_param.js_instrument = True
        # Record the callstack of all WebRequests made
        browser_param.callstack_instrument = False # to see if a script sent smth back
        # Record DNS resolution
        browser_param.dns_instrument = False
        browser_param.save_content = True

        browser_param.custom_params = {"isMobile" : MOBILE}

    # Update TaskManager configuration (use this for crawl-wide settings)
    manager_params.data_directory = DATADIR
    manager_params.log_path = OWPM_LOG

    # memory_watchdog and process_watchdog are useful for large scale cloud crawls.
    # Please refer to docs/Configuration.md#platform-configuration-options for more information
    # manager_params.memory_watchdog = True
    # manager_params.process_watchdog = True

    dcfp_logger.info(f"Starting Crawl [{CRAWL_ID}]")

    # Commands time out by default after 60 seconds
    with TaskManager(
        manager_params,
        browser_params,
        SQLiteStorageProvider(SQLITE),
        LevelDbProvider(LEVELDB),
    ) as manager:
        # Visits the sites
        for index, site in enumerate(sites):

            def callback(success: bool, val: str = site, i : int = index) -> None:
                log_msg = f"CommandSequence for {i}-{val} ran {'successfully' if success else 'unsuccessfully'}"
                logging.getLogger("openwpm").info(log_msg)
                
                if success:
                    dcfp_logger.info(log_msg)
                else:
                    dcfp_logger.warning(log_msg)

            # Parallelize sites over all number of browsers set above.
            command_sequence = CommandSequence(
                site,
                site_rank=index,
                callback=callback,
            )

            # Start by visiting the page
            command_sequence.append_command(GetCommand(url=site, sleep=3), timeout=60)

            if COOKIES:
                command_sequence.append_command(AcceptCookiesCommand())

            # Run commands across all browsers (simple parallelization)
            manager.execute_command_sequence(command_sequence)
        
    dcfp_logger.info(f"Terminating Crawl [{CRAWL_ID}]")
