import logging

from src.models.factories.users import user_test_data_to_payload, build_user

log = logging.getLogger(__name__)


class UsersTracker:
    def __init__(self, api_client):
        """
        Test helper that creates users via the API and tracks their IDs
        so they can be cleaned up after test run."""
        self.api = api_client
        self.ids = []

    def create(self, overrides=None):
        """Create a user with Faker + overrides and track its id."""
        payload = user_test_data_to_payload(build_user(overrides))
        resp = self.api.post("/user/", json=payload)
        assert resp.status_code == 201, f"Create failed: {resp.text!r}"

        body = resp.json()
        user_id = body["id"]
        self.ids.append(user_id)
        return {"id": user_id, "payload": payload, "body": body}

    def cleanup(self):
        """Delete all tracked users."""
        for user_id in reversed(self.ids):
            try:
                request = self.api.delete(f"/user/{user_id}")
                if request.status_code not in (200, 202, 204, 404):
                    log.warning(f"Failed to delete user {user_id}: {request.status_code}")
            except Exception as e:
                log.warning(f"There were issues deleting user {user_id}: {e}")
        self.ids.clear()
