import logging
import time

import serial
import serial.tools.list_ports


logger = logging.getLogger(__name__)

def connect():
    port = ""
    for item in serial.tools.list_ports.comports():
        logger.info("comport {} - device {}".format(item[0], item[2]))
        if "USB VID:PID=0483:5740" in item[2]:
            port = item[0]
            logger.info('using {}'.format(port))
    if port == "":
        logger.error("crow not found, exit")
        raise ValueError("can't find crow device")
    try:
        return serial.Serial(port, 115200, timeout=0.1)
    except serial.SerialException as e:
        logger.error("could not open comport {}".format(port), e)
        raise ValueError("can't open serial port")

def reconnect():
    try:
        c = crow_connect()
        myprint(" <online!>")
        return c
    except ValueError as err:
        myprint(" <lost connection>")

def writelines(writer, file):
    with open(file) as d:
        lua = d.readlines()
        for line in lua:
            writer(line.encode())  # convert text to bytes
            time.sleep(0.002)  # fix os x crash?

def upload(writer, printer, file):
    printer(" uploading "+file+"\n\r")
    writer(bytes("^^s", 'utf-8'))
    time.sleep(0.2)  # wait for allocation
    writelines(writer, file)
    time.sleep(0.1)  # wait for upload to complete
    writer(bytes("^^w", 'utf-8'))

def execute(writer, printer, file):
    printer(" running "+file+"\n\r")
    writer(bytes("^^s", 'utf-8'))
    time.sleep(0.2)  # wait for allocation
    writelines(writer, file)
    time.sleep(0.01)
    writer(bytes("^^e", 'utf-8'))

# leaving this here for 'run a code chunk'
#def execute( writer, printer, file ):
#    printer(" running "+file+"\n\r")
#    writer(bytes("```", 'utf-8'))
#    writelines( writer, file )
#    time.sleep(0.1)
#    writer(bytes("```", 'utf-8'))
#    time.sleep(0.1)
#    writer(bytes("init()\n\r", 'utf-8'))
