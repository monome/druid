from prompt_toolkit.application import Application
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

from druid.config import DruidConfigError
from druid.ui.tty import FuncTTY, TextAreaTTY


# monkey patch to fix https://github.com/monome/druid/issues/8
Char.display_mappings['\t'] = '  '


DRUID_INTRO = '//// druid. q to quit. h for help\n\n'

class DruidReplLayout:
    def __init__(self, config, accept_handler):
        self.input_field = TextArea(
            height=1, 
            prompt='> ', 
            style='class:input-field',
            multiline=False,
            wrap_lines=False,
        )

        self.input_field.accept_handler = accept_handler

        self.captures = [
            TextArea(style='class:capture-field', height=2)
            for _ in config['captures']
        ]
        self.capture_handlers = self.build_capture_handlers(
            zip(self.captures, config['captures']),
        )
        self.output_field = TextArea(style='class:output-field', text=DRUID_INTRO)
        captures = VSplit(self.captures)
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

        style = Style(list(config['style'].items()))

        self.application = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )

    def test_format(self, fmt):
        try:
            self.capture_format_handler(FuncTTY(lambda s: None), fmt)(
                'event(1, 2)',
                'event',
                ['1', '2'],
            )
        except:
            raise DruidConfigError(
                'error evaluating format string: {}'.format(fmt)
            )

    def build_capture_handlers(self, config):
        events = {
            'change': [
                self.default_handler,
                self.default_handler,
            ],
            'stream': [
                self.default_handler,
                self.default_handler,
            ],
            'ii': {},
        }
        for capture, cfg in config:
            for key, fmt in cfg.items():
                if key in events:
                    tty = TextAreaTTY(capture)
                    if isinstance(events[key], list):
                        self.bind_input_captures(key, events[key], cfg, tty)
                    else:
                        events[key] = self.bind_nested_captures(
                            events, 
                            cfg[key], 
                            tty,
                            [key],
                        )
        return events


    def bind_input_captures(self, key, events, cfg, tty):
        if 'on_inputs' in cfg:
            for on_input in cfg['on_inputs']:
                if 1 <= on_input <= 2:
                    fmt = cfg[key]
                    self.test_format(fmt)
                    handler = self.capture_format_handler(tty, fmt)
                    events[on_input - 1] = handler
                else:
                    raise DruidConfigError(
                        "'on_inputs' setting {} is out of bounds".format(on_input)
                    )
        else:
            raise DruidConfigError(
                "'on_input' required for 'stream' and 'change' events"
            )

    def default_handler(self, line, evt, args):
        print('default handler:', line)
        return ''

    def capture_format_handler(self, tty, fmt):
        def _handler(line, evt, args):
            tty.show('\n' + fmt.format(
                line=line.strip().strip('^^'),
                event=evt,
                args=args,
            ) + '\n')
        return _handler

    def bind_nested_captures(self, events, cfg, tty, breadcrumb):
        if isinstance(cfg, str):
            self.test_format(cfg)
            return self.capture_format_handler(tty, cfg)
        elif isinstance(cfg, dict):
            return {
                self.bind_nested_captures(
                    events[k],
                    sub, 
                    tty, 
                    [*breadcrumb, k],
                )
                for k, sub in cfg.items()
            }
        else:
            raise DruidConfigError(
                "expected string or dict for capture '{}'".format(
                    '.'.join(breadcrumb),
                ),
            )
