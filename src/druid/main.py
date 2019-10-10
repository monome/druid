import argparse
import logging.config
import os

import anyconfig

from druid.cli.arguments import DirectoryArgumentAction
from druid.config import DruidConfig
from druid.ui import commands
from druid.ui.shell import DruidShellCLI
from druid.version import __version__


def main():
    parser = argparse.ArgumentParser()
    cli = DruidShellCLI()
    cli.register(parser)
    parser.set_defaults(func=cli)
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='monome druid v{}'.format(__version__),
    )        
    parser.add_argument(
        '--config_dir',
        action=DirectoryArgumentAction,
        default='.',
        help='Directory to load additional configuration from',
    )
    parser.add_argument(
        '--config_files',
        nargs="*",
        default=[],
        help='Additional config files to load',
    )

    subparsers = parser.add_subparsers()
    for name, command in commands.DRUID_COMMANDS.items():
        subparser = subparsers.add_parser(name, help=command.help())
        command.register(subparser)

    args = parser.parse_args()
    config = DruidConfig(
        os.path.join(args.config_dir, x)
        for x in [
            os.path.join(os.path.expanduser('~/.druid.yml')),
            'druid.yml',
            *args.config_files,
        ]        
    )

    logging.config.dictConfig(config['logging'])
    args.func(args, config)


if __name__ == '__main__':
    main()
