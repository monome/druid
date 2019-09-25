from __future__ import unicode_literals

import sys
import serial
import serial.tools.list_ports
import time
import threading
import queue
import asyncio

from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl


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

def crow_connect():
    port = ""
    for item in serial.tools.list_ports.comports():
        if "USB VID:PID=0483:5740" in item[2]:
            port = item[0]
    if port == "":
        raise ValueError("can't find crow device")
    try:
        return serial.Serial(port,115200, timeout=0.1)
    except:
        raise ValueError("can't open serial port")

def forLuaLines( fn, file ):
    with open(file) as d:
        lua = d.readlines()
        for line in lua:
            fn( line.encode() ) # convert text to bytes

def uploader( fn, file ):
    myprint(" uploading "+file)
    fn(bytes("^^k", 'utf-8'))
    time.sleep(0.4) # wait for restart
    fn(bytes("^^s", 'utf-8'))
    time.sleep(0.2) # wait for allocation
    forLuaLines( fn, file )
    time.sleep(0.2) # wait for upload to complete
    fn(bytes("^^e", 'utf-8'))

def runner( fn, file ):
    myprint(" running "+file+"\r")
    fn(bytes("```", 'utf-8'))
    forLuaLines( fn, file )
    time.sleep(0.1)
    fn(bytes("```", 'utf-8'))

def parser( cmd ):
    global ser
    if cmd == "q":
        raise ValueError("bye.")
    elif "r " in cmd:
        runner( ser.write, cmd[2:] )
    elif cmd == "r":
        runner( ser.write, "./sketch.lua" )
    elif "u " in cmd:
        uploader( ser.write, cmd[2:] )
    elif cmd == "u":
        uploader( ser.write, "./sketch.lua" )
    elif cmd == "p":
        ser.write(bytes("^^p", 'utf-8'))
    elif cmd == "h":
        myprint(druid_help)
    else:
        ser.write(bytes(cmd + "\r\n", 'utf-8'))

output_field = TextArea( style='class:output-field'
                       , text=druid_intro
                       )
input_field = TextArea( height=1
                      , prompt='> '
                      , style='class:input-field'
                      , multiline=False
                      , wrap_lines=False
                      )

async def shell():
    container = HSplit([ output_field
                       , Window( height=1
                               , char='/'
                               , style='class:line'
                               , content=FormattedTextControl( text='druid////' )
                               , align=WindowAlign.RIGHT
                               )
                       , input_field
                       ])

    def accept(buff):
        try:
            parser(input_field.text)
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
        ('output-field', 'bg:#000000 #cccccc'),
        ('input-field', 'bg:#000000 #ffffff'),
        ('line',        '#443388'),
    ])

    application = Application(
        layout=Layout(container, focused_element=input_field),
        key_bindings=kb,
        style=style,
        mouse_support=True,
        full_screen=True,
    )
    result = await application.run_async()

def myprint(st):
    s = output_field.text + st.replace('\r','')
    output_field.buffer.document = Document( text=s
                                           , cursor_position=len(s)
                                           )

async def printer():
    global ser
    while True:
        r = ser.read(10000)
        if len(r) > 0:
            myprint( r.decode('ascii') )
        await asyncio.sleep(0.001) # TODO set serial read rate!

def main():
    loop = asyncio.get_event_loop()

    global ser
    try:
        ser = crow_connect()
    except ValueError as err:
        print(err)
        exit()

    # run script passed from command line
    if len(sys.argv) == 2:
        runner( ser.write, sys.argv[1] )

    use_asyncio_event_loop()

    with patch_stdout():
        background_task = asyncio.gather(printer(), return_exceptions=True)
        loop.run_until_complete(shell())
        background_task.cancel()
        loop.run_until_complete(background_task)

    ser.close()
    exit()

main()
