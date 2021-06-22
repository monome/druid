""" Command-line interface for druid """

import sys
import time

import click

import requests
import os
from packaging import version

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

@cli.command(short_help="Update crow firmware")
def firmware():
    """ Update crow firmware
    """
    print("Checking for updates...")
    git_query = requests.get('https://raw.githubusercontent.com/monome/crow/main/version.txt')
    git_data = git_query.text.split()
    print(">> git version", git_data[0])

    with Crow() as crow:
      local_version = "none"
      try:
        crow.connect()
      except:
        print("No crow found, or might be in bootloader mode already...")
        local_version = "0"

      # crow found: clear script and read version
      if local_version != "0":
        crow.write("crow.reset()")
        time.sleep(0.1)
        c = crow.read(1000000)
        crow.write("^^v")
        tmp = (crow.read(100)).split("'")
        local_version = tmp[1][1:]

      print(">> local version: ", local_version)

      if version.parse(local_version) >= version.parse(git_data[0]):
        print("Up to date.")
        exit()

      # delete old crow.dfu if exists
      if os.path.exists("crow.dfu"):
        os.remove("crow.dfu")

      print("Downloading new version:", git_data[1])
      res = requests.get(git_data[1])
      with open('crow.dfu', 'wb') as fwfile:
        fwfile.write(res.content)

      if local_version != "0":
        crow.write('^^b')
        time.sleep(1.0)
        print("Crow bootloader enabled.")

      try:
        pydfu.init()
      except ValueError:
        print("Error: pydfu didn't find crow!")
        exit()

      elements = pydfu.read_dfu_file("crow.dfu")
      if not elements:
          return
      print("Writing memory...")
      pydfu.write_elements(elements, False, progress=pydfu.cli_progress)

      print("Exiting DFU...")
      pydfu.exit_dfu()

      os.remove("crow.dfu")
      print("Update complete.")


@cli.command(short_help="Clear userscript")
def clearscript():
    """ Clear userscript from crow' flash memory """
    try:
        pydfu.init()
    except ValueError:
        print("Error: pydfu didn't find crow! Check you've forced the bootloader.")
        exit()
    print("Clearing userscript...")
    # note we must write a single byte of 0x00 but are primarily just triggering erase of the flash page
    pydfu.write_elements([{"addr":0x08010000, "size": 1, "data": [0]}], False)
    print("Complete. Exiting DFU...")
    pydfu.exit_dfu()


@cli.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
@click.option("--theme/--no-theme", default=True, show_default=True,
              help="Whether to use the internal color theme.")
def repl(filename, theme):
    """ Start interactive terminal """
    druid_repl.main(filename, theme)
