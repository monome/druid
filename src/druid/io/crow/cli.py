from argparse import FileType

from druid.io.crow.device import Crow
from druid.ui.cli import CLICommand


class CrowUploadCLI(CLICommand):
    '''
    upload a script to crow
    '''

    def register(self, parser):
        super().register(parser)
        parser.add_argument(
            'script',
            help='script file',
            type=FileType,
        )

    def __call__(self, args, config):
        with Crow() as crow:
            crow.upload(args.script)
            time.sleep(0.5)  # wait for new script to be ready
            print(crow.cmd('^^p'))


class CrowDownloadCLI(CLICommand):
    '''
    download the script stored on crow
    '''

    def __call__(self, args, config):
        with Crow() as crow:
            print(crow.cmd('^^p'))
