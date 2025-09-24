import logging
import os

from src.helpers.driver_managers import ChromeManager, FirefoxManager

log = logging.getLogger(__name__)


class DriverFactory:
    """Factory for creating Selenium WebDriver instances based on BROWSER env var."""
    def __init__(self):
        log.setLevel(logging.INFO)
        self.__browser_type = (os.getenv('BROWSER') or "chrome").lower()
        log.info(f"initiating f{self.__browser_type!r} webdriver")

    def make(self, options=None):
        """Return a configured WebDriver instance for the chosen browser."""
        if self.__browser_type == "chrome":
            driver = ChromeManager().get_driver(options=options)
            return driver
        elif self.__browser_type == "firefox":
            driver = FirefoxManager().get_driver(options=options)
        else:
            raise ValueError(f"Unsupported browser: {self.__browser_type!r}")
        return driver
