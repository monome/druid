# druid

a super-basic terminal and some utilities for crow

## setup

- tested on linux & mac osx (attaches to first found crow port)
- requires python 2.7+
- requires pyserial. install using `pip install pyserial`
- optionally uses readline. install using `pip install readline` (mac / linux only)

## druid (REPL)

```
python druid.py
```

- type q (enter) to quit.
- crow response is printed after each command entered.
- readline enabled (up arrow)
- type r to send & run the lua script in `sketch.lua` immediately
- type u to upload the script in `sketch.lua` to crow's internal flash memory
- type p to print the script currently in crow's internal flash memory

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

## download

```
python download.py
```

prints to screen. copy to file by:

```
python download.py > feathers.lua
```


---

## c version

check out the `c` subfolder

## setup

run `make`

then run `./druid`

`q` to quit

## port

default connects to

```
/dev/ttyAMA0
```

specify an arg for different port ie

```
./druid /dev/ttyAMA1
```

## BROKEN

- DOESN'T WORK ON MACOS. serial port open just hangs.
- sloppy use of `getch()` means chars aren't reported until CR, so there are double-prints etc
- crow prints will interrupt command typing
- no readline niceties (up-arrow)

## TODO

- hack into old command-line maiden, use readline and ncurses etc





