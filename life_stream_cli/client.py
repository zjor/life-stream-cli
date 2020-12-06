import logging
import requests as rq
import datetime as dt
from typing import Optional

from life_stream_cli.config import Config


class Client:
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.config = Config()

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
        shard_id = self.config.get_shard_id()
        if not shard_id:
            raise Exception("shard_id was not found, please authenticate")

        return {"X-ShardId": shard_id}

    def save(self, message):
        response = rq.post(
            f"{self.base_uri}/api/stream",
            headers=self._get_headers(),
            json={"payload": message})
        return response.json()

    def fetch(self, days=-1, tags=None):
        args = ""
        if days and days > -1:
            after_millis = int((dt.datetime.now().timestamp() - days * 24 * 3600) * 1000)
            args += f"after={after_millis}"

        if tags:
            tags = tags.split(",")
            args += "&" + "&".join(map(lambda x: f"tags={x}", tags))

        response = rq.get(f"{self.base_uri}/api/stream?{args}", headers=self._get_headers())
        if response.status_code == rq.codes.ok:
            return response.json()
        else:
            logging.warning(f"fetch: {response.status_code}")
            return None

    def delete(self, id_):
        response = rq.delete(f"{self.base_uri}/api/stream/id/{id_}", headers=self._get_headers())
        if not response.status_code == rq.codes.ok:
            logging.warning(f"delete: {response.status_code}")
            return False
        return True
