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
