import sys
import serial
import time

try:
  ser = serial.Serial("/dev/ttyACM0",115200, timeout=1)
except:
  print("serial problem with /dev/ttyACM0")
  exit()

if len(sys.argv) < 2:
  print("usage: python upload.py file-to-upload.lua")
  exit()

try:
  f = open(sys.argv[1],"r")
except:
  print("file problem")
  exit()

print("upload start.")

ser.write("^^c")
ser.write("^^s")

for line in f:
  ser.write(line+"\n")

ser.write("^^e")

print(ser.read(10000))

print("file uploaded:")

ser.write("^^p")

print(ser.read(100000))




