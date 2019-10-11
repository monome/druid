from argparse import FileType
import asyncio
import logging

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    VSplit, HSplit,
    Window, WindowAlign,
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl

from druid.io.crow.device import Crow
from druid.ui.cli import CLICommand
from druid.ui.tty import TextAreaTTY


logger = logging.getLogger(__name__)

# monkey patch to fix https://github.com/monome/druid/issues/8
Char.display_mappings['\t'] = '  '


def run(config, script=None):
    loop = asyncio.get_event_loop()
    with Crow() as crow:
        if script is not None:
            crow.execute(script)

        use_asyncio_event_loop()
        with patch_stdout():
            shell = DruidRepl(crow, config)
            background_task = asyncio.gather(
                *shell.background(),
                return_exceptions=True,
            )
            loop.run_until_complete(shell.foreground())
            background_task.cancel()
            loop.run_until_complete(background_task)

DRUID_INTRO = '//// druid. q to quit. h for help\n\n'
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
        self.layout()
        self.tty = TextAreaTTY(self.output_field)
        self.input_parser = DruidParser(
            self.crow,
            self.tty,
            config,
        )

    def layout(self):
        self.input_field = TextArea(
            height=1, 
            prompt='> ', 
            style='class:input-field',
            multiline=False,
            wrap_lines=False,
        )

        self.input_field.accept_handler = self.accept_input
        self.capture1 = TextArea(style='class:capture-field', height=2)
        self.capture2 = TextArea(style='class:capture-field', height=2)
        self.output_field = TextArea(style='class:output-field', text=DRUID_INTRO)
        captures = VSplit([self.capture1, self.capture2])
        container = HSplit([
            captures, 
            self.output_field,
            Window(
                height=1, 
                char='/', 
                style='class:line',
                content=FormattedTextControl(text='druid////'),
                align=WindowAlign.RIGHT
            ),
            self.input_field
        ])

        kb = KeyBindings()

        @kb.add('c-c', eager=True)
        @kb.add('c-q', eager=True)
        def _(event):
            event.app.exit()

        style = Style([
            ('capture-field', '#747369'),
            ('output-field', '#d3d0c8'),
            ('input-field', '#f2f0ec'),
            ('line', '#747369'),
        ])

        self.application = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )

    def background(self):
        return []

    def foreground(self):
        return self.application.run_async()

    def accept_input(self, buf):
        text = self.input_field.text
        self.tty.show('\n> {}\n'.format(text))
        try:
            self.input_parser.parse(text)
        except ExitDruid:
            print('bye.')
            get_app().exit()
        except Exception as e:
            logger.error(
                'error processing input',
                text,
                e,
            )

class DruidParser:

    def __init__(self, crow, tty, config):
        self.crow = crow
        self.tty = tty
        try:
            self.default_script = config['scripts']['default']
        except KeyError:
            self.default_script = "./sketch.lua"

    def parse(self, s):
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
            self.crow.cmd(self.tty, "^^p")
            return
        elif c == "h":
            self.tty.show(DRUID_HELP)
            return
        
        self.crow.write(s + "\r\n")


class ExitDruid(Exception):
    pass
