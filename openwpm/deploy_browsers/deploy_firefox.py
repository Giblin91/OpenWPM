import json
import logging
import os.path
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from easyprocess import EasyProcessError
from multiprocess import Queue
from pyvirtualdisplay import Display
from selenium import webdriver

from ..commands.profile_commands import load_profile
from ..config import BrowserParamsInternal, ConfigEncoder, ManagerParamsInternal
from ..utilities.platform_utils import get_firefox_binary_path
from . import configure_firefox
from .selenium_firefox import FirefoxBinary, FirefoxLogInterceptor, Options

DEFAULT_SCREEN_RES = (1366, 768)
#ANDROID_SCREEN_RES = (360, 592)  # Moto G5
ANDROID_SCREEN_RES = (412, 691)  # Pixel 2 XL
logger = logging.getLogger("openwpm")


def deploy_firefox(
    status_queue: Queue,
    browser_params: BrowserParamsInternal,
    manager_params: ManagerParamsInternal,
    crash_recovery: bool,
) -> Tuple[webdriver.Firefox, Path, Optional[Display]]:
    """
    launches a firefox instance with parameters set by the input dictionary
    """
    firefox_binary_path = get_firefox_binary_path()

    root_dir = os.path.dirname(__file__)  # directory of this file

    browser_profile_path = Path(tempfile.mkdtemp(prefix="firefox_profile_"))
    status_queue.put(("STATUS", "Profile Created", browser_profile_path))

    # Use Options instead of FirefoxProfile to set preferences since the
    # Options method has no "frozen"/restricted options.
    # https://github.com/SeleniumHQ/selenium/issues/2106#issuecomment-320238039
    fo = Options()
    # Set a custom profile that is used in-place and is not deleted by geckodriver.
    # https://firefox-source-docs.mozilla.org/testing/geckodriver/CrashReports.html
    # Using FirefoxProfile breaks stateful crawling:
    # https://github.com/openwpm/OpenWPM/issues/423#issuecomment-521018093
    fo.add_argument("-profile")
    fo.add_argument(str(browser_profile_path))

    # CUSTOM CALO - START
    screen_res = DEFAULT_SCREEN_RES
    
    if browser_params.custom_params["isMobile"]:
        screen_res = ANDROID_SCREEN_RES
        #agent = " Mozilla/5.0 (Android 7.0; Mobile; rv:55.0) Gecko/55.0 Firefox/55.0" # Moto G5
        # https://github.com/duckduckgo/tracker-radar-collector/blob/3e9f49e46e5051e9f3d26bcd3be054447af887e4/crawler.js#L9
        agent = " Mozilla/5.0 (Linux; Android 10; Pixel 2 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Mobile Safari/537.36"
        fo.set_preference("general.useragent.override", agent)
    # CUSTOM CALO - END

    assert browser_params.browser_id is not None
    if browser_params.seed_tar and not crash_recovery:
        logger.info(
            "BROWSER %i: Loading initial browser profile from: %s"
            % (browser_params.browser_id, browser_params.seed_tar)
        )
        load_profile(
            browser_profile_path,
            browser_params,
            browser_params.seed_tar,
        )
    elif browser_params.recovery_tar:
        logger.debug(
            "BROWSER %i: Loading recovered browser profile from: %s"
            % (browser_params.browser_id, browser_params.recovery_tar)
        )
        load_profile(
            browser_profile_path,
            browser_params,
            browser_params.recovery_tar,
        )
    status_queue.put(("STATUS", "Profile Tar", None))

    display_mode = browser_params.display_mode
    display_pid = None
    display_port = None
    display = None
    if display_mode == "headless":
        fo.headless = True
        fo.add_argument("--width={}".format(screen_res[0]))
        fo.add_argument("--height={}".format(screen_res[1]))
    if display_mode == "xvfb":
        try:
            display = Display(visible=False, size=screen_res)
            display.start()
            display_pid, display_port = display.pid, display.display
        except EasyProcessError:
            raise RuntimeError(
                "Xvfb could not be started. \
                Please ensure it's on your path. \
                See www.X.org for full details. \
                Commonly solved on ubuntu with `sudo apt install xvfb`"
            )
    # Must do this for all display modes,
    # because status_queue is read off no matter what.
    status_queue.put(("STATUS", "Display", (display_pid, display_port)))

    if browser_params.extension_enabled:
        # Write config file
        extension_config: Dict[str, Any] = dict()
        extension_config.update(browser_params.to_dict())
        extension_config["logger_address"] = manager_params.logger_address
        extension_config[
            "storage_controller_address"
        ] = manager_params.storage_controller_address
        extension_config["testing"] = manager_params.testing
        ext_config_file = browser_profile_path / "browser_params.json"
        with open(ext_config_file, "w") as f:
            json.dump(extension_config, f, cls=ConfigEncoder)
        logger.debug(
            "BROWSER %i: Saved extension config file to: %s"
            % (browser_params.browser_id, ext_config_file)
        )

        # TODO restore detailed logging
        # fo.set_preference("extensions.@openwpm.sdk.console.logLevel", "all")

    # Configure privacy settings
    configure_firefox.privacy(browser_params, fo)

    # Set various prefs to improve speed and eliminate traffic to Mozilla
    configure_firefox.optimize_prefs(fo)

    # Intercept logging at the Selenium level and redirect it to the
    # main logger.
    interceptor = FirefoxLogInterceptor(browser_params.browser_id)
    interceptor.start()

    # Set custom prefs. These are set after all of the default prefs to allow
    # our defaults to be overwritten.
    for name, value in browser_params.prefs.items():
        logger.info(
            "BROWSER %i: Setting custom preference: %s = %s"
            % (browser_params.browser_id, name, value)
        )
        fo.set_preference(name, value)

    # Launch the webdriver
    status_queue.put(("STATUS", "Launch Attempted", None))
    fb = FirefoxBinary(firefox_path=firefox_binary_path)
    driver = webdriver.Firefox(
        firefox_binary=fb,
        options=fo,
        log_path=interceptor.fifo,
    )

    # driver created

    # Add extension
    if browser_params.extension_enabled:

        # Install extension
        ext_loc = os.path.join(root_dir, "../../Extension/openwpm.xpi")
        ext_loc = os.path.normpath(ext_loc)
        driver.install_addon(ext_loc, temporary=True)
        logger.debug(
            "BROWSER %i: OpenWPM Firefox extension loaded" % browser_params.browser_id
        )

    # set window size
    driver.set_window_size(*screen_res)

    # Get browser process pid
    if hasattr(driver, "service") and hasattr(driver.service, "process"):
        pid = driver.service.process.pid
    elif hasattr(driver, "binary") and hasattr(driver.binary, "process"):
        pid = driver.binary.process.pid
    else:
        raise RuntimeError("Unable to identify Firefox process ID.")

    status_queue.put(("STATUS", "Browser Launched", int(pid)))

    return driver, browser_profile_path, display
