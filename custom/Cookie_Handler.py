# CUSTOM CALO
import time
import logging

from bs4 import BeautifulSoup as bs

from custom.File_Helper import dump_list, PATH_TO_COOKIES

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

accept_words_list = []
GLOBAL_SELECTOR = "a, button, div, span, form, p"

def get_accept_words():
    """
    Reads the accept cookie consent words from file.
    """
    global accept_words_list

    if not accept_words_list:
        # Get list of words from .txt
        lines = open(PATH_TO_COOKIES, "r", encoding="utf8").readlines()
                    
        accept_words_list = [w.casefold().strip("\n") for w in lines]
    
    return accept_words_list

def find_accept_cookies(tag_list):
    global accept_words_list

    get_accept_words()

    ret = None

    # First button found is returned.
    # Any button find in list is given priority
    # NOTE: Priority is given to how buttons are ordered.
    for t in tag_list:
        txt = t.getText().casefold().strip("✓›! \n\t•")
        if txt in accept_words_list:
            ret = t
            break
        """
        else:
            # If word and text do not match, button text might contain a single valid keyword
            # i.e. "accept" in "accept all essential and not essential cookies"
            btn_words = txt.split(" ")
            for word in accept_words_list:
                if word in btn_words:
                    ret = t
                    # (Words list) First loop break
                    break
        # (Buttons) Second loop break, else it continued search
        if ret is not None:
            break
        """

    return ret

def find_as_button(soup : bs):
    buttons = soup.find_all("button")
    return find_accept_cookies(buttons)

def find_as_role(soup : bs):
    roles = soup.find_all(has_role_button)
    return find_accept_cookies(roles)

def has_role_button(tag):
    return tag.has_attr('role') and tag['role'] == 'button'

def find_as_id(soup : bs):
    id = soup.find_all(has_id_button)
    return find_accept_cookies(id)

def has_id_button(tag):
    return tag.has_attr('id') and tag['id'] == 'button'

def find_clickable(soup : bs):
    tag_found = find_as_button(soup)
    
    if not tag_found:
        tag_found = find_as_role(soup)
        
        if not tag_found:
            tag_found = find_as_id(soup)
    
    # Might still be None
    return tag_found

def get_possible_xpaths(clickable_tag):
    
    xpath_list = []

    att_id = "id" if clickable_tag.has_attr("id") else ""
    id_val = clickable_tag["id"] if clickable_tag.has_attr("id") else ""
    att_class = "class" if clickable_tag.has_attr("class") else ""
    class_val = clickable_tag["class"] if clickable_tag.has_attr("class") else ""
    text = clickable_tag.getText()
    
    if att_id and att_class and text:
        xpath = "//{}[@{}='{}' and @{}='{}' and text()='{}']".format(
            clickable_tag.name,
            att_id,
            id_val,
            att_class,
            class_val,
            text
        )
        xpath_list.append(xpath)

    if att_id and att_class:
        xpath = "//{}[@{}='{}' and @{}='{}']".format(
            clickable_tag.name,
            att_id,
            id_val,
            att_class,
            class_val
        )
        xpath_list.append(xpath)

    if att_id and text:
        xpath = "//{}[@{}='{}' and text()='{}']".format(
            clickable_tag.name,
            att_id,
            id_val,
            text,
        )
        xpath_list.append(xpath)
    
    if att_class and text:
        xpath = "//{}[@{}='{}' and text()='{}']".format(
            clickable_tag.name,
            att_class,
            class_val,
            text
        )
        xpath_list.append(xpath)
    
    if att_class:
        xpath = "//{}[@{}='{}']".format(
            clickable_tag.name,
            att_class,
            class_val,
        )
        xpath_list.append(xpath)

    if text:
        xpath = "//{}[text()='{}']".format(
            clickable_tag.name,
            text
        )
        xpath_list.append(xpath)
    
    return xpath_list

