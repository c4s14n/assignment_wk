import logging

from selenium.webdriver.common.by import By

from src.models.factories.users import UserTestData
from src.pages.base_page import BasePage

log = logging.getLogger(__name__)


class AddUserPage(BasePage):
    """Page object for the 'Add User' screen."""
    __path = "add"
    __title = (By.CSS_SELECTOR, ".MuiBox-root.MuiBox-root-6 > :first-child")
    __name = (By.NAME, "name")
    __user_name = (By.NAME, "username")
    __email = (By.NAME, "email")
    __phone = (By.NAME, "phone")
    __add_button = (By.XPATH, "//button[normalize-space(.)='Add User']")

    def navigate(self):
        """Open the Add User page."""
        self._navigate(self.__path)
        log.info(f'User navigates to {self.title} Page')
        return self

    def navigate_to_homepage(self):
        self._wrapper.find_element(self._home_page_link).click()

    @property
    def title(self):
        """Return the page title text."""
        return self._wrapper.find_element(self.__title).text

    @property
    def __name_input(self):
        return self._wrapper.find_element(self.__name)

    @property
    def __username_input(self):
        return self._wrapper.find_element(self.__user_name)

    @property
    def __email_input(self):
        return self._wrapper.find_element(self.__email)

    @property
    def __phone_input(self):
        return self._wrapper.find_element(self.__phone)

    def add_user(self, user: UserTestData):
        """Fill the user form with data from a UserTestData object."""
        log.info(f"Filling user form with following details:{user!r}")
        self.__name_input.send_keys(user.name)
        self.__username_input.send_keys(user.username)
        self.__email_input.send_keys(user.email)
        self.__phone_input.send_keys(user.phone)
        return self

    def save(self):
        """Click the 'Add User' button to submit the form."""
        log.info("...Save USER details")
        self._wrapper.find_element(self.__add_button).click()

    # def cancel(self):
    #     """Click the 'Cancel' button to discard the form."""
    #     log.info("...Cancel USER creation")
    #     self._wrapper.find_element(self._cancel_button).click()

