from dataclasses import dataclass, asdict
from typing import Optional

from faker import Faker
from selenium.webdriver.remote.webelement import WebElement

fake = Faker()


@dataclass
class UserTestData:
    """
    Lightweight container for user test data.
    Used for generating fake users in API tests.
    """
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


def get_fake_user() -> UserTestData:
    """
    Build a valid random user using Faker.
    Returns a UserTestData instance ready to serialize into a request payload.
    """
    return UserTestData(
        name=fake.first_name(),
        username=fake.user_name(),
        email=fake.email(),
        phone=fake.phone_number(),
    )


def build_user(overrides: dict | None = None) -> UserTestData:
    """Start from a valid fake user, then override fields for a scenario."""
    user = get_fake_user()
    for k, v in (overrides or {}).items():
        setattr(user, k, v)
    return user


def user_test_data_to_payload(user: UserTestData) -> dict:
    """Dataclass transformation to JSON-able dict."""
    return asdict(user)


@dataclass(frozen=True)
class UsersColumnHeaderActions:
    """
    Groups elements for a Users column in header :
    field, header cell, and optional action buttons.
    """
    field: str
    title: str
    column_header: WebElement
    sort_btn: Optional[WebElement]
    menu_btn: Optional[WebElement]


@dataclass(frozen=True)
class UsersRowData:
    """
    Groups values and action buttons for a Users table row.
    """
    id: str
    name: str
    username: str
    email: str
    phone: str
    edit: WebElement
    remove: WebElement
