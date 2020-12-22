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

    def register(self, email, password) -> Optional[str]:
        response = rq.post(f"{self.base_uri}/api/auth/register", json={
            "email": email,
            "password": password
        })
        if response.status_code == rq.codes.ok:
            return response.json()["shardId"]
        else:
            return None

    def _get_headers(self):
        return {"X-ShardId": self.shard_id}

    def save(self, message, created_at=None):
        response = rq.post(
            f"{self.base_uri}/api/stream",
            headers=self._get_headers(),
            json={
                "payload": message,
                "createdAt": created_at
            })
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
            return None

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
