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


logger = logging.getLogger(__name__)

# monkey patch to fix https://github.com/monome/druid/issues/8
Char.display_mappings['\t'] = '  '


class DruidShellCLI(CLICommand):
    '''
    druid <-> crow interactive shell
    '''

    def register(self, parser):
        parser.add_argument(
            'script',
            nargs='?',
            type=FileType,
            help='script to execute before starting shell',
        )

    def __call__(self, args, config):
        loop = asyncio.get_event_loop()
        with Crow() as crow:
            if args.script is not None:
                crow.execute(args.script)

            use_asyncio_event_loop()
            with patch_stdout():
                shell = DruidShell(crow, DruidParser(config))
                background_task = asyncio.gather(
                    *shell.background(),
                    return_exceptions=True,
                )
                loop.run_until_complete(shell.foreground())
                background_task.cancel()
                loop.run_until_complete(background_task)

class DruidShell:
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

    def __init__(self, crow, input_parser):
        self.crow = crow
        self.input_parser = input_parser
        self.layout()

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
        self.output_field = TextArea(style='class:output-field', text=self.DRUID_INTRO)
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
        self.show(self.output_field, '\n> {}\n'.format(text))
        try:
            self.input_parser.parse(text)
        except DruidShellError as e:
            logger.error(
                'error processing input',
                text,
                e,
            )
            self.app.exit()

    def show(self, field, st):
        s = field.text + st.replace('\r', '')
        field.buffer.document = Document(text=s, cursor_position=len(s))


class DruidParser:
    def __init__(self, crow):
        self.crow = crow

    def parse(self, s):
        pass


class DruidParseError(Exception):
    pass
