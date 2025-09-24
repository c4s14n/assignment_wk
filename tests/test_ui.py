import logging

import pytest

from src.models.factories.users import UserTestData, get_fake_user, user_test_data_to_payload
from src.pages.add_user_page import AddUserPage
from src.pages.update_user_page import UpdateUserPage
from src.pages.users_page import UsersPage
from src.steps.validation_steps import validate_user_update, validate_users_are_matching, validate_users_not_matching

log = logging.getLogger(__name__)


@pytest.mark.ui
def test_create_new_user():
    add_user_page = AddUserPage()
    add_user_page.navigate()
    test_user = get_fake_user()
    add_user_page.add_user(test_user).save()
    users_page = UsersPage()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    last_created_user = users_page.get_user_with_username(test_user.username)
    validate_users_are_matching(test_user, last_created_user[0])


@pytest.mark.ui
def test_cancel_user_creation():
    users_page = UsersPage()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    expected_first_user = users_page.get_first_user_in_grid()
    add_user_page = AddUserPage()
    add_user_page.navigate()
    test_user_data = UserTestData(name="john12", username="wick1", email="test@test.com", phone="1234567")
    add_user_page.add_user(test_user_data).cancel()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    actual_first_user = users_page.get_first_user_in_grid()
    validate_users_are_matching(expected_first_user, actual_first_user)


@pytest.mark.parametrize("rows_per_page", ["25", "50", "100"])
@pytest.mark.ui
def test_user_can_pick_rows_per_page(rows_per_page):
    users_page = UsersPage()
    users_page.navigate()
    list_of_users = users_page.get_users_from_page_grid(rows_per_page=rows_per_page)
    log.info("Validate number of rows per page are displayed correctly")
    assert len(list_of_users) <= int(rows_per_page), \
        f'Rows displayed expected {int(rows_per_page)} but got {len(list_of_users)}'


@pytest.mark.ui
def test_user_can_be_updated():
    users_page = UsersPage()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    get_user_before = users_page.get_first_user_in_grid()
    get_user_before.edit.click()
    test_user_data = UserTestData(name="John", email="wick@wick.com")
    update_page = UpdateUserPage()
    update_page.edit_user(test_user_data).update()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    get_user_after = users_page.get_first_user_in_grid()
    validate_user_update(get_user_before, get_user_after, expected_changes=user_test_data_to_payload(test_user_data))


@pytest.mark.ui
def test_user_cancel_update():
    users_page = UsersPage()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    user_to_be_updated = users_page.get_first_user_in_grid()
    user_to_be_updated.edit.click()
    test_user_data = UserTestData(name="John", email="wick@wick.com")
    update_page = UpdateUserPage()
    update_page.edit_user(test_user_data).cancel()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    get_user_again = users_page.get_first_user_in_grid()
    validate_user_update(user_to_be_updated, get_user_again, expected_changes={})


@pytest.mark.ui
def test_user_are_unique_by_details():
    test_user = UserTestData(name="John1", email="wick1@wick.com", phone="12345678", username="jw")
    add_user_page = AddUserPage()
    add_user_page.navigate()
    add_user_page.add_user(test_user).save()
    users_page = UsersPage()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    first_created_user = users_page.get_user_with_username(test_user.username)
    add_user_page = AddUserPage()
    add_user_page.navigate()
    add_user_page.add_user(test_user).save()
    users_page = UsersPage()
    users_page.navigate()
    users_page.pick_menu_option_for_column("ID", "Sort by DESC")
    second_created_user = users_page.get_user_with_username(test_user.username)
    validate_users_not_matching(first_created_user[0], second_created_user[0])