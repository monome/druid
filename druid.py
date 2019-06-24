import sys
import serial
import readline

try:
  ser = serial.Serial("/dev/ttyACM0",115200, timeout=0.1)
except:
  print("serial problem with /dev/ttyACM0")
  exit()

cmd = ""

while cmd != "q":
  cmd = raw_input("> ")
  ser.write(cmd+"\r\n")
  print(ser.read(1000000))
