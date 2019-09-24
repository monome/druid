import sys
import serial
import serial.tools.list_ports
try:
    import readline
except:
    print("readline failed to import")
import time
import threading
import Queue

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

druid_help  = "h            this menu\n"
druid_help += "r            runs 'sketch.lua'\n"
druid_help += "u            uploads 'sketch.lua'\n"
druid_help += "r <filename> run <filename>\n"
druid_help += "u <filename> upload <filename>\n"
druid_help += "p            print current userscript\n"
druid_help += "q            quit\n"

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

def process( cmd ):
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
    elif cmd == "h":
        print("\n"+druid_help)
    else:
        ser.write(cmd+"\r\n")

# async reader
def async_in(data, queue):
    for line in iter(data.readline, b''):
        queue.put(line)
    data.close()

############################################
# enter
print("//// druid. q to quit. h for help")

# run script passed from command line
if len(sys.argv) == 2:
    runner( ser.write, sys.argv[1] )

# start async
q = Queue.Queue()
t = threading.Thread(target=async_in, args=(sys.stdin, q))
t.daemon = True #thread dies with program
t.start()

# repl
heard = ""
while heard != "q":
    try: heard = q.get_nowait()
    except Queue.Empty:
        r = ser.read(10000)
        if len(r) > 0:
            print("> "+r)
    else: # got line
        process(heard)
    time.sleep(0.05)

# leave
ser.close()
exit()
