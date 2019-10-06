import serial
import serial.tools.list_ports
import time

def connect():
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

def reconnect():
    try:
        c = crow_connect()
        myprint( " <online!>" )
        return c
    except ValueError as err:
        myprint( " <lost connection>" )

def writelines( writer, file ):
    with open(file) as d:
        lua = d.readlines()
        for line in lua:
            writer( line.encode() ) # convert text to bytes
            time.sleep(0.001) # fix os x crash?

def upload( writer, printer, file ):
    printer(" uploading "+file+"\n\r")
    writer(bytes("^^k", 'utf-8'))
    time.sleep(0.4) # wait for restart
    writer(bytes("^^s", 'utf-8'))
    time.sleep(0.2) # wait for allocation
    writelines( writer, file )
    time.sleep(0.2) # wait for upload to complete
    writer(bytes("^^e", 'utf-8'))
    time.sleep(0.2) # wait for flash write
    writer(bytes("init()\n\r", 'utf-8'))

def execute( writer, printer, file ):
    printer(" running "+file+"\n\r")
    writer(bytes("```", 'utf-8'))
    writelines( writer, file )
    time.sleep(0.1)
    writer(bytes("```", 'utf-8'))
    time.sleep(0.1)
    writer(bytes("init()\n\r", 'utf-8'))
