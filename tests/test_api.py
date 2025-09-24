import logging

import pytest

from src.models.factories.users import user_test_data_to_payload, UserTestData
from src.models.user_model import UserModel
from src.steps.validation_steps import validate_response, validate_status_and_time, validate_user_update

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "params",
    [None,
     {"id": 1},
     {"id": [1, 2, 3]}], ids=["all_users", "single_user_by_id", "multiple_user_by_id"], )
def test_positive_get_users(api_client, params):
    resp = api_client.get("/user/", params=params)
    validate_response(response=resp, expected_model=UserModel, expected_status=200, max_response_ms=500)
    users = resp.json()
    assert len(users) > 0, f"Expected at least one user (got {len(users)})"
    if params:
        expected_ids = params["id"]
        if not isinstance(expected_ids, (list, tuple, set)):
            expected_ids = [expected_ids]

        actual_ids = [user["id"] for user in users]
        assert set(actual_ids) == set(expected_ids), \
            f"Expected ids {expected_ids}, got {actual_ids}"
        assert len(actual_ids) == len(expected_ids), \
            f"Expected {len(expected_ids)} users, got {len(actual_ids)}"


@pytest.mark.parametrize(
    "params, expected_status",
    [
        ({"id": 1}, 200),
        ({"id": 1}, 404),
        ({"id": "string"}, {400, 422}),
        ({"id": "!#"}, {400, 422}),
        ({"id": -82}, {400, 422}),
        ({"id": " "}, {400, 422}),
    ],
    ids=[
        "tolerated_resource_absence_200_code_but_empty",
        "user_not_exist",
        "bad_id_string",
        "bad_id_symbol",
        "bad_id_negative",
        "bad_id_space",
    ]
)
def test_negative_get_users(api_client, params, expected_status):
    api_client = api_client
    resp = api_client.get("/user/", params=params)
    validate_response(response=resp,
                      expected_model=UserModel,
                      expected_status=expected_status,
                      max_response_ms=100,
                      expect_empty=True)


@pytest.mark.parametrize(
    "user_payload, expected_status",
    [
        pytest.param({}, 201, id="valid_random_user"),
        pytest.param({"email": "not-an-email"}, {400, 422}, id="invalid_email"),
        pytest.param({"username": ""}, 400, id="empty_username"),
        pytest.param({"phone": "somestring"}, {400, 422}, id="bad_phone_format"),
        pytest.param({"phone": None}, {400, 422}, id="null_phone"),
        pytest.param({"name": " "}, 400, id="empty_name"),
    ],
    indirect=["user_payload"],
)
def test_create_api_user(api_client, user_payload, expected_status):
    resp = api_client.post("/user/", json=user_payload)

    validate_response(
        response=resp,
        expected_model=UserModel,
        expected_status=expected_status,
        max_response_ms=500,
        expect_empty=False
    )
    # print(resp.json())


@pytest.mark.parametrize(
    "user_payload, expected_status",
    [
        pytest.param({}, 200, id="valid_full_update"),
        pytest.param({"email": "test@email.com", "username": "some_username"}, 200, id="valid_partial_update"),
        pytest.param({"email": "not-an-email"}, {400, 422}, id="invalid_email"),
        pytest.param({"username": ""}, 400, id="empty_username"),
        pytest.param({"name": " "}, 400, id="empty_name"),
        pytest.param({"phone": "bad"}, {400, 422}, id="bad_phone"),
    ],
    indirect=["user_payload"],
)
def test_update_user_put(api_client, user_payload, expected_status):
    created = api_client.create_user_for_test(user_payload)
    uid = created["id"]
    params = {"id": uid}
    original_user = api_client.get("/user/", params=params)
    print(original_user.json())
    print(original_user.json())
    resp = api_client.put(f"/user/{uid}", json=user_payload)

    updated = validate_response(
        response=resp,
        expected_model=UserModel,
        expected_status=expected_status,
        max_response_ms=500,
        expect_empty=False
    )

    assert updated.id == uid
    for key in ("name", "username", "email", "phone"):
        if key not in user_payload:
            assert getattr(updated, key) == created[key]


@pytest.mark.parametrize(
    "user_payload, expected_status",
    [
        pytest.param({}, 200, id="valid_delete_user"),
    ],
    indirect=["user_payload"],
)
def test_delete_user(api_client, user_payload, expected_status):
    created = api_client.create_user_for_test(user_payload)
    uid = created["id"]
    resp = api_client.delete("/user/", id_resource=uid)
    params = {"id": uid}
    validate_status_and_time(response=resp,
                             expected_status=expected_status,
                             max_response_ms=500)

    original_user = api_client.get("/user/", params=params)
    validate_response(response=original_user,
                      expected_model=UserModel,
                      expected_status=expected_status,
                      max_response_ms=500,
                      expect_empty=True)


@pytest.mark.parametrize(
    "user_payload, expected_status",
    [
        pytest.param({}, 200, id="valid_end_2_end"),
    ],
    indirect=["user_payload"],
)
def test_end_2_end_api(api_client, user_payload, expected_status):
    new_user = api_client.post("/user/", json=user_payload)

    created_user = validate_response(
        response=new_user,
        expected_model=UserModel,
        expected_status=201,
        max_response_ms=500,
        expect_empty=False
    )

    user_payload["email"] = "updatedtest@email.com"
    user_payload["username"] = "updated_username"
    expected_changes = UserTestData(email="updatedtest@email.com", username="updated_username")

    update_user = api_client.patch(f'/user/{created_user.id}', json=user_payload)

    validate_response(
        response=update_user,
        expected_model=UserModel,
        expected_status=expected_status,
        max_response_ms=500,
        expect_empty=False
    )
    params = {"id": created_user.id}
    retrieve_user = api_client.get("/user/", params=params)
    updated_user=validate_response(
        response=retrieve_user,
        expected_model=UserModel,
        expected_status=expected_status,
        max_response_ms=500,
        expect_empty=False
    )
    validate_user_update(created_user, updated_user[0], user_test_data_to_payload(expected_changes))
    delete_user = api_client.delete("/user/", id_resource=created_user.id)
    validate_status_and_time(response=delete_user,
                             expected_status=expected_status,
                             max_response_ms=500)

    get_deleted = api_client.get("/user/", params=params)
    validate_response(response=get_deleted,
                      expected_model=UserModel,
                      expected_status=expected_status,
                      max_response_ms=500,
                      expect_empty=True)
