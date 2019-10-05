# druid

a basic repl for crow with some utilities

## setup

- requires python 3.5+
  - windows & osx: https://www.python.org/downloads/
  - linux: `sudo apt-get install python3 python3-pip`
- requires pyserial, asyncio, and prompt_toolkit. install & run with:
```bash
sh setup.sh
source Scripts/activate  # need to do this each time you run a new shell
python druid.py
```

## linux additional setup

without

## druid

```
python3 druid.py
```

- type q (enter) to quit.
- type h (enter) for a list of special commands.

- input values are printed on the top line
- will reconnect to crow after a disconnect / restart
- scrollable console history

example:

```
t@nav: ~/druid $ python3 druid.py
//// druid. q to quit. h for help

> x=6

> print(x)
6

> output[1].volts = 0

> q
```

execute a lua script and enter the REPL from the command line:
```
python3 druid.py examples/test-2.lua
```

diagnostic logs are written to druid.log

## upload

```
python3 upload.py examples/test-2.lua
```

uploads the provided lua file to crow & stores it in flash to be executed on boot.

## download

```
python3 download.py
```

prints to screen. copy to file by:

```
python3 download.py > feathers.lua
```
