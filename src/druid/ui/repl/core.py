from argparse import FileType
import asyncio
import logging
import os
import sys
import traceback

from prompt_toolkit.application.current import get_app
from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout

from druid.config import DruidConfigError
from druid.io.crow.device import Crow, CrowAsync, CrowParser
from druid.io.device import DeviceNotFoundError
from druid.ui.repl.layout import DruidReplLayout
from druid.ui.tty import TextAreaTTY


logger = logging.getLogger(__name__)


def run(config, script=None):
    loop = asyncio.get_event_loop()
    crow = CrowAsync()
    try:
        crow.find_device()
    except DeviceNotFoundError as exc:
        print(str(exc))
        sys.exit(1)
    else:
        if script is not None:
            crow.execute(script)

        use_asyncio_event_loop()
        with patch_stdout():
            shell = DruidRepl(crow, config)
            try:
                background_task = asyncio.gather(
                    *shell.background(),
                    return_exceptions=True,
                )
                loop.run_until_complete(shell.foreground())
            finally:
                background_task.cancel()
                loop.run_until_complete(background_task)

DRUID_HELP = '''
 h            this menu
 r            runs 'sketch.lua'
 u            uploads 'sketch.lua'
 r <filename> run <filename>
 u <filename> upload <filename>
 p            print current userscript
 q            quit

'''

class DruidRepl:

    def __init__(self, crow, config):
        self.crow = crow
        self.layout = DruidReplLayout(
            config['ui'],
            self.accept_input,
        )
        self.tty = TextAreaTTY(self.layout.output_field)
        self.input_parser = DruidParser(
            self.crow,
            self.tty,
            config,
        )
        self.crow_parser = CrowParser(
            self.tty,
            event_handlers=self.layout.capture_handlers,
        )
        self.crow.attach(self.tty)
            
    def background(self):
        yield self.crow.listen(self.crow_parser)
        # yield self.process_crow_output()

    def foreground(self):
        return self.layout.application.run_async()

    def accept_input(self, buf): 
        text = self.layout.input_field.text

        self.tty.show('\n> {}\n'.format(text))
        try:
            self.input_parser.parse(text)
        except ExitDruid:
            print('bye.')
            get_app().exit()
        except Exception as e:
            logger.error(
                'error processing input: {}\n{}'.format(
                    text,
                    traceback.format_exc(),
                )
            )

    def on_connect(self):
        self.tty.show(' <connected!>')


class DruidParser:

    def __init__(self, crow, tty, config):
        self.crow = crow
        self.tty = tty
        try:
            self.default_script = config['scripts']['default']
        except KeyError:
            self.default_script = "./sketch.lua"

    def parse(self, s):
        logger.debug('user input: {}'.format(s))

        parts = s.split(maxsplit=1)
        if len(parts) == 0:
            return
        c = parts[0]
        if c == "q":
            raise ExitDruid
        elif c == "r":
            if len(parts) == 1:
                self.crow.execute(self.tty, self.default_script)
                return
            elif len(parts) == 2 and os.path.isfile(parts[1]):
                self.crow.execute(self.tty, parts[1])
                return
        elif c == "u":
            if len(parts) == 1:
                self.crow.upload(self.tty, self.default_script)
                return
            elif len(parts) == 2 and os.path.isfile(parts[1]):
                self.crow.upload(self.tty, parts[1])
                return
        elif c == "p":
            self.crow.writeline("^^p")
            return
        elif c == "h":
            self.tty.show(DRUID_HELP)
            return
        
        self.crow.write(s + "\r\n")


class ExitDruid(Exception):
    pass
