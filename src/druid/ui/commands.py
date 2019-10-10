from druid.ui.cli import CLICommand
from druid.io.crow.cli import CrowUploadCLI, CrowDownloadCLI


DRUID_COMMANDS = {
    'upload': CrowUploadCLI(),
    'download': CrowDownloadCLI(),
}


