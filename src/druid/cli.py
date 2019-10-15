""" Command-line interface for druid """

import logging
import logging.config
import os
import sys
import time

import click

from druid.config import DruidConfig
from druid.io.crow.device import Crow
from druid.io.device import DeviceNotFoundError
from druid.ui.repl import core as druid_repl
from druid.ui.tty import FuncTTY


logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):
    """ Terminal interface for crow """
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)

@cli.command(short_help="Download a file from crow")
def download():
    """
    Download a file from crow and print it to stdout
    """
    crow = Crow()
    try:
        crow.connect()
    except DeviceNotFoundError as err:
        click.echo(err)
        sys.exit(1)

    crow.write("^^p", "utf-8")
    click.echo(crow.read(1000000).decode())
    crow.close()

@cli.command(short_help="Upload a file to crow")
@click.argument("filename", type=click.Path(exists=True))
def upload(filename):
    """
    Upload a file to crow.
    FILENAME is the path to the Lua file to upload
    """
    crow = Crow()
    tty = FuncTTY(click.echo)
    try:
        crow.connect()
    except DeviceNotFoundError as err:
        click.echo(err)
        sys.exit(1)

    crow.upload(tty, filename)
    time.sleep(0.5)
    click.echo('\n')
    click.echo(crow.dump())

@cli.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
def repl(filename):
    """ Start interactive terminal """

    config = DruidConfig([
        os.path.expanduser("~/druid.yml"),
        os.path.expanduser("~/.druid.yml"),
        os.path.realpath("druid.yml"),
        os.path.realpath(".druid.yml"),
    ])
    os.makedirs('./logs', exist_ok=True)
    logging.config.dictConfig(config['logging'])

    druid_repl.main(config, script=filename)
