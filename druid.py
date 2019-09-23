import sys
import serial
import serial.tools.list_ports
try:
    import readline
except:
    print("readline failed to import")
import time

port = ""
for item in serial.tools.list_ports.comports():
    if "USB VID:PID=0483:5740" in item[2]:
        port = item[0]

if port == "":
    print("can't find crow device")
    exit()

try:
  ser = serial.Serial(port,115200, timeout=0.1)
except:
  print("can't open serial port")
  exit()

def forLuaLines( fn, file ):
    with open(file) as d:
        lua = d.readlines()
        for line in lua:
            fn( line )

def uploader( fn, file ):
    print(" uploading "+file)
    fn("^^k")
    time.sleep(0.4) # wait for restart
    fn("^^s")
    time.sleep(0.2) # wait for allocation
    forLuaLines( fn, file )
    time.sleep(0.2) # wait for upload to complete
    fn("^^e")

def runner( fn, file ):
    print(" running "+file)
    fn("```")
    forLuaLines( fn, file )
    time.sleep(0.1)
    fn("```")

# enter
print("//// druid. q to quit.")

# run script passed from command line
if len(sys.argv) == 2:
    runner( ser.write, sys.argv[1] )

# repl
cmd = ""
while cmd != "q":
    if "r " in cmd:
        runner( ser.write, cmd[2:] )
    elif cmd == "r":
        runner( ser.write, "./sketch.lua" )
    elif "u " in cmd:
        uploader( ser.write, cmd[2:] )
    elif cmd == "u":
        uploader( ser.write, "./sketch.lua" )
    elif cmd == "p":
        ser.write("^^p")
    elif cmd == "help":
        print(druid_help)
    else:
        ser.write(cmd+"\r\n")
    print(ser.read(1000000))
    cmd = raw_input("> ")

# leave
ser.close()
exit()
