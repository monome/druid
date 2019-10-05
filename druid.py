#!/usr/bin/env python3

from __future__ import unicode_literals

import sys
import asyncio
import crowlib

from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, WindowAlign
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl

# monkey patch to fix https://github.com/monome/druid/issues/8
Char.display_mappings['\t'] = '  '

druid_intro = "//// druid. q to quit. h for help\n\n"
druid_help  = """
 h            this menu
 r            runs 'sketch.lua'
 u            uploads 'sketch.lua'
 r <filename> run <filename>
 u <filename> upload <filename>
 p            print current userscript
 q            quit

"""

def druidparser( writer, cmd ):
    if cmd == "q":
        raise ValueError("bye.")
    elif "r " in cmd:
        crowlib.execute( writer, myprint, cmd[2:] )
    elif cmd == "r":
        crowlib.execute( writer, myprint, "./sketch.lua" )
    elif "u " in cmd:
        crowlib.upload( writer, myprint, cmd[2:] )
    elif cmd == "u":
        crowlib.upload( writer, myprint, "./sketch.lua" )
    elif cmd == "p":
        writer(bytes("^^p", 'utf-8'))
    elif cmd == "h":
        myprint(druid_help)
    else:
        writer(bytes(cmd + "\r\n", 'utf-8'))

def crowparser( text ):
    if "^^" in text:
        cmds = text.split('^^')
        for cmd in cmds:
            t3 = cmd.rstrip().partition('(')
            x = t3[0]
            args = t3[2].rstrip(')').partition(',')
            if x == "stream" or x == "change":
                dest = capture1
                if args[0] == "2":
                    dest = capture2
                _print( dest, ('\ninput['+args[0]+'] = '+args[2]+'\n'))
            elif len(cmd) > 0:
                myprint(cmd+'\n')
    elif len(text) > 0:
        myprint(text+'\n')

capture1 = TextArea( style='class:capture-field'
                   , height=2
                   )
capture2 = TextArea( style='class:capture-field'
                   , height=2
                   )
output_field = TextArea( style='class:output-field'
                       , text=druid_intro
                       )
async def shell():
    global crow
    input_field = TextArea( height=1
                          , prompt='> '
                          , style='class:input-field'
                          , multiline=False
                          , wrap_lines=False
                          )

    captures = VSplit([ capture1, capture2 ])
    container = HSplit([ captures
                       , output_field
                       , Window( height=1
                               , char='/'
                               , style='class:line'
                               , content=FormattedTextControl( text='druid////' )
                               , align=WindowAlign.RIGHT
                               )
                       , input_field
                       ])

    def cwrite(xs):
        global crow
        try:
            crow.write(xs)
        except:
            crowreconnect()

    def accept(buff):
        try:
            myprint( '\n> '+input_field.text+'\n' )
            druidparser( cwrite, input_field.text )
        except ValueError as err:
            print(err)
            get_app().exit()

    input_field.accept_handler = accept

    kb = KeyBindings()
    @kb.add('c-c', eager=True)
    @kb.add('c-q', eager=True)
    def _(event):
        event.app.exit()

    style = Style([
        ('capture-field', '#747369'),
        ('output-field', '#d3d0c8'),
        ('input-field', '#f2f0ec'),
        ('line',        '#747369'),
    ])

    application = Application(
        layout=Layout(container, focused_element=input_field),
        key_bindings=kb,
        style=style,
        mouse_support=True,
        full_screen=True,
    )
    result = await application.run_async()

def _print(field, st):
    s = field.text + st.replace('\r','')
    field.buffer.document = Document( text=s
                                    , cursor_position=len(s)
                                    )

def myprint(st):
    _print( output_field, st )

def crowreconnect():
    global crow
    try:
        crow = crowlib.connect()
        myprint( " <online!>\n" )
    except ValueError as err:
        myprint( " <lost connection>\n" )

async def printer():
    global crow
    while True:
        sleeptime = 0.001
        try:
            r = crow.read(10000)
            if len(r) > 0:
                lines = r.decode('ascii').split('\n\r')
                for line in lines:
                    crowparser( line )
        except:
            sleeptime = 1.0
            crowreconnect()
        await asyncio.sleep(sleeptime)

def main():
    global crow
    loop = asyncio.get_event_loop()

    try:
        crow = crowlib.connect()
    except ValueError as err:
        print(err)
        exit()

    # run script passed from command line
    if len(sys.argv) == 2:
        crowlib.execute( crow.write, myprint, sys.argv[1] )

    use_asyncio_event_loop()

    with patch_stdout():
        background_task = asyncio.gather(printer(), return_exceptions=True)
        loop.run_until_complete(shell())
        background_task.cancel()
        loop.run_until_complete(background_task)

    crow.close()
    exit()

if __name__ == '__main__':
  main()
