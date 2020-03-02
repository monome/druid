""" Druid REPL """
# pylint: disable=C0103
import asyncio
import logging.config
import os
import sys

from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    VSplit, HSplit,
    Window, WindowAlign,
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl

# from druid import crowlib
from druid.crow import Crow


# monkey patch to fix https://github.com/monome/druid/issues/8
Char.display_mappings['\t'] = '  '

druid_intro = "//// druid. q to quit. h for help\n\n"
druid_help = """
 h            this menu
 r            runs 'sketch.lua'
 u            uploads 'sketch.lua'
 r <filename> run <filename>
 u <filename> upload <filename>
 p            print current userscript
 q            quit

"""


class Druid:
    def __init__(self, crow):
        self.crow = crow
        self.set_state('repl')
        self.output_field = TextArea(style='class:output-field', text=druid_intro)

    async def foreground(self, script=None):
        if script is not None:
            if self.crow.is_connected == False:
                print('no crow device found. exiting.')
                return
            self.crow.execute(script)

        self.app = self.fullscreen()
        return await self.app.run_async()

    async def background(self):
        await self.crow.read_forever()

    def set_state(self, state):
        if state == 'repl':
            on_disconnect = lambda exc: self.output(' <crow disconnected>\n')
            self.crow.replace_handlers({
                'connect': [lambda: self.output(' <crow connected>\n')],
                'connect_err': [on_disconnect],
                'disconnect': [on_disconnect],

                'running': [lambda fname: self.output(f'running {fname}\n')],
                'uploading': [lambda fname: self.output(f'uploading {fname}\n')],

                'crow_event': [],
                'crow_output': [lambda output: self.output(output + '\n')],
            })
        else:
            return
        self.state = state

    def output(self, st):
        self.output_to_field(self.output_field, st)

    def output_to_field(self, field, st):
        s = field.text + st.replace('\r', '')
        field.buffer.document = Document(text=s, cursor_position=len(s))

    def accept(self, buff):
        self.output(f'\n> {self.input_field.text}\n')
        self.parse(self.input_field.text)

    def parse(self, cmd):
        parts = cmd.split(maxsplit=1)
        if len(parts) == 0:
            return
        c = parts[0]
        if c == 'r' or c == 'u':
            run_func = self.crow.upload if c == 'u' else self.crow.execute
            if len(parts) == 1:
                run_func('./sketch.lua')
            elif len(parts) == 2 and os.path.isfile(parts[1]):
                run_func(parts[1])
            else:
                self.crow.writeline(cmd)
        elif len(parts) == 1:
            if c == 'q':
                print('bye.')
                self.app.exit()
            elif c == 'p':
                self.crow.write('^^p')
            elif c == 'h':
                self.output(druid_help)
            else:
                self.crow.writeline(cmd)
        else:
            self.crow.writeline(cmd)

    def fullscreen(self):
        self.statusbar = Window(
            height=1,
            char='/',
            style='class:line',
            content=FormattedTextControl(text='druid////'),
            align=WindowAlign.RIGHT
        )
        self.input_field = TextArea(
            height=1,
            prompt='> ',
            multiline=False,
            wrap_lines=False,
            style='class:input-field'
        )
        self.input_field.accept_handler = self.accept
        self.container = HSplit([
            self.output_field,
            self.statusbar,
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

        return Application(
            layout=Layout(self.container, focused_element=self.input_field),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )


def main(script=None):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)-15s %(levelname)-8s'
                          '%(processName)-10s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'druid.log',
                'mode': 'w',
                'formatter': 'detailed',
            },
        },
        'loggers': {
            'druid.crow': {
                'handlers': ['file'],
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': [],
        },
    })

    loop = asyncio.get_event_loop()
    use_asyncio_event_loop()
    with patch_stdout():
        with Crow() as crow:
            shell = Druid(crow)
            crow.reconnect(errmsg='crow disconnected')
            background_task = asyncio.gather(
                shell.background(),
                return_exceptions=True,
            )
            loop.run_until_complete(shell.foreground())
            background_task.cancel()
