import logging
import os
from typing import Optional

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from src.helpers.driver_factory import DriverFactory

log = logging.getLogger(__name__)


class ActionWrapper:
    """Convenience actions around ActionChains."""

    def __init__(self, driver):
        self.actions = ActionChains(driver)

    def hover_over(self, element: WebElement):
        self.actions.move_to_element(element).perform()

    def scroll_to_elm(self, element):
        self.actions.scroll_to_element(element).perform()


class ElementWrapper:
    """Element find/wait helpers for chaining."""

    def __init__(self, driver):
        self.__driver = driver
        self.__timeout = int(os.getenv("DEFAULT_TIMEOUT"), 10)
        self.__element: Optional[WebElement] = None

    def find_element(self, locator):
        """Wait for presence, set current element, and return self for chaining."""
        self.presence_of_element(locator)
        self.__element = self.__driver.find_element(*locator)
        return self

    def find_elements(self, locator) -> list[WebElement]:
        """Return all matching elements (no current-element side effect)."""
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.presence_of_all_elements_located(locator)
        )
        return self.__driver.find_elements(*locator)

    def wait_for_element_to_load(self, element):
        element_present = WebDriverWait(self.__driver, self.__timeout).until(ec.visibility_of(element))
        if not element_present:
            raise Exception("Element not found: {}".format(element))

    def presence_of_element(self, locator):
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.presence_of_element_located(locator)
        )

    def click(self):
        # element = self.__driver.find_element(*locator)
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.element_to_be_clickable(self.__element)
        )
        log.debug("...clicking element: <%s>", self.__element.text)
        self.__element.click()

    def send_keys(self, *value):
        # element = self.__driver.find_element(*locator)
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.visibility_of(self.__element)
        )
        self.__element.send_keys(*value)

    def is_displayed(self) -> bool:
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.visibility_of(self.__element)
        )
        return self.__element.is_displayed()

    def clear(self):
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.visibility_of(self.__element)
        )
        log.debug(f"...clear <{self.__element.tag_name!r}> element")
        select_key = Keys.CONTROL
        self.__element.click()
        self.__element.send_keys(select_key, "a")
        self.__element.send_keys(Keys.BACKSPACE)

    @property
    def text(self):
        WebDriverWait(self.__driver, self.__timeout).until(
            ec.visibility_of(self.__element)
        )
        return self.__element.text


class NavigationWrapper:
    """Navigation and context switching helpers."""
    def __init__(self, driver):
        self.__driver = driver

    def get_url(self, url):
        log.debug(f"...navigating to: <{url!r}> page")
        self.__driver.get(url)


class SeleniumDriverWrapper:
    """Thin pass-through to raw WebDriver for a few common calls."""
    def __init__(self, driver):
        self.__driver = driver

    def close(self):
        self.__driver.close()

    def quit(self):
        self.__driver.quit()

    def get_current_url(self):
        return self.__driver.current_url

    def execute_script(self, script, *args):
        return self.__driver.execute_script(script, *args)


class WebDriverWrapper(SeleniumDriverWrapper, ElementWrapper, NavigationWrapper, ActionWrapper):
    """Unified wrapper exposing element/nav/actions on a single object."""

    def __init__(self):
        self._driver = DriverFactory().make()
        ElementWrapper.__init__(self, self._driver)
        NavigationWrapper.__init__(self, self._driver)
        ActionWrapper.__init__(self, self._driver)
        SeleniumDriverWrapper.__init__(self, self._driver)

    @property
    def driver(self):
        return self._driver

    def quit(self):
        self._driver.quit()
