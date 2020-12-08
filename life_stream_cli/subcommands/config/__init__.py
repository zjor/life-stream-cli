import logging
from life_stream_cli.subcommands.config import config_utils


def config_command(set_name: str = None,
                   get_name: str = None,
                   unset_name: str = None,
                   reset: bool = False):
    if reset:
        config_utils.reset_config()
        logging.info("Config reset to defaults")
    elif set_name:
        key, value = set_name.split("=")
        config_utils.set_param(key, value)
    elif get_name:
        logging.info(f"{get_name} = {config_utils.get_param(get_name)}")
    elif unset_name:
        config_utils.unset_param(unset_name)
    else:
        logging.info("No options were specified")
