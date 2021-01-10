import logging
import requests as rq
import datetime as dt
from typing import Optional


class Client:
    def __init__(self, base_uri, shard_id):
        self.base_uri = base_uri
        self.shard_id = shard_id

    def login(self, email, password) -> Optional[str]:
        response = rq.post(f"{self.base_uri}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == rq.codes.ok:
            return response.json()["shardId"]
        elif response.status_code == rq.codes.unauthorized:
            json = response.json()
            logging.info(f"code: {json['code']}; message: {json['message']}")
            return None
        else:
            logging.warning(f"{response.status_code}")
            return None

    def register(self, username, email, password) -> Optional[str]:
        response = rq.post(f"{self.base_uri}/api/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        if response.status_code == rq.codes.ok:
            return response.json()["shardId"]
        else:
            logging.warning(f"{response.status_code}")
            return None

    def request_password_reset(self, email):
        response = rq.post(f"{self.base_uri}/api/auth/password/requestReset", json={
            "email": email,
        })
        if response.status_code == rq.codes.ok:
            return True
        else:
            logging.warning(f"{response.status_code}")
            return False

    def reset_password(self, email, code, password):
        response = rq.post(f"{self.base_uri}/api/auth/password/reset", json={
            "email": email,
            "code": code,
            "password": password
        })
        if response.status_code == rq.codes.ok:
            return response.json()["shardId"]
        else:
            logging.warning(f"{response.status_code}")
            return None

    def change_password(self, password: str):
        response = rq.post(
            f"{self.base_uri}/api/user/password",
            headers=self._get_headers(),
            json={
                "password": password
            })
        json = response.json()
        if response.status_code == rq.codes.ok:
            return json
        else:
            logging.warning(f"{response.status_code}")

    def get_profile(self) -> dict:
        response = rq.get(f"{self.base_uri}/api/user", headers=self._get_headers())
        return response.json()

    def update_profile(self, fields: dict) -> Optional[dict]:
        response = rq.post(
            f"{self.base_uri}/api/user",
            headers=self._get_headers(),
            json=fields)
        json = response.json()
        if response.status_code == rq.codes.ok:
            return json
        elif response.status_code == 400:
            logging.info(f"code: {json['code']}; message: {json['message']}")
        else:
            logging.warning(f"{response.status_code}")

    def _get_headers(self):
        return {"X-ShardId": self.shard_id}

    def save(self, message, created_at=None, published=False):
        response = rq.post(
            f"{self.base_uri}/api/stream",
            headers=self._get_headers(),
            json={
                "payload": message,
                "createdAt": created_at,
                "published": published
            })
        return response.json()

    def publish(self, id_):
        response = rq.post(
            f"{self.base_uri}/api/stream/id/{id_}/publish",
            headers=self._get_headers())
        return response.json()

    def update(self, id_, message):
        response = rq.post(
            f"{self.base_uri}/api/stream/id/{id_}",
            headers=self._get_headers(),
            json={"payload": message})
        return response.json()

    def fetch(self, days: int = -1, tags: str = None, keys: str = None):
        args = ""
        if days and days > -1:
            after_millis = int((dt.datetime.now().timestamp() - days * 24 * 3600) * 1000)
            args += f"after={after_millis}"

        if tags:
            tags = tags.split(",")
            args += "&" + "&".join(map(lambda x: f"tags={x}", tags))

        if keys:
            keys = keys.split(",")
            args += "&" + "&".join(map(lambda x: f"attrs={x}", keys))

        response = rq.get(f"{self.base_uri}/api/stream?{args}", headers=self._get_headers())
        if response.status_code == rq.codes.ok:
            return response.json()
        else:
            logging.warning(f"fetch: {response.status_code}")
            return []

    def fetch_by_id(self, id_):
        response = rq.get(f"{self.base_uri}/api/stream/id/{id_}", headers=self._get_headers())
        if response.status_code == rq.codes.ok:
            return response.json()
        else:
            logging.warning(f"fetch_by_id: {response.status_code}")
            return None

    def stats(self):
        response = rq.get(f"{self.base_uri}/api/stats/tags", headers=self._get_headers())
        if response.status_code == rq.codes.ok:
            return response.json()
        else:
            logging.warning(f"stats: {response.status_code}")
            return None

    def delete(self, id_):
        response = rq.delete(f"{self.base_uri}/api/stream/id/{id_}", headers=self._get_headers())
        if not response.status_code == rq.codes.ok:
            logging.warning(f"delete: {response.status_code}")
            return False
        return True
