import sys
import serial
import serial.tools.list_ports
try:
    import readline
except importError:
    print("readline failed to import")

def getLua():
    script = ""
    with open("./sketch.lua") as d:
        lua = d.readlines()
        for line in lua:
            script += line
    return script

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

cmd = ""

print("//// druid. q to quit.")

while cmd != "q":
  if cmd == "r":
    ser.write(getLua())
  elif cmd == "u":
    ser.write("^^s")
    ser.write(getLua())
    ser.write("^^e")
  elif cmd == "p":
      ser.write("^^p")
  else:
    ser.write(cmd+"\r\n")
  print(ser.read(1000000))
  cmd = raw_input("> ")

ser.close()
exit()
