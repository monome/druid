""" Command-line interface for druid """

import sys
import time

import click

import requests

from druid import __version__
from druid.crow import Crow
from druid import repl as druid_repl
from druid import pydfu

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
    with Crow() as crow:
        crow.connect()
        crow.write('^^p')
        time.sleep(0.3)
        click.echo(crow.read(1000000))

@cli.command(short_help="Upload a file to crow")
@click.argument("filename", type=click.Path(exists=True))
def upload(filename):
    """
    Upload a file to crow.
    FILENAME is the path to the Lua file to upload
    """
    with Crow() as crow:
        crow.connect()
        crow.upload(filename)
        click.echo(crow.read(1000000))
        time.sleep(0.3)
        crow.write('^^p')
        time.sleep(0.3)
        click.echo(crow.read(1000000))

@cli.command(short_help="Update bootloader")
def update():
    """ Update bootloader
    """
    print("update")
    v = requests.get('https://raw.githubusercontent.com/monome/crow/main/version.txt')
    r = v.text.split()
    print("version", r[0])
    print(r[1])

    """
    with Crow() as crow:
      crow.connect()
      # get version
      # compare to remote version (quit if up to date)
      # download file
      # unpack file
      # flash file (below)
      crow.write('^^b')
      time.sleep(1.0)
      print("crow bootloader enabled")
      try:
        pydfu.init()
      except ValueError:
        print("pydfu didn't find crow")
        exit()
      print("Writing binary...")
      pydfu.write_bin("crow.bin", progress=pydfu.cli_progress)
      print("Exiting DFU...")
      pydfu.exit_dfu()
    """


@cli.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
def repl(filename):
    """ Start interactive terminal """
    druid_repl.main(filename)
