# druid

a basic repl for crow with some utilities

## setup (python3 version)

- tested on linux & mac osx (attaches to first found crow port)
- requires python 3.5+
  - windows & osx: https://www.python.org/downloads/
  - linux: `sudo apt-get install python3 python3-pip`
- requires pyserial, asyncio, and prompt_toolkit. install with:
```
pip3 install pyserial asyncio prompt_toolkit
```
## linux additional setup

without 

## druid

```
python3 druid.py
```

- type q (enter) to quit.
- type h (enter) for a list of commands.

- default input vals are printed on the top line
- messages from crow are printed instantly (asynchronously)
- will reconnect to crow after a disconnect / restart
- scrollable console history

## druid-old (REPL)

deprecated version requires python2.7+

```
python druid-old.py
```

- type q (enter) to quit.
- crow response is printed after each command entered.
- readline enabled (up arrow history)
- type r to send & run the lua script in `sketch.lua` immediately.
- type u to upload the script in `sketch.lua` to crow's internal flash memory.
- type p to print the script currently in crow's internal flash memory.

example:

```
10.0.0.132 ~/druid $ python druid.py
//// druid. q to quit.

> x=6

> print(x)
6

> output[1].volts = 0

> q
```

## upload

```
python upload.py examples/test-2.lua
```

uploads the provided lua file to crow & stores it in flash to be executed on boot.

## download

```
python download.py
```

prints to screen. copy to file by:

```
python download.py > feathers.lua
```
