# druid

a basic repl for crow with some utilities

## setup

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

## examples

druid comes with a bunch of example scripts to help introduce crow's syntax, and spur your imagination with some zany ideas. Here's the list with a brief description of each (most scripts have a longer description including the assignment of ins and outs at the top of the script):

- `boids.lua`: four simulated birds that fly around your input
- `booleanlogic.lua`: logic gates determined by two input gates
- `clockdiv.lua`: four configurable clock divisions of the input clock
- `cvdelay.lua`: a control voltage delay with four taps & looping option
- `gingerbread.lua`: clocked chaos generators
- `samplehold.lua`: sample and hold with quantization & randomness
- `seqswitch.lua`: route an input to 1 of 4 outputs with optional 'hold'
- `shiftregister.lua`: output the last 4 captured voltages & play just friends
- `stop.lua`: reset crow
