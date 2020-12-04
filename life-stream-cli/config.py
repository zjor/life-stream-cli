from pathlib import Path
from typing import Optional


class Config:
    DIR_NAME = ".life-stream"
    SHARD_ID_FILENAME = "shard_id"

    def __init__(self):
        self.base_path = Path(str(Path.home()) + f"/{Config.DIR_NAME}")
        self.shard_id_path = Path(str(self.base_path) + f"/{Config.SHARD_ID_FILENAME}")

    def dir_exists(self) -> bool:
        return self.base_path.exists()

    def shard_id_exists(self) -> bool:
        return self.shard_id_path.exists()

    def store_shard_id(self, value) -> None:
        self.base_path.mkdir(exist_ok=True)
        with open(self.shard_id_path, "w") as f:
            f.write(value)

    def get_shard_id(self) -> Optional[str]:
        if not self.shard_id_exists():
            return None
        with open(self.shard_id_path, "r") as f:
            return f.readlines()[0].strip()


if __name__ == "__main__":
    config = Config()
    print(config.dir_exists())
    print(config.shard_id_exists())

    config.store_shard_id("123456")
    print(config.get_shard_id())

    config.store_shard_id("0987654")
    print(config.get_shard_id())
