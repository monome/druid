""" Command-line interface for druid """

import sys
import time

import click

from druid import __version__, crowlib
from druid import repl as druid_repl

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__)
def cli(ctx):
    """ Terminal interface for crow """
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)

@cli.command(short_help="Download a file from crow")
def download():
    """
    Download a file from crow and print it to stdout
    """
    try:
        crow = crowlib.connect()
    except ValueError as err:
        click.echo(err)
        sys.exit(1)

    crow.write(bytes("^^p", "utf-8"))
    time.sleep(0.3) # wait for print to complete
    click.echo(crow.read(1000000).decode())
    crow.close()

def myprint(string):
    click.echo(string)

@cli.command(short_help="Upload a file to crow")
@click.argument("filename", type=click.Path(exists=True))
def upload(filename):
    """
    Upload a file to crow.
    FILENAME is the path to the Lua file to upload
    """
    try:
        crow = crowlib.connect()
    except ValueError as err:
        click.echo(err)
        sys.exit(1)

    crowlib.upload(crow.write, myprint, filename)
    click.echo(crow.read(1000000).decode()) # receive errors
    time.sleep(0.3) # wait for new script to be ready
    crow.write(bytes("^^p", "utf-8"))
    time.sleep(0.3) # wait for print to complete
    click.echo(crow.read(1000000).decode())
    crow.close()

@cli.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
def repl(filename):
    """ Start interactive terminal """
    druid_repl.main(filename)
