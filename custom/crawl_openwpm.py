# CUSTOM CALO
import logging
from pathlib import Path

from custom.File_Helper import get_tranco_domains, PATH_TO_DCFP_HTML

from custom.Cookie_Handler import AcceptCookiesCommand

from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.storage.leveldb import LevelDbProvider
from openwpm.task_manager import TaskManager

def main(args):
    NUM_BROWSERS = args.browsers
    TOP_SITES = args.top
    MOBILE = args.mobile
    # display_mode = native, headless, xvfb
    DISPLAY = args.display_mode
    COOKIES = args.cookies

    #TODO log args param
    print("B: {}".format(NUM_BROWSERS))
    print("T: {}".format(TOP_SITES))
    print("M: {}".format(MOBILE))
    print("D: {}".format(DISPLAY))
    print("C: {}".format(COOKIES))

    # The list of sites that we wish to crawl
    sites = get_tranco_domains(TOP_SITES)
    sites.append("file://" + str(PATH_TO_DCFP_HTML))

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

    # Update TaskManager configuration (use this for crawl-wide settings)
    manager_params.data_directory = Path("./datadir/")
    manager_params.log_path = Path("./datadir/openwpm.log")

    # memory_watchdog and process_watchdog are useful for large scale cloud crawls.
    # Please refer to docs/Configuration.md#platform-configuration-options for more information
    # manager_params.memory_watchdog = True
    # manager_params.process_watchdog = True


    # Commands time out by default after 60 seconds
    with TaskManager(
        manager_params,
        browser_params,
        SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite")),
        LevelDbProvider(Path("./datadir/crawl-data-leveldb")),
    ) as manager:
        # Visits the sites
        for index, site in enumerate(sites):

            def callback(success: bool, val: str = site) -> None:
                logging.getLogger("openwpm").info(f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}")

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
