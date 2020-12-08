import json
from pathlib import Path

DIR_NAME = ".life-stream"
CONFIG_FILENAME = "config.json"

default_config = {
    "version": "0.1.0",
    "params": {
        "active-profile": "default",
        "profiles": {
            "default": {
                "endpoint": "http://api.lifestream.176.102.64.189.xip.io"
            },
            "local": {
                "endpoint": "http://localhost:8080"
            }
        }
    }
}


def ensure_dir(dir_name=DIR_NAME):
    path = Path(str(Path.home()) + f"/{dir_name}")
    if not path.exists():
        path.mkdir()
    return path


def ensure_config_file():
    dir_path = ensure_dir(DIR_NAME)
    path = Path(str(dir_path) + f"/{CONFIG_FILENAME}")
    if not path.exists():
        store_config(default_config, str(path))
    return path


def store_config(config, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(config, indent=4))
        f.write('\n')


def load_config():
    filename = ensure_config_file()
    with open(filename) as f:
        return json.load(f), filename


def set_param(key, value):
    key_path = key.split(".")
    config, filename = load_config()
    params = config["params"]
    while len(key_path) > 1:
        if not key_path[0] in params:
            params[key_path[0]] = {}
        params = params[key_path[0]]
        key_path = key_path[1:]
    params[key_path[0]] = value
    store_config(config, filename)


def unset_param(key):
    key_path = key.split(".")
    config, filename = load_config()
    params = config["params"]
    while len(key_path) > 1:
        if not key_path[0] in params:
            params[key_path[0]] = {}
        params = params[key_path[0]]
        key_path = key_path[1:]
    params.pop(key_path[0], None)
    store_config(config, filename)


def get_param(key):
    key_path = key.split(".")
    config, filename = load_config()
    params = config["params"]
    while len(key_path) > 1:
        if not key_path[0] in params:
            params[key_path[0]] = {}
        params = params[key_path[0]]
        key_path = key_path[1:]
    return params[key_path[0]] if key_path[0] in params else None


def reset_config():
    _, filename = load_config()
    store_config(default_config, filename)


def get_active_profile():
    active_profile = get_param("active-profile")
    if not active_profile:
        raise Exception("active-profile is not set")
    return active_profile


def get_endpoint():
    active_profile = get_active_profile()
    key = f"profiles.{active_profile}.endpoint"
    endpoint = get_param(key)
    if not endpoint:
        raise Exception(f"Endpoint is not set for the key: {key}")
    return endpoint
