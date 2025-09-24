"""Pytest execution configuration for Setup and Teardown"""
import logging

import pytest
from dotenv import load_dotenv

from core.container import AppContainer
from src.models.factories.users import build_user, user_test_data_to_payload
from src.wrappers.user_api_client import UserApiClient

log = logging.getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
def run_before_and_after_tests():
    """setup"""
    load_dotenv()
    yield
    """teardown"""


@pytest.fixture()
def ui_context():
    container = AppContainer()
    container.init_resources()
    container.wire(packages=["src.pages", "tests"])
    yield container
    container.unwire()
    container.shutdown_resources()


def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker("ui"):
            item.fixturenames.append("ui_context")


@pytest.fixture
def user_payload(request) -> dict:
    """
    Indirect param fixture.
    Returns a ready-to-send JSON payload.
    """
    overrides = request.param or {}
    user = build_user(overrides)
    return user_test_data_to_payload(user)


@pytest.fixture
def api_client():
    log.info("Providing UserApiClient")
    client = UserApiClient()
    yield client
    log.info("Running UserApiClient context cleanup")
    client.cleanup_created_users()
