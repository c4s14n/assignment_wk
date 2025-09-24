import logging

from selenium.webdriver.common.by import By

from src.models.factories.users import UserTestData
from src.pages.base_page import BasePage

log = logging.getLogger(__name__)


class UpdateUserPage(BasePage):
    """Page object for the 'Update User' screen."""
    __path = "edit"
    __title = (By.CSS_SELECTOR, ".MuiBox-root.MuiBox-root-6 > :first-child")
    __name = (By.NAME, "name")
    __user_name = (By.NAME, "username")
    __email = (By.NAME, "email")
    __phone = (By.NAME, "phone")
    __update_user_button = (By.XPATH, "//button[normalize-space(.)='Update User']")

    @property
    def title(self):
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

    def edit_user(self, user: UserTestData):
        """Update user form fields with data from a UserTestData object.
        A value of None or '#' means skip updating that field.
        """
        log.info(f"Updating fallowing user details: {user!r}")
        if user.name not in (None, "#"):
            self.__name_input.clear()
            self.__name_input.send_keys(user.name)

        if user.username not in (None, "#"):
            self.__username_input.clear()
            self.__username_input.send_keys(user.username)

        if user.email not in (None, "#"):
            self.__email_input.clear()
            self.__email_input.send_keys(user.email)

        if user.phone not in (None, "#"):
            self.__phone_input.clear()
            self.__phone_input.send_keys(user.phone)

        return self

    def update(self):
        """Click the 'Update User' button."""
        log.info("...Update USER")
        self._wrapper.find_element(self.__update_user_button).click()
