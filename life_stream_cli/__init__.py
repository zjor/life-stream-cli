import click
import datetime as dt
import getpass
import logging
import colorama
from collections import defaultdict
from termcolor import colored
from prompt_toolkit import prompt

from life_stream_cli.client import Client
from life_stream_cli.config import Config

from life_stream_cli.subcommands.config import config_command
from life_stream_cli.subcommands.config.config_utils import get_endpoint, get_active_profile
from life_stream_cli.subcommands.config.credentials_utils import load_credentials, store_credentials, Credentials

colorama.init()

logging.basicConfig(level=logging.INFO)

REMOTE_HOST = "http://api.lifestream.176.102.64.189.xip.io"
LOCAL_HOST = "http://localhost:8080"

host = REMOTE_HOST


# host = LOCAL_HOST


def do_login(client) -> bool:
    print("Please login or register first")
    email = input("Email: ")
    password = getpass.getpass()
    shard_id = client.login(email, password)
    if not shard_id:
        print("Seems you don't have an account, registering...")
        shard_id = client.register(email, password)
        if not shard_id:
            print("Something terribly wrong happened, exiting")
            return False
        else:
            print("Success!")
    else:
        print("Success!")
    store_credentials(Credentials(email, shard_id))
    return True


def colorize_tag(tag):
    fores = ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    backs = ['on_grey', 'on_red', 'on_green', 'on_yellow', 'on_blue', 'on_magenta', 'on_cyan', 'on_white']
    ix = hash(tag) % 8
    return colored(tag, fores[ix], attrs=['bold'])


def format_entries(entries, show_id=False):
    grouped = defaultdict(list)
    for entry in entries:
        created_at = dt.datetime.fromtimestamp(entry["createdAt"] / 1000)
        date = dt.datetime.strftime(created_at, "%Y-%m-%d")
        time = dt.datetime.strftime(created_at, "%H:%M:%S")

        line = ""
        if show_id:
            line += entry["id"] + " "

        line += f"[{time}]"

        if len(entry["tags"]) > 0:
            c_tags = map(colorize_tag, entry['tags'])
            line += f" {', '.join(c_tags)}"

        prefix = "\n" if "\n" in entry["raw"] else " "
        line += f"{prefix}{entry['raw']}"
        grouped[date].append(line)

    return grouped


client = Client(get_endpoint(), None)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    global client
    endpoint = get_endpoint()
    credentials = load_credentials()
    if not credentials:
        if do_login(Client(endpoint, None)):
            credentials = load_credentials()
            client = Client(endpoint, credentials.shard_id)
    else:
        client = Client(endpoint, credentials.shard_id)
    if ctx.invoked_subcommand is None:
        search(["-n 7"])


@cli.command()
@click.option("--set", "set_name", required=False, type=str)
@click.option("--get", "get_name", required=False, type=str)
@click.option("--unset", "unset_name", required=False, type=str)
@click.option("--reset", "reset", is_flag=True)
def config(set_name, get_name, unset_name, reset):
    config_command(set_name, get_name, unset_name, reset)


@cli.command()
def login():
    do_login(client)


@click.argument('words', nargs=-1)
@click.option('-f', '--filename')
@cli.command()
def save(words, filename):
    if filename:
        with open(filename, "r") as f_:
            content_ = f_.read().strip()
    else:
        if not words:
            content_ = prompt("> ", vi_mode=True, multiline=True)
        else:
            content_ = " ".join(words)
    print(client.save(content_))


@click.option('-n', '--days', type=int)
@click.option('-t', '--tags', type=str)
@click.option('--show-id', type=bool, default=False, is_flag=True)
@cli.command()
def search(days: int, tags: str, show_id: bool):
    items = format_entries(client.fetch(days=days, tags=tags), show_id)
    for item in items.items():
        print(f"[{colored(item[0], 'blue', attrs=['bold'])}]")
        for line in item[1]:
            print(f"  {line}")


@click.argument("id_", nargs=1)
@cli.command()
def delete(id_: str):
    if client.delete(id_):
        print(f"Message {id_} was deleted")


@cli.command()
def whoami():
    active_profile = get_active_profile()
    endpoint = get_endpoint()
    credentials = load_credentials()
    email = credentials.email if credentials else "not authorized"
    print(f"Profile: {active_profile}\nEndpoint: {endpoint}\nEmail: {email}")
