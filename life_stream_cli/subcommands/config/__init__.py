from life_stream_cli.subcommands.config import config_utils


def config_command(set_name):
    print(f"setting: {set_name}")
    config = config_utils.load_config()
    print(config)
