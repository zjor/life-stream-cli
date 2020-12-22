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


def do_login(client_) -> bool:
    print("Please login or register first")
    email = input("Email: ")
    password = getpass.getpass()
    shard_id = client_.login(email, password)
    if not shard_id:
        print("Seems you don't have an account, registering...")
        shard_id = client_.register(email, password)
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

        attrs = entry['attributes'] if 'attributes' in entry else None

        if attrs and len(attrs) > 0:
            line += "\n"
            for k, v in attrs.items():
                line += colored(f" {k}: {v} ", attrs=['reverse']) + " "
            line += "\n"

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


@cli.command(help="Sets local configurations")
@click.option("--set", "set_name", required=False, type=str)
@click.option("--get", "get_name", required=False, type=str)
@click.option("--unset", "unset_name", required=False, type=str)
@click.option("--reset", "reset", is_flag=True)
def config(set_name, get_name, unset_name, reset):
    config_command(set_name, get_name, unset_name, reset)


@cli.command(help="Logs in to the current endpoint")
def login():
    do_login(client)


@click.argument('words', nargs=-1)
@click.option('-f', '--filename', help="Takes record content from the file")
@click.option('--date', 'date_', type=str, help="Specifies creation date in format YYYY-mm-dd")
@cli.command(help="Creates a new record")
def save(words, filename, date_):
    if filename:
        with open(filename, "r") as f_:
            content_ = f_.read().strip()
    else:
        if not words:
            content_ = prompt("> ", vi_mode=True, multiline=True)
        else:
            content_ = " ".join(words)

    created_at = None
    if date_:
        created_at = int((dt.datetime.strptime(date_, "%Y-%m-%d") - dt.datetime.utcfromtimestamp(0))
                         .total_seconds() * 1000)

    print(client.save(content_, created_at))


@click.argument("id_", nargs=1)
@cli.command(help="Updates an existing record")
def edit(id_):
    existing = client.fetch_by_id(id_)
    content_ = prompt(">", vi_mode=True, multiline=True, default=existing['raw'])
    print(client.update(id_, content_))


@click.option('-n', '--days', type=int, help="n days back in the past")
@click.option('-t', '--tags', type=str, help="Tags in the format tag1,tag2 without hashes")
@click.option('-k', '--keys', type=str, help="Keys in the format key1:value1,key2:value2")
@click.option('--show-id', type=bool, default=False, is_flag=True, help="Display record IDs")
@click.option('--id', 'id_', type=str, help="Find a single record by ID")
@cli.command(help="Searches for the records")
def search(days: int, tags: str, keys: str, show_id: bool, id_: str):
    if id_:
        items = [client.fetch_by_id(id_)]
    else:
        items = client.fetch(days=days, tags=tags, keys=keys)

    total = len(items)

    items = format_entries(items, show_id)
    for item in items.items():
        print(f"[{colored(item[0], 'blue', attrs=['bold'])}]")
        for line in item[1]:
            print(f"  {line}")

    msg = colored(f"\nTotal: {total} records\n", color='grey')
    print(msg)


@click.argument("id_", nargs=1)
@cli.command(help="Deletes a record by ID")
def delete(id_: str):
    if client.delete(id_):
        print(f"Message {id_} was deleted")


@cli.command(help="Prints current user's email and the selected endpoint")
def whoami():
    active_profile = get_active_profile()
    endpoint = get_endpoint()
    credentials = load_credentials()
    email = credentials.email if credentials else "not authorized"
    print(f"Profile: {active_profile}\nEndpoint: {endpoint}\nEmail: {email}")


@cli.command(help="Shows statistics by tags")
def stats():
    stats_ = client.stats().items()
    stats_ = sorted(stats_, key=lambda item: item[1], reverse=True)
    if len(stats_) > 0:
        print("[ Your tags statistics ]")
        for item in stats_:
            print(f"  - {colorize_tag(item[0])}: {item[1]}")
        msg = colored(f"\nTotal: {len(stats_)} tags\n", color='grey', attrs=['dark'])
        print(msg)
