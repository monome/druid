#!/usr/bin/env python3

from druid import crowlib


def main():
    try:
        crow = crowlib.connect()
    except ValueError as err:
        print(err)
        exit()

    crow.write(bytes('^^p', 'utf-8'))
    print(crow.read(1000000).decode())

    crow.close()
    exit()

main()
