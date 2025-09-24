from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


class DriverManager(ABC):
    """Abstract base for WebDriver managers."""

    @abstractmethod
    def _create_driver(self, options=None) -> WebDriver:
        """Subclasses must implement WebDriver creation."""
        raise NotImplementedError

    def get_driver(self, options=None) -> WebDriver:
        """Public factory for creating a WebDriver instance."""
        return self._create_driver(options)


class ChromeManager(DriverManager):
    def _create_driver(self, options=None):
        if options is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--no-default-browser-check")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver


class FirefoxManager(DriverManager):
    def _create_driver(self, options=None):
        if options is None:
            options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(options)
        return driver
