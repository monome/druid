import sys
import crowlib

def myprint(st):
    print(st)

def main():
    try:
        crow = crowlib.connect()
    except ValueError as err:
        print(err)
        exit()

    # run script passed from command line
    if len(sys.argv) == 2:
        crowlib.upload( crow.write, myprint, sys.argv[1] )
        print(crow.read(1000000).decode())
        print(' file uploaded:')
        crow.write(bytes('^^p', 'utf-8'))
        print(crow.read(1000000).decode())
    else:
        print('usage: python3 upload.py file-to-upload.lua')

    crow.close()
    exit()

main()
