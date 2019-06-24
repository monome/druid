import sys
import serial
import time

try:
  ser = serial.Serial("/dev/ttyACM0",115200, timeout=0.1)
except:
  print("serial problem with /dev/ttyACM0")
  exit()

ser.write("^^p")

print(ser.read(1000000))
