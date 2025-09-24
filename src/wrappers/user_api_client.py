import logging
import os
from typing import Optional, Dict, Any

import requests

from src.models.factories.users import user_test_data_to_payload, build_user

logger = logging.getLogger(__name__)


class UserApiClient:
    """Simple API client for User endpoints (GET, POST, PUT, DELETE)."""
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL').lower()
        if not self.base_url:
            raise ValueError("API_BASE_URL environment variable must be set")
        self.base_url = self.base_url.rstrip("/").lower()
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._timeout = int(os.getenv("API_TIMEOUT", "10"))
        self._created_ids: list[int] = []

    def _url(self, path: str) -> str:
        """Builds a full URL from base URL and relative path."""
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Send a GET request with optional query parameters."""
        url = self._url(path)
        logger.info(f"GET {url!r} params: {params!r}")
        resp = self.session.get(url, params=params, timeout=self._timeout)
        logger.debug(f"Response {resp.status_code!r} having response like {resp.text[:300]!r}")
        return resp

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Send a POST request with optional JSON body."""
        url = self._url(path)
        logger.info(f"POST {url!r} json: {json!r}")
        resp = self.session.post(url, json=json, timeout=self._timeout)
        self._track_created_id(resp)
        logger.debug(f"Response {resp.status_code!r} having response like {resp.text[:300]!r}")
        return resp

    def put(self, path: str, json: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Send a PUT request with optional JSON body."""
        url = self._url(path)
        logger.info(f"PUT {url!r} json: {json!r}")
        resp = self.session.put(url, json=json, timeout=self._timeout)
        logger.debug(f"Response {resp.status_code!r} having response like {resp.text[:300]!r}")
        return resp

    def patch(self, path: str, json: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Send a PATCH request with optional JSON body."""
        url = self._url(path)
        logger.info(f"PATCH {url!r} json: {json!r}")
        resp = self.session.patch(url, json=json, timeout=self._timeout)
        logger.debug(f"Response {resp.status_code!r} having response like {resp.text[:300]!r}")
        return resp

    def delete(self, path: str,  id_resource: int) -> requests.Response:
        """Send a DELETE request for a resource ID."""
        url = self._url(path+str(id_resource))
        logger.info(f"DELETE {url!r}")
        resp = self.session.delete(url, timeout=self._timeout)
        logger.debug(f"Response {resp.status_code!r} having response like {resp.text[:300]!r}")
        return resp

    def create_user_for_test(self, payload):
        # payload = user_test_data_to_payload(build_user({}))
        resp = self.post("/user/", json=payload)
        assert resp.status_code == 201, f"Setup create failed: {resp.text}"
        return resp.json()

    def cleanup_created_users(self):
        """Delete all tracked created resources."""
        logger.info(f"Context cleaning...")
        while self._created_ids:
            uid = self._created_ids.pop()
            try:
                resp = self.delete("/user/",id_resource=uid)
                if resp.status_code not in (200, 202, 204, 404):
                    logger.warning(f"Delete of {uid} returned {resp.status_code}")
            except Exception as e:
                logger.warning(f"Failed to delete {uid}: {e}")

    def _track_created_id(self, resp: requests.Response):
        """Extract and store the id if response is 201 Created."""
        if resp.status_code != 201:
            return
        try:
            body = resp.json()
            if isinstance(body, dict) and "id" in body:
                self._created_ids.append(body["id"])
                logger.info(f"Tracked created id={body['id']}")
        except Exception as e:
            logger.warning(f"Could not parse id from response: {e}")
