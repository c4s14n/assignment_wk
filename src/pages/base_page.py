import logging
import os
from typing import Annotated

from selenium.webdriver.common.by import By

from core.container import AppContainer
from src.wrappers.scenario_context import ScenarioContext
from dependency_injector.wiring import inject, Provide

log = logging.getLogger(__name__)


class BasePage:
    """Base class for all page objects. Provides common locators and navigation."""
    _users_page_link = (By.LINK_TEXT, "Users")
    _home_page_link = (By.LINK_TEXT, "Home")
    _add_users_page_link = (By.LINK_TEXT, "Add Users")
    _cancel_button = (By.XPATH, "//button[normalize-space(.)='Cancel']")

    @inject
    def __init__(self, context: Annotated[ScenarioContext, Provide[AppContainer.scenario_context]]):
        """Inject scenario context and store its wrapper for browser interactions."""
        self._wrapper = context.wrapper

    def _navigate(self, path):
        """Open a page relative to BASE_URL using the given path."""
        self._wrapper.get_url(os.environ["BASE_URL"] + path)

    def cancel(self):
        log.info("...Cancel USER update")
        self._wrapper.find_element(self._cancel_button).click()
