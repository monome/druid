import sys
import serial
import readline

def getLua():
    script = ""
    with open("./sketch.lua") as d:
        lua = d.readlines()
        for line in lua:
            script += line
    return script

try:
  ser = serial.Serial("/dev/ttyACM0",115200, timeout=0.1)
except:
  print("serial problem with /dev/ttyACM0")
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

