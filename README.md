# druid

A basic REPL for crow with some utilities

## Setup

Requirements:
- Python 3.5+
  - Windows & OS X: https://www.python.org/downloads/
  - Linux: `sudo apt-get install python3 python3-pip` or equivalent
- `pip` and `setuptools`
- `pyserial` and `prompt_toolkit`

Note: you might need to use `python` and `pip` instead of `python3` and `pip3` depending on your platform. If `python3` is not found, check that you have python >= 3.5 with `python --version`.

Install and run:
```bash
# Ensure setuptools is up to date
pip3 install --upgrade setuptools
# Install druid
pip3 install monome-druid
# Run druid :)
druid
```

## Druid

Start by running `druid`

- type q (enter) to quit.
- type h (enter) for a list of special commands.

- input values are printed on the top line
- will reconnect to crow after a disconnect / restart
- scrollable console history

Example:

```
druid
//// druid. q to quit. h for help

> x=6

> print(x)
6

> output[1].volts = 0

> q
```

Execute a lua script and enter the REPL from the command line:
```
druid examples/test-2.lua
```

Diagnostic logs are written to `druid.log`.

## Upload

```
python3 upload.py examples/test-2.lua
```

Uploads the provided lua file to crow & stores it in flash to be executed on boot.

## Download

```
python3 download.py
```

Prints to screen.
Copy to file by running:

```
python3 download.py > feathers.lua
```

## Examples

Druid comes with a bunch of example scripts to help introduce crow's syntax, and spur your imagination with some zany ideas. Here's the list with a brief description of each (most scripts have a longer description including the assignment of ins and outs at the top of the script):

- `boids.lua`: four simulated birds that fly around your input
- `booleanlogic.lua`: logic gates determined by two input gates
- `clockdiv.lua`: four configurable clock divisions of the input clock
- `cvdelay.lua`: a control voltage delay with four taps & looping option
- `gingerbread.lua`: clocked chaos generators
- `samplehold.lua`: sample and hold with quantization & randomness
- `seqswitch.lua`: route an input to 1 of 4 outputs with optional 'hold'
- `shiftregister.lua`: output the last 4 captured voltages & play just friends
- `stop.lua`: reset crow
