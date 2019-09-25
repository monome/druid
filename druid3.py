from __future__ import unicode_literals

import sys
import serial
import serial.tools.list_ports
import asyncio

from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, WindowAlign
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

def druidparser( writer, cmd ):
    if cmd == "q":
        raise ValueError("bye.")
    elif "r " in cmd:
        runner( writer, cmd[2:] )
    elif cmd == "r":
        runner( writer, "./sketch.lua" )
    elif "u " in cmd:
        uploader( writer, cmd[2:] )
    elif cmd == "u":
        uploader( writer, "./sketch.lua" )
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
            else:
                myprint(cmd+'\n')
    else:
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
        ('capture-field', 'bg:#000000 #747369'),
        ('output-field', 'bg:#000000 #d3d0c8'),
        ('input-field', 'bg:#000000 #f2f0ec'),
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
        crow = crow_connect()
        crowparser( " <online!>" )
    except ValueError as err:
        crowparser( " <lost connection>" )

async def printer():
    global crow
    while True:
        sleeptime = 0.001
        try:
            r = crow.read(10000)
            if len(r) > 0:
                lines = r.decode('ascii').split()
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
        crow = crow_connect()
    except ValueError as err:
        print(err)
        exit()

    # run script passed from command line
    if len(sys.argv) == 2:
        runner( crow.write, sys.argv[1] )

    use_asyncio_event_loop()

    with patch_stdout():
        background_task = asyncio.gather(printer(), return_exceptions=True)
        loop.run_until_complete(shell())
        background_task.cancel()
        loop.run_until_complete(background_task)

    crow.close()
    exit()

main()
