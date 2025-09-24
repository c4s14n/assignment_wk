import logging
from typing import Any, Iterable, Literal, Union, Optional

import pytest
import pytest_check as check
from pydantic import TypeAdapter
from requests import Response
from selenium.webdriver.remote.webelement import WebElement

from src.models.factories.users import UserTestData, UsersRowData

log = logging.getLogger(__name__)


def validate_users_not_matching(expected_user, actual_user):
    log.info("..Validate that user object is not identical to expected")
    same_fields = (
            expected_user.name == actual_user.name
            and expected_user.username == actual_user.username
            and expected_user.email == actual_user.email
            and expected_user.phone == actual_user.phone
    )
    check.is_false(same_fields, f'Users are identical user1: {expected_user!r} \n user2: {actual_user!r}')


def validate_users_are_matching(expected_user: UserTestData, actual_user: UsersRowData):
    log.info("..Validate that user object matches expected")
    same_fields = (
            expected_user.name == actual_user.name
            and expected_user.username == actual_user.username
            and expected_user.email == actual_user.email
            and expected_user.phone == actual_user.phone
    )
    check.is_true(same_fields, f'Users are NOT identical user1: {expected_user!r} \n user2: {actual_user!r}')


def validate_user_update(before_user, after_user, expected_changes: dict):
    log.info("..Validate user details were updated as expected")
    for field, value in expected_changes.items():
        if value is None or isinstance(value, WebElement):
            continue

        after_val = getattr(after_user, field, None)
        before_val = getattr(before_user, field, None)

        check.equal(after_val, value,
                    f"{field!r} did not update to expected {value!r}")
        check.not_equal(before_val, after_val,
                        f"{field!r} did not change")

    for field in vars(before_user):
        if field not in expected_changes and hasattr(after_user, field):
            before_val = getattr(before_user, field)
            after_val = getattr(after_user, field)

            if before_val is None or after_val is None:
                continue
            if isinstance(before_val, WebElement) or isinstance(after_val, WebElement):
                continue
            check.equal(before_val, after_val,
                        f"{field!r} unexpectedly changed")


def validate_status_and_time(
        response: Response,
        expected_status: Union[int, Iterable[int]] = 200,
        max_response_ms: int = 500,
        *,
        check_json_content_type: bool = True,
):
    """Soft-assert status code and time response (optionally) verify JSON content type."""
    log.info("..Validating response code")
    if isinstance(expected_status, int):
        expected_codes = {expected_status}
    else:
        expected_codes = set(expected_status)
    check.is_true(
        response.status_code in expected_codes,
        f"Expected HTTP {expected_status}, got {response.status_code!r}"
    )
    log.info(f"..Validating response time is less then {max_response_ms}")
    elapsed_ms = response.elapsed.total_seconds() * 1000
    check.less(
        elapsed_ms, max_response_ms,
        f"Response time expected < {max_response_ms} ms, got {elapsed_ms:.1f} ms"
    )

    if check_json_content_type:
        log.info(f"..Validating content-type")
        content_type = (response.headers.get("Content-Type") or "").lower()
        check.is_true("json" in content_type, f"Content-Type should be JSON, got: {content_type!r}")


def validate_response(
        response: Response,
        expected_model: Any,
        expected_status: Union[int, Iterable[int]],
        *,
        max_response_ms: int = 500,
        expect_empty: Optional[bool] = False,
        many: Literal[True, False, "auto"] = "auto",
):
    """
    High-level validation:
      1) validates status/time (soft asserts)
      2) parses JSON
      3) validates schema (hard fail)

    Returns the parsed/validated object(s).
    """
    validate_status_and_time(response, expected_status, max_response_ms)
    if response.status_code == 204:
        pytest.fail("Got 204 No Content but attempted to validate a body.")

    log.info(f"..Validating response is JSON")
    try:
        payload = response.json()
    except ValueError as e:
        pytest.fail(f"Invalid JSON body: {e}")

    log.info(f"..Validating response Schema")
    if many == "auto":
        many = isinstance(payload, list)
    try:
        validator = TypeAdapter(list[expected_model] if many else expected_model)
        parsed = validator.validate_python(payload)
    except Exception as e:
        pytest.fail(f"Schema validation failed: {e}")

    if expect_empty is not None:
        log.info(f"..Validating response is {'empty' if expect_empty else 'non-empty'}")
        try:
            responses_count = len(parsed)
        except TypeError:
            responses_count=len([parsed])
        is_empty = (responses_count == 0)
        check.equal(
            is_empty, expect_empty,
            f"Expected {'empty' if expect_empty else 'non-empty'} object, got: {parsed!r}"
        )

    return parsed
