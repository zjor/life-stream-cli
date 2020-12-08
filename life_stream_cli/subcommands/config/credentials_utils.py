import configparser
from pathlib import Path

from life_stream_cli.subcommands.config.config_utils import ensure_dir, get_active_profile

CREDENTIALS_FILENAME = "credentials"


class Credentials:
    def __init__(self, email, shard_id):
        self.email = email
        self.shard_id = shard_id

    def __str__(self):
        return f"Credentials(email: {self.email}, shard_id: {self.shard_id})"


def store(profile, **kwargs):
    config = configparser.ConfigParser()
    dir_path = ensure_dir()
    filename = Path(str(dir_path) + f"/{CREDENTIALS_FILENAME}")
    if filename.exists():
        config.read(str(filename))
    config[profile] = kwargs
    with open(str(filename), "w") as f:
        config.write(f)


def store_credentials(credentials):
    store(get_active_profile(), **credentials.__dict__)


def load_credentials():
    config = configparser.ConfigParser()
    dir_path = ensure_dir()
    filename = Path(str(dir_path) + f"/{CREDENTIALS_FILENAME}")
    if not filename.exists():
        return None
    config.read(str(filename))
    profile = get_active_profile()
    if profile in config:
        section = config[profile]
        return Credentials(email=section["email"], shard_id=section["shard_id"])
    else:
        return None
