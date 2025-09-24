import logging
from typing import Optional, List

from src.models.factories.users import UsersColumnHeaderActions, UsersRowData
from src.pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

log = logging.getLogger(__name__)


class UsersPage(BasePage):
    """Page object for the Users table (grid)."""
    __path = "all"
    __header_elements = (By.CSS_SELECTOR, "div[role='row'][aria-rowindex='1']")
    __header_column = (By.CSS_SELECTOR, "div[role='columnheader']")
    __menu_element = (By.CSS_SELECTOR, 'ul[role="menu"]')
    __menu_items = (By.CSS_SELECTOR, 'li[role="menuitem"]')
    __sort_button = (By.CSS_SELECTOR, "button[aria-label='Sort']")
    __menu_button = (By.CSS_SELECTOR, "button[aria-label='Menu'][aria-haspopup='true']")
    __drop_down_rows = (By.CSS_SELECTOR, 'div[role="button"]')
    __drop_down_menu = (By.CSS_SELECTOR, 'ul[role="listbox"]')
    __drop_down_menu_items = (By.CSS_SELECTOR, 'li[role="option"]')
    __users_grid = (By.CSS_SELECTOR, '[role="row"].MuiDataGrid-row')
    __edit_button = (By.XPATH, "//button[normalize-space(.)='Edit']")
    __remove_button = (By.XPATH, "//button[normalize-space(.)='Remove']")

    @property
    def _rows_on_grid(self):
        """Return all currently visible rows in the grid."""
        return self._wrapper.find_elements(self.__users_grid)

    def navigate(self):
        """Navigate to the Users page."""
        log.info(f'User navigates to Users Page')
        self._navigate(self.__path)
        return self

    def _safe_find(self, ctx, locator) -> Optional[object]:
        """Try to find element in context using wrapper, return None if not found."""
        try:
            return ctx.find_element(*locator)
        except NoSuchElementException:
            return None

    def __get_header_actions(self) -> List[UsersColumnHeaderActions]:
        """Collect header columns with their actions (sort, menu)."""
        header_row = self._wrapper.find_element(self.__header_elements)
        columns = header_row.find_elements(self.__header_column)
        results: List[UsersColumnHeaderActions] = []
        for column in columns:
            field = (column.get_attribute("data-field") or "").strip()
            title = column.text.strip()
            sort_btn = self._safe_find(column, self.__sort_button)
            menu_btn = self._safe_find(column, self.__menu_button)

            results.append(
                UsersColumnHeaderActions(
                    field=field,
                    title=title,
                    column_header=column,
                    sort_btn=sort_btn,
                    menu_btn=menu_btn
                )
            )
        return results

    def __get_menu_options_from_header(self, header_name: str):
        """Open column menu and return visible options for given header."""
        header_elements = self.__get_header_actions()
        for element in header_elements:
            if element.title == header_name:
                self._wrapper.hover_over(element.menu_btn)
                element.menu_btn.click()
        menu = self._wrapper.find_element(self.__menu_element)
        menu_options = menu.find_elements(self.__menu_items)
        visible_opt = [opt for opt in menu_options if opt.is_displayed()]
        if not visible_opt:
            raise RuntimeError("Menu appeared but none is visible")
        return visible_opt

    def pick_menu_option_for_column(self, column_name: str, menu_option: str):
        """Select a menu option from a column header."""
        log.info(f'User is selecting [{menu_option}] for [{column_name}] column')
        options = self.__get_menu_options_from_header(column_name)
        menu_choice = [n for n in options if n.text == menu_option]
        if len(menu_choice) == 0:
            raise RuntimeError("No element was identified by this option")
        elif len(menu_choice) > 1:
            first_element = menu_choice[0]
            log.warning(
                f'There were more than one elements detected, first element will be used: [{first_element.text}]')
            first_element.click()
        else:
            menu_choice[0].click()

    def get_user_with_username(self, username: str):
        """Return list of users in grid with matching username."""
        log.info(f'Filter grid by username: [{username}] if present')
        users_grid = self.get_users_from_page_grid()
        lis_users = [user for user in users_grid if user.username == username]
        return lis_users

    def get_users_from_page_grid(self, rows_per_page: str = "25")->List[UsersRowData]:
        """Extract all users currently loaded in the grid based on rows_per_page option."""
        self.select_rows_per_page(rows_per_page)
        seen_ids = set()
        results = []
        while True:
            rows = self._rows_on_grid
            if not rows:
                break
            for row in rows:
                row_id = row.get_attribute("data-id") or row.get_attribute("aria-rowindex")
                if row_id in seen_ids:
                    continue
                id_val = row.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="id"]').text.strip()
                name = row.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="name"]').text.strip()
                username = row.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="username"]').text.strip()
                email = row.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="email"]').text.strip()
                phone = row.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="phone"]').text.strip()
                buttons = row.find_elements(By.CSS_SELECTOR, 'div[role="cell"][data-field="actions"] > button')

                results.append(UsersRowData(
                    id=id_val,
                    name=name,
                    username=username,
                    email=email,
                    phone=phone,
                    edit=buttons[0] if len(buttons) > 0 else None,
                    remove=buttons[1] if len(buttons) > 1 else None
                ))
                seen_ids.add(row_id)
            last_row = rows[-1]
            self._wrapper.scroll_to_elm(last_row)
            new_rows = self._rows_on_grid
            new_last = new_rows[-1].get_attribute("data-id") if new_rows else None
            if new_last in seen_ids:
                break
        return results

    def select_rows_per_page(self, rows_per_page: str):
        """Change the 'rows per page' setting in the grid."""
        log.info(f'Getting users within the limit of {rows_per_page} rows per page')
        self._wrapper.find_element(self.__drop_down_rows).click()
        menu = self._wrapper.find_element(self.__drop_down_menu)
        menu_options = menu.driver.find_element(By.CSS_SELECTOR, f'li[role="option"][data-value="{rows_per_page}"]')
        menu_options.click()

    def remove(self):
        """Click the Remove button."""
        log.info("Click Remove button")
        self._wrapper.find_element(self.__remove_button).click()

    def get_first_user_in_grid(self) -> UsersRowData:
        """Return first user row currently visible in the grid."""
        rows = self._rows_on_grid
        results = []
        for element in rows:
            id_val = element.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="id"]')
            name = element.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="name"]')
            username = element.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="username"]')
            email = element.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="email"]')
            phone = element.find_element(By.CSS_SELECTOR, 'div[role="cell"][data-field="phone"]')
            buttons = element.find_elements(By.CSS_SELECTOR, 'div[role="cell"][data-field="actions"] > button')
            results.append(
                UsersRowData(
                    id=id_val.text.strip(),
                    name=name.text.strip(),
                    username=username.text.strip(),
                    email=email.text.strip(),
                    phone=phone.text.strip(),
                    edit=buttons[0] if len(buttons) > 0 else None,
                    remove=buttons[1] if len(buttons) > 1 else None
                )
            )
        return results[0]