def click_banner(driver):

    accept_words_list = get_accept_words()

    banner_data = {"matched_containers": [], "candidate_elements": []}
    contents = driver.find_elements(By.CSS_SELECTOR, GLOBAL_SELECTOR)

    candidate = None

    for c in contents:
        try:
            if c.text.lower().strip(" ✓›!\n") in accept_words_list:
                candidate = c
                banner_data["candidate_elements"].append({"id": c.id,
                                                          "tag_name": c.tag_name,
                                                          "text": c.text,
                                                          "size": c.size
                                                          })
                break
        except:
            log("Exception in processing element: {}".format (c.id), "error")
            
    # Click the candidate
    if candidate is not None:
        try: # in some pages element is not clickable

            log("Clicking text: {}".format (candidate.text.lower().strip(" ✓›!\n")) )
            candidate.click()
            banner_data["clicked_element"] = candidate.id
            log("Clicked: {}".format (candidate.id) )
            
        except:
            log("Exception in candidate click", "error")
    else:
        log("Warning, no matching candidate", "warning")

    return banner_data

def log(msg, mode="info"):
    logger = logging.getLogger("openwpm")

    if mode == "info":
        logger.info(msg)
    elif mode == "error":
        logger.error(msg)
    else:
        logger.warning(msg)

def priv_accept(driver):
    dump_value = None

    # Following solution is extracted from https://github.com/marty90/priv-accept

    # Click Banner
    log("Searching Banner")
    banner_data = click_banner(driver)
    
    dump_value = "CLICK"
    if banner_data["candidate_elements"]:
        dump_value += "({})".format(banner_data["candidate_elements"][0]["text"])

    if not "clicked_element" in banner_data:
        
        dump_value = None
        
        try:
            iframe_contents = driver.find_elements(By.CSS_SELECTOR, "iframe")
            for content in iframe_contents:

                log("Switching to frame: {}".format(content.id) )
                
                try:
                    driver.switch_to.frame(content)
                    banner_data = click_banner(driver)
                    driver.switch_to.default_content()
                    if "clicked_element" in banner_data:
                        
                        dump_value = "CLICK"
                        if banner_data["candidate_elements"]:
                            dump_value += "({})".format(banner_data["candidate_elements"][0]["text"])

                        break
                except NoSuchFrameException:
                    driver.switch_to.default_content()
                    
                    log("Error in switching to frame", "error")
        except NoSuchElementException:
            driver.switch_to.default_content()
            
            log("Error searching iframe", "error")
    
    # timeout was a cmd line param, default was 5
    timeout = 5
    time.sleep(timeout)
    
    log("URL after click: {}".format(driver.current_url))
    
    return dump_value


class AcceptCookiesCommand(BaseCommand):
    """This command tries to "accept" all cookies on navigated page"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "AcceptCookiesCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:

        ex_list = set()
            
        soup = bs(webdriver.page_source, "html.parser", multi_valued_attributes=None)
        clickable_tag = find_clickable(soup)
        dump_value = None

        if clickable_tag:
            dump_value = "FOUND"

            xpaths = get_possible_xpaths(clickable_tag)
            
            for i, xpath in enumerate(xpaths):
                try:
                    clickable_element = webdriver.find_element(By.XPATH, xpath)
                    if clickable_element:

                        coord = clickable_element.location_once_scrolled_into_view
                        webdriver.execute_script("window.scrollTo({},{});".format(coord["x"], coord["y"]))
                        time.sleep(1)
                        
                        clickable_element.click()
                        time.sleep(5)
                        
                        dump_value = "CLICK({})".format(clickable_tag.getText().strip())
                        break
                except NoSuchElementException as nsee:
                    if i == (len(xpaths)-1):
                        dump_value = "ERROR"
                
                except Exception as e:
                    # Split on ".", select last [-1], drop last to char [:-2] ("'>")
                    ex_type = str(type(e)).split(".")[-1][:-2]
                    ex_list.add(ex_type)
                    if i == (len(xpaths)-1):
                        dump_value = "ERROR"
        
        #if not dump_value or dump_value == "ERROR":
        #    dump_value = priv_accept(webdriver)

        to_dump = "{} - {}".format(dump_value, webdriver.current_url)
        
        # We log list even if in the end a button was clicked
        if ex_list:
            to_dump += " --> {}".format(str(list(ex_list)))

        dump_list([to_dump], "accept_cookies.log", mode = "a")
